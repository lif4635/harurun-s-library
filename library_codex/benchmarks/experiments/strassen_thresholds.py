import argparse
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from library_codex.benchmarks.official_comparison import compare
from library_codex.tools.check_library_checker import solution


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--reviewed", type=int, nargs="+", required=True)
    parser.add_argument("--problem", type=Path, required=True)
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--thresholds", type=int, nargs="+", default=[32, 64, 128, 256, 512, 1024])
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, _ = solution("matrix_product")
    with tempfile.TemporaryDirectory(prefix="harurun-strassen-") as directory:
        variants = []
        for threshold in args.thresholds:
            if threshold < 1:
                parser.error("threshold must be positive")
            path = Path(directory) / (str(threshold) + ".py")
            original = "strassen_matrix_multiply(first, second)"
            replaced = f"strassen_matrix_multiply(first, second, threshold={threshold})"
            if source.count(original) != 1:
                raise ValueError("matrix product driver changed")
            path.write_text(source.replace(original, replaced), encoding="utf-8")
            variants.append(f"threshold{threshold}={path}")
        compare(SimpleNamespace(snapshot=args.snapshot, reviewed=args.reviewed,
                                problem=args.problem, cases=args.cases, variant=variants,
                                python=sys.executable, repeat=args.repeat, seed=20261005,
                                timeout=90, output=args.output))


if __name__ == "__main__":
    main()
