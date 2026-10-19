import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import statistics
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", choices=("default", "wide", "mo"))
    parser.add_argument("--official", type=Path)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--cases", nargs="+", default=["max_00", "small_a_00"])
    parser.add_argument("--output", type=Path, default=ROOT / "library_codex/benchmarks/results/range_inversions_comparison.json")
    args = parser.parse_args()
    if args.worker:
        from math import isqrt
        read = sys.stdin.buffer.readline
        n, q = map(int, read().split())
        values = list(map(int, read().split()))
        queries = [tuple(map(int, read().split())) for _ in range(q)]
        if args.worker == "mo":
            from library_codex.range_query.OfflineRangeInversions import range_inversions
            answers = range_inversions(values, queries)
        else:
            from library_codex.range_query.StaticRangeInversions import StaticRangeInversions
            width = 2 * (isqrt(n) + 1) if args.worker == "wide" else None
            table = StaticRangeInversions(values, width)
            answers = [table.query(l, r) for l, r in queries]
        print("\n".join(map(str, answers)))
        return
    from library_codex.benchmarks.official_comparison import measure
    from library_codex.benchmarks.official_benchmark import runtime_info
    from library_codex.tools.check_library_checker import file_digest, save_json

    if args.official is None or args.repeat < 1:
        parser.error("require --official and repeat >= 1")
    problem = args.official / "data_structure/static_range_inversions_query"
    hashes = json.loads((problem / "hash.json").read_text())
    cases = args.cases
    for case in cases:
        if Path(case).name != case:
            parser.error("invalid case name")
        for directory, suffix in (("in", ".in"), ("out", ".out")):
            path = problem / directory / (case + suffix)
            if file_digest(path) != hashes.get(path.name):
                raise ValueError("official case hash mismatch: " + str(path))
    sources = {
        "squareRoot": ROOT / "library_codex/range_query/StaticRangeInversions.py",
        "mo": ROOT / "library_codex/range_query/OfflineRangeInversions.py",
    }
    report = {
        "measuredAt": datetime.now(timezone.utc).isoformat(),
        "environment": runtime_info(sys.executable),
        "repeat": args.repeat,
        "sourceSha256": {name: hashlib.sha256(path.read_text().encode()).hexdigest() for name, path in sources.items()},
        "harnessSha256": hashlib.sha256(Path(__file__).read_text().encode()).hexdigest(),
        "checkerSha256": file_digest(problem / "checker"),
        "upstreamRevision": subprocess.check_output(["git", "-C", str(args.official), "rev-parse", "HEAD"], text=True).strip(),
        "protocol": "sequential fresh PyPy processes, shuffled variants, startup/JIT/I/O included, official checker each run, GNU time RSS, no memory limit",
        "variants": {"default": "block width isqrt(N)+1", "wide": "block width 2*(isqrt(N)+1)", "mo": "offline Mo ordering with a Fenwick tree"},
        "results": [],
    }
    with tempfile.TemporaryDirectory(prefix="harurun-inversions-") as directory:
        temporary = Path(directory)
        for case in cases:
            samples = {name: [] for name in report["variants"]}
            stdin = problem / "in" / (case + ".in")
            expected = problem / "out" / (case + ".out")
            for iteration in range(args.repeat):
                order = list(samples)
                random.Random(19384 + iteration).shuffle(order)
                for name in order:
                    output = temporary / "output"
                    command = [sys.executable, str(Path(__file__).resolve()), "--worker", name]
                    elapsed, rss = measure(command, stdin, output, temporary / "rss", 60)
                    checked = subprocess.run([str(problem / "checker"), str(stdin), str(output), str(expected)], capture_output=True, timeout=30)
                    if checked.returncode:
                        raise ValueError(checked.stderr.decode(errors="replace"))
                    samples[name].append({"seconds": elapsed, "peakRssKiB": rss, "outputSha256": file_digest(output)})
            row = {"case": case, "inputSha256": file_digest(stdin), "expectedSha256": file_digest(expected), "implementations": {}}
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
