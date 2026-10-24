import argparse
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
from types import SimpleNamespace

from library_codex.benchmarks.official_comparison import compare
from library_codex.tools.check_library_checker import file_digest, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--problem", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cpu", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--cases", nargs="+", default=["fft_killer_04", "max_random_00"])
    parser.add_argument("--modes", nargs="+", default=["baseline", "fused_both"])
    parser.add_argument("--current", action="store_true")
    parser.add_argument("--variants-dir", type=Path, default=Path(".cache/large-locality-variants"))
    parser.add_argument("--variant", action="append", default=[])
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("repeat must be positive")
    if not hasattr(os, "sched_setaffinity"):
        raise SystemExit("Run this measurement controller with Linux CPython; --python selects the tested PyPy")
    os.sched_setaffinity(0, {args.cpu})
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    for name in list(os.environ):
        if name.startswith(("PYPY", "PYTHON")):
            del os.environ[name]
    runtime = Path(args.python).resolve()
    environment = dict(platform=platform.platform(), libc=platform.libc_ver(),
                       affinity=sorted(os.sched_getaffinity(0)), stackLimit="unlimited",
                       lscpu=subprocess.check_output(["lscpu"], text=True),
                       runtimePath=str(runtime), runtimeSha256=file_digest(runtime),
                       memoryLimitEnforced=False,
                       notes="Same-host comparison; host load is not isolated; judge Docker and CPU are not reproduced")
    arguments = SimpleNamespace(
        snapshot=Path("library_codex/benchmarks/baselines/large_convolution_snapshot.json"),
        reviewed=[], problem=args.problem, cases=args.cases,
        variant=[mode + "=" + str(args.variants_dir / (mode + ".py")) for mode in args.modes],
        python=str(runtime), repeat=args.repeat, seed=92471, timeout=120, output=args.output,
    )
    if args.current:
        arguments.variant.append("current=verify/library_checker/solutions/convolution_mod_large.py")
    arguments.variant.extend(args.variant)
    save_json(args.output.with_suffix(".environment.json"), environment)
    compare(arguments)
    report = json.loads(args.output.read_text())
    report["environment"] = environment
    save_json(args.output, report)


if __name__ == "__main__":
    main()
