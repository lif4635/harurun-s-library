import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", choices=("before", "current"))
    parser.add_argument("--number", type=int)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--values", type=int, nargs="+", default=[10**10, 10**12, 10**14])
    parser.add_argument("--output", type=Path, default=ROOT / "library_codex/benchmarks/results/square_free_comparison.json")
    args = parser.parse_args()
    if args.worker:
        if args.worker == "before":
            from library_codex.benchmarks.baselines.count_square_free_before import count_square_free
        else:
            from library_codex.prime.Sieve import count_square_free
        print(count_square_free(args.number))
        return
    from library_codex.benchmarks.official_comparison import measure
    from library_codex.tools.check_library_checker import save_json

    if args.repeat < 1 or any(value < 1 or value > 10**14 for value in args.values):
        parser.error("require repeat >= 1 and 1 <= values <= 10^14 for the old implementation")
    paths = {
        "before": ROOT / "library_codex/benchmarks/baselines/count_square_free_before.py",
        "current": ROOT / "library_codex/prime/Sieve.py",
    }
    cpu = Path("/proc/cpuinfo").read_text()
    cpu = next(line.split(":", 1)[1].strip() for line in cpu.splitlines() if line.startswith("model name"))
    report = {
        "measuredAt": datetime.now(timezone.utc).isoformat(),
        "runtime": subprocess.check_output([sys.executable, "--version"], text=True).strip(),
        "platform": platform.platform(), "cpu": cpu, "repeat": args.repeat,
        "sourceSha256": {name: hashlib.sha256(path.read_text().encode()).hexdigest() for name, path in paths.items()},
        "harnessSha256": hashlib.sha256(Path(__file__).read_text().encode()).hexdigest(),
        "baselineRevision": "57d2a224ce91bd44d1c1aeb4bfed216a07eb187e",
        "protocol": "fresh sequential PyPy processes, shuffled order, startup/JIT/imports included, GNU time RSS, equality with original sieve, no memory limit",
        "results": [],
    }
    with tempfile.TemporaryDirectory(prefix="harurun-squarefree-") as directory:
        temporary = Path(directory)
        stdin = temporary / "input"
        stdin.write_text("")
        for number in args.values:
            samples = {name: [] for name in paths}
            expected = None
            for iteration in range(args.repeat):
                order = list(paths)
                random.Random(72941 + iteration).shuffle(order)
                for name in order:
                    output = temporary / "output"
                    command = [sys.executable, str(Path(__file__).resolve()), "--worker", name, "--number", str(number)]
                    elapsed, rss = measure(command, stdin, output, temporary / "rss", 60)
                    result = int(output.read_text())
                    if expected is None:
                        expected = result
                    if result != expected:
                        raise AssertionError((number, name, result, expected))
                    samples[name].append({"seconds": elapsed, "peakRssKiB": rss, "outputSha256": hashlib.sha256(output.read_bytes()).hexdigest()})
            row = {"number": number, "result": expected, "implementations": {}}
            for name, values in samples.items():
                row["implementations"][name] = {
                    "samples": values,
                    "medianSeconds": statistics.median(value["seconds"] for value in values),
                    "peakRssKiB": max(value["peakRssKiB"] for value in values),
                }
            report["results"].append(row)
            print(json.dumps(row), flush=True)
    save_json(args.output, report)


if __name__ == "__main__":
    main()
