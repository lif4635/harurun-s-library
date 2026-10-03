import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT.parent))

from build_codon import SUPPORTED, atomic_write, generate
from build_library_catalog import build_standalone_code
from library_codex.benchmarks.codon_cases import CASES


def compare(module, size, repeat, pypy, codon):
    if size < 2 or repeat < 1:
        raise ValueError("size >= 2 and repeat >= 1 required")
    original, _ = build_standalone_code(ROOT / (module + ".py"), ROOT)
    native = generate(module)
    solver = CASES[module]
    versions = {
        "codon": subprocess.check_output([codon, "--version"], text=True).strip(),
        "pypy": subprocess.check_output([pypy, "--version"], text=True).strip(),
    }
    if versions["codon"] != "0.19.3":
        raise ValueError("AtCoder validation requires Codon 0.19.3")
    source = {"pypy": "import sys\n" + original + "\n" + solver, "codon": native + "\n" + solver}
    samples = {"pypy": [], "codon": []}
    expected = None
    with tempfile.TemporaryDirectory(prefix="library-codon-") as temporary:
        folder = Path(temporary)
        for name, code in source.items():
            (folder / (name + ".py")).write_text(code, encoding="utf-8")
        executable = folder / "a.out"
        command = [codon, "build", "--release", "-o", str(executable), str(folder / "codon.py")]
        start = perf_counter()
        build = subprocess.run(command, capture_output=True, text=True, timeout=120)
        compile_seconds = perf_counter() - start
        if build.returncode:
            raise RuntimeError(build.stdout + build.stderr)
        commands = {"pypy": [pypy, str(folder / "pypy.py")], "codon": [str(executable)]}
        for iteration in range(repeat + 1):
            for name in (commands if iteration % 2 == 0 else reversed(commands)):
                start = perf_counter()
                result = subprocess.run(commands[name], input=f"{size}\n", capture_output=True, text=True, timeout=120)
                elapsed = perf_counter() - start
                if result.returncode:
                    raise RuntimeError(name + ": " + result.stdout + result.stderr)
                if expected is None:
                    expected = result.stdout
                if result.stdout != expected:
                    raise AssertionError(module + " outputs disagree: " + name + "\n" + result.stdout + "\nexpected\n" + expected)
                if iteration:
                    samples[name].append(elapsed)
    return {
        "module": module, "size": size, "versions": versions,
        "platform": platform.platform(), "compileSeconds": compile_seconds,
        "timing": "fresh sequential processes; one discarded process per runtime; compilation excluded; startup and IO included",
        "samplesSeconds": samples,
        "medianSeconds": {name: statistics.median(values) for name, values in samples.items()},
        "sourceSha256": {name: hashlib.sha256(code.encode()).hexdigest() for name, code in source.items()},
        "outputSha256": hashlib.sha256(expected.encode()).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("modules", nargs="*")
    parser.add_argument("--size", type=int, default=1024)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--pypy", default="pypy3")
    parser.add_argument("--codon", default="codon")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if any(module not in SUPPORTED for module in args.modules):
        parser.error("unknown module")
    for executable in (args.pypy, args.codon):
        if not shutil.which(executable):
            parser.error("executable not found: " + executable)
    rows = []
    for module in args.modules or SUPPORTED:
        result = compare(module, args.size, args.repeat, args.pypy, args.codon)
        rows.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    if args.output:
        atomic_write(args.output, json.dumps(rows, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
