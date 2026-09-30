import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from library_codex.benchmarks.library_checker import compare, fetch
from library_codex.benchmarks.lc_problems import PROBLEMS, problem_module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("fetch", "small", "large", "stress"))
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--reviewed", type=int, nargs="+", default=[])
    parser.add_argument("--size", type=int)
    parser.add_argument("--problems", nargs="+", choices=PROBLEMS, default=PROBLEMS)
    args = parser.parse_args()
    failures = []
    for problem in args.problems:
        try:
            if args.phase == "fetch":
                with redirect_stdout(io.StringIO()):
                    fetch(SimpleNamespace(problem=problem, language="pypy3", top=1, cache=args.cache))
                print(problem + ": fetched", flush=True)
                continue
            if args.output is None:
                parser.error("--output is required for checks")
            snapshot = args.cache / (problem + "-pypy3.json")
            rows = json.loads(snapshot.read_text())["submissions"]
            ids = [row["id"] for row in rows]
            if not ids or not set(ids) <= set(args.reviewed):
                raise ValueError("source review required: " + str(ids))
            fps = problem == "convolution_mod" or "formal_power_series" in problem
            default_size = 80 if args.phase == "small" else (65536 if fps else 100000) if args.phase == "large" else (262145 if fps else 500000)
            size = args.size if args.size is not None else min(default_size, getattr(problem_module(problem), "MAX_SIZE", 500000))
            if size < 2:
                raise ValueError("size must be at least 2")
            suffix = "-" + str(size) if args.size else ""
            output = args.output / (problem + "-" + args.phase + suffix + ".json")
            with redirect_stdout(io.StringIO()):
                compare(SimpleNamespace(snapshot=snapshot, reviewed=ids, python=sys.executable,
                    size=size, families=None, seed=92471, repeat=1 if args.phase == "small" else 3,
                    timeout=90, output=output))
            results = json.loads(output.read_text())["results"]
            for row in results:
                times = {name: round(value["medianSeconds"], 4) for name, value in row["implementations"].items()}
                print(problem, row["family"], size, times, flush=True)
        except Exception as error:
            failures.append(problem)
            print(problem + ": FAILED: " + repr(error), flush=True)
    if failures:
        raise SystemExit("failed problems: " + ", ".join(failures))


if __name__ == "__main__":
    main()
