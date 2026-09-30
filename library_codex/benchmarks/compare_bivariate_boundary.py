import argparse
import hashlib
import importlib
import json
from pathlib import Path
import statistics
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from library_codex.benchmarks.compare_bivariate_methods import coefficients, run_python
from library_codex.benchmarks.library_checker import atomic_write, json_bytes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", choices=("current", "colored"))
    parser.add_argument("--no-boundary", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--shapes", nargs="+", default=["256x256", "127x521"])
    parser.add_argument("--repeat", type=int, default=3)
    args = parser.parse_args()
    if args.child:
        if args.no_boundary:
            module = importlib.import_module("library_codex.convolution.MultivariateMultiplication")
            ntt = importlib.import_module("library_codex.convolution.NTT998")
            module._multiply998 = ntt._multiply_without_boundary
        args.warmups = 0
        run_python(args)
        return
    if args.output is None or args.repeat < 1:
        parser.error("--output and positive --repeat required")
    modes = [("current", False), ("current", True), ("colored", False), ("colored", True)]
    cases = []
    for shape in args.shapes:
        width, height = map(int, shape.split("x"))
        for operation in ("inverse", "exponential"):
            values = coefficients(width, height, operation, "dense", 0, 92471)
            payload = f"{width} {height} {operation} 1234567\n" + " ".join(map(str, values)) + "\n"
            samples = {}
            for iteration in range(args.repeat):
                order = modes[iteration % len(modes):] + modes[:iteration % len(modes)]
                for mode, disabled in order:
                    name = mode + ("-no-boundary" if disabled else "")
                    command = [sys.executable, str(Path(__file__).resolve()), "--child", mode]
                    if disabled:
                        command.append("--no-boundary")
                    completed = subprocess.run(command, input=payload.encode(), capture_output=True,
                                               timeout=45, check=True)
                    samples.setdefault(name, []).append(json.loads(completed.stdout))
                    if len({s["outputSha256"] for rows in samples.values() for s in rows}) != 1:
                        raise ValueError("output mismatch")
            medians = {name: statistics.median(s["seconds"] for s in rows) for name, rows in samples.items()}
            cases.append(dict(shape=[width, height], operation=operation, samples=samples,
                              medianSeconds=medians, inputSha256=hashlib.sha256(payload.encode()).hexdigest()))
            files = [Path(__file__), ROOT / "library_codex/benchmarks/compare_bivariate_methods.py",
                     ROOT / "library_codex/benchmarks/bivariate_candidates.py",
                     ROOT / "library_codex/convolution/NTT998.py",
                     ROOT / "library_codex/convolution/MultivariateMultiplication.py",
                     ROOT / "library_codex/fps/MultivariateFPS.py", ROOT / "library_codex/fps998/FPS.py"]
            atomic_write(args.output, json_bytes(dict(cases=cases, repeat=args.repeat, warmups=0, seed=92471,
                         timing="function only; fresh sequential PyPy processes",
                         memoryMetric="/proc/self/status VmHWM after calculation",
                         sourceSha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files})))
            print(shape, operation, medians, flush=True)


if __name__ == "__main__":
    main()
