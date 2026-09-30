import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
from time import perf_counter


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from library_codex.benchmarks.library_checker import atomic_write, json_bytes
from library_codex.benchmarks.lc_problems import standalone
from library_codex.benchmarks.lc_problems._composition import composition_case


FUNCTIONS = (
    "_compose_ntt", "_descend_q", "_build_frequency_q", "_ascend_p",
    "_butterfly", "_butterfly_inv", "_ntt_plan", "taylor_shift", "multiply", "array",
)


def instrument(module):
    rows = {}
    stack = []

    def wrap(name, function):
        def measured(*args, **kwargs):
            row = rows.setdefault(name, dict(calls=0, inclusiveSeconds=0.0, exclusiveSeconds=0.0, lengths=Counter()))
            row["calls"] += 1
            if name in {"_butterfly", "_butterfly_inv"}:
                row["lengths"][len(args[0])] += 1
            frame = [0.0]
            stack.append(frame)
            start = perf_counter()
            try:
                return function(*args, **kwargs)
            finally:
                elapsed = perf_counter() - start
                stack.pop()
                row["inclusiveSeconds"] += elapsed
                row["exclusiveSeconds"] += elapsed - frame[0]
                if stack:
                    stack[-1][0] += elapsed
        return measured

    originals = {name: getattr(module, name) for name in FUNCTIONS}
    for name, function in originals.items():
        setattr(module, name, wrap(name, function))
    return rows, originals


def run_child(size, mode, seed):
    module = importlib.import_module("library_codex.fps998.Composition")
    data, expected = composition_case(size, "dense", seed)
    lines = data.splitlines()
    outer = list(map(int, lines[1].split()))
    inner = list(map(int, lines[2].split()))
    rows, originals = instrument(module) if mode == "instrumented" else ({}, {})
    start = perf_counter()
    try:
        result = module.fps_compose(outer, inner, size)
    finally:
        elapsed = perf_counter() - start
        for name, function in originals.items():
            setattr(module, name, function)
    tokens = [str(value).encode() for value in result]
    if expected is not None and tokens != expected:
        raise ValueError("independent oracle mismatch")
    return dict(mode=mode, seconds=elapsed, functions=rows,
                inputSha256=hashlib.sha256(data).hexdigest(),
                outputSha256=hashlib.sha256(b"\n".join(tokens)).hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=131072)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--seed", type=int, default=92471)
    parser.add_argument("--child", choices=("plain", "instrumented"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.size <= 131072 or args.repeat < 1:
        parser.error("invalid size or repeat")
    if args.child:
        print(json.dumps(run_child(args.size, args.child, args.seed)))
        return
    if args.output is None:
        parser.error("--output is required")
    samples = []
    for iteration in range(args.repeat):
        modes = ("plain", "instrumented") if iteration % 2 == 0 else ("instrumented", "plain")
        for mode in modes:
            command = [sys.executable, str(Path(__file__).resolve()), "--child", mode,
                       "--size", str(args.size), "--seed", str(args.seed)]
            sample = json.loads(subprocess.check_output(command, timeout=120))
            samples.append(sample)
            print(mode, round(sample["seconds"], 4), flush=True)
    if len({sample["outputSha256"] for sample in samples}) != 1:
        raise ValueError("instrumentation changed the result")
    profile = [sample for sample in samples if sample["mode"] == "instrumented"]
    medians = {mode: statistics.median(sample["seconds"] for sample in samples if sample["mode"] == mode)
               for mode in ("plain", "instrumented")}
    representative = min(profile, key=lambda sample: abs(sample["seconds"] - medians["instrumented"]))
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(), size=args.size,
                  seed=args.seed, repeat=args.repeat, runtime=sys.version,
                  sourceSha256=hashlib.sha256(standalone("composition_of_formal_power_series_large")).hexdigest(),
                  timing="fresh process; function only; coarse wrappers, not cProfile; inclusive times overlap",
                  medians=medians, representative=representative, samples=samples)
    atomic_write(args.output, json_bytes(report))
    print(json.dumps(dict(medians=medians, functions=representative["functions"]), indent=2))


if __name__ == "__main__":
    main()
