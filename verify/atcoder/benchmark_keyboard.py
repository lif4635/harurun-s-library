import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
from time import perf_counter

from library_codex.benchmarks.seg_tree_traversal import inputs
from verify.atcoder.abc434_g import Keyboard


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=8000000)
    parser.add_argument("--q", type=int, default=200000)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--case", choices=["mixed", "digits", "cancellation"], default="cancellation")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--cpu", type=int, default=2)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    standalone = Path(__file__).with_name("abc434_g_standalone.py")
    if hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, {args.cpu})
    baseline = root / "library_codex/benchmarks/experiments/keyboard_functions.py"
    programs = [("class", standalone)]
    if args.compare:
        programs.insert(0, ("functions", baseline))
    text, operations = inputs(args.n, args.q, args.case)
    tree = Keyboard(text)
    expected = []
    lines = [(str(args.n) + " " + str(args.q)).encode(), text]
    for kind, a, b in operations:
        if kind == 1:
            tree.set(a, b)
            lines.append(("1 " + str(a + 1) + " " + chr(b)).encode())
        else:
            _, length, value = tree.prod(a, b)
            expected.append(str(value if length else -1))
            lines.append(("2 " + str(a + 1) + " " + str(b)).encode())
    payload = b"\n".join(lines) + b"\n"
    answer = ("\n".join(expected) + "\n").encode()
    del tree, lines, expected, operations, text
    gc.collect()
    records = []
    for repeat in range(args.repeat):
        for variant, program in (programs if repeat % 2 == 0 else programs[::-1]):
            started = perf_counter()
            run = subprocess.run(["/usr/bin/time", "-f", "%M", sys.executable, "-I", str(program)], input=payload, capture_output=True, timeout=60, check=True)
            seconds = perf_counter() - started
            assert run.stdout == answer
            row = {"variant": variant, "repeat": repeat, "seconds": seconds, "peakRssKiB": int(run.stderr.strip()), "outputSha256": hashlib.sha256(run.stdout).hexdigest()}
            records.append(row)
            print(json.dumps(row), flush=True)
    sources = [standalone, Path(__file__), root / "verify/atcoder/abc434_g.py", root / "library_codex/segment_tree/SegTreeTraversal.py"]
    if args.compare:
        sources.append(baseline)
    report = {
        "n": args.n, "q": args.q, "case": args.case,
        "python": sys.version, "platform": platform.platform(),
        "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "timing": "fresh isolated standalone process; includes startup, JIT, stdin/stdout, excludes fixture generation; no warmup",
        "validation": "all stdout compared with imported implementation; independent naive oracle covered by unit tests, not this maximum-size fixture; not official judge data or online AC",
        "inputSha256": hashlib.sha256(payload).hexdigest(),
        "sourceHashes": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "records": records,
        "medians": [{"variant": variant, **{key: statistics.median(row[key] for row in records if row["variant"] == variant) for key in ("seconds", "peakRssKiB")}} for variant, _ in programs],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
