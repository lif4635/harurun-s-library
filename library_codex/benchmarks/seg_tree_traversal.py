import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import random
import resource
import statistics
import subprocess
import sys
from time import perf_counter

from library_codex.benchmarks.experiments import keyboard_functions as example
from verify.atcoder import abc434_g as current


def stack_fold(size, left, right, prepend, initial):
    if not 0 <= left <= right <= size:
        raise IndexError("invalid half-open range")
    left += size
    right += size
    result = initial
    pending = []
    while left < right:
        if left & 1:
            pending.append(left)
            left += 1
        if right & 1:
            right -= 1
            result = prepend(right, result)
        left >>= 1
        right >>= 1
    for node in reversed(pending):
        result = prepend(node, result)
    return result


class InlineKeyboard(example.Keyboard):
    __slots__ = ()

    def prod(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        left += self.size
        right += self.size
        prepend = self._prepend
        result = (0, 0, 0)
        while left < right:
            height = min((right & -right).bit_length(), (right - left).bit_length()) - 1
            result = prepend((right >> height) - 1, result)
            right -= 1 << height
        return result


def inputs(n, q, case):
    rng = random.Random(434)
    alphabet = b"123456789BBBBBBBBB" if case == "mixed" else b"123456789"
    text = bytes(rng.choice(alphabet) for _ in range(n))
    if case == "cancellation":
        block = b"123456789" * 7 + b"B" * 32
        text = (block * ((n + len(block) - 1) // len(block)))[:n]
    operations = []
    for i in range(q):
        if i % 2:
            a = rng.randrange(n)
            b = rng.randrange(a + 1, n + 1)
            operations.append((2, a, b))
        else:
            operations.append((1, rng.randrange(n), rng.choice(b"123456789BBBBBBBBB")))
    return text, operations


def worker(args):
    if args.variant == "stack":
        example.fold = stack_fold
    if args.variant == "lists":
        example.array = lambda code, values: list(values)
    cls = current.Keyboard if args.variant == "class" else InlineKeyboard if args.variant == "inline" else example.Keyboard
    text, operations = inputs(args.n, args.q, args.case)
    input_hash = hashlib.sha256(text + repr(operations).encode()).hexdigest()
    start = perf_counter()
    tree = cls(text)
    built = perf_counter()
    checksum = 0
    for kind, a, b in operations:
        if kind == 1:
            tree.set(a, b)
        else:
            back, length, value = tree.prod(a, b)
            checksum = (checksum * 1000003 + value + length * 31 + back) % 1000000007
    ended = perf_counter()
    print(json.dumps({
        "variant": args.variant, "case": args.case, "n": args.n, "q": args.q,
        "inputHash": input_hash, "checksum": checksum,
        "buildSeconds": built - start, "operationsSeconds": ended - built,
        "totalSeconds": ended - start,
        "peakRssKiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=200000)
    parser.add_argument("--q", type=int, default=30000)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--cpu", type=int, default=2)
    parser.add_argument("--variant", choices=["shared", "inline", "stack", "lists", "class"])
    parser.add_argument("--case", choices=["mixed", "digits", "cancellation"])
    parser.add_argument("--cases", nargs="+", default=["mixed", "digits", "cancellation"], choices=["mixed", "digits", "cancellation"])
    parser.add_argument("--variants", nargs="+", default=["shared", "class"], choices=["shared", "inline", "stack", "lists", "class"])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.variant:
        worker(args)
        return
    if hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, {args.cpu})
    root = Path(__file__).resolve().parents[2]
    sources = [root / "library_codex/segment_tree/SegTreeTraversal.py", root / "verify/atcoder/abc434_g.py", Path(__file__), Path(example.__file__)]
    records = []
    expected = {}
    for case in args.cases:
        for repeat in range(args.repeat):
            for variant in (args.variants if repeat % 2 == 0 else args.variants[::-1]):
                command = [sys.executable, "-m", "library_codex.benchmarks.seg_tree_traversal", "--variant", variant, "--case", case, "--n", str(args.n), "--q", str(args.q)]
                run = subprocess.run(command, cwd=root, capture_output=True, text=True, check=True, timeout=180)
                record = json.loads(run.stdout)
                pair = record["inputHash"], record["checksum"]
                assert expected.setdefault(case, pair) == pair
                record["repeat"] = repeat
                records.append(record)
                print(case, repeat, variant, round(record["totalSeconds"], 4), flush=True)
    report = {
        "python": sys.version, "platform": platform.platform(),
        "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "cpuInfo": Path("/proc/cpuinfo").read_text().split("model name", 1)[-1].splitlines()[0].strip(),
        "timing": "fresh process; no warmup; build and operations include JIT, exclude input generation and interpreter startup; peak RSS includes input generation",
        "sourceHashes": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "records": records,
        "medians": [{"case": case, "variant": variant, **{
            key: statistics.median(r[key] for r in records if r["case"] == case and r["variant"] == variant)
            for key in ["buildSeconds", "operationsSeconds", "totalSeconds", "peakRssKiB"]
        }} for case in args.cases for variant in args.variants],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
