"""Run the repeatable correctness and performance checks for library_codex."""

import argparse
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
TOOLS = ROOT / "tools"

QUICK_TESTS = (
    ROOT / "verify" / "combinatorics" / "test_langford.py",
    ROOT / "verify" / "combinatorics" / "test_skolem.py",
    ROOT / "verify" / "test_changed_checks.py",
    ROOT / "verify" / "test_contribution_guide.py",
    ROOT / "verify" / "test_api_reference.py",
    ROOT / "verify" / "test_library_catalog.py",
    ROOT / "verify" / "test_module_boundaries.py",
    ROOT / "verify" / "data_structure" / "test_debug_output.py",
    ROOT / "verify" / "data_structure" / "test_dynamic_wavelet_matrix.py",
    ROOT / "verify" / "data_structure" / "test_int_range_tree.py",
    ROOT / "verify" / "graph_flow" / "test_advanced_flow.py",
    ROOT / "verify" / "graph_flow" / "test_push_relabel.py",
    ROOT / "verify" / "graph" / "test_csr_graph.py",
)


def run_step(label, command):
    print(f"\n== {label} ==", flush=True)
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=REPOSITORY)
    elapsed = time.perf_counter() - started
    if completed.returncode:
        print(f"FAILED: {label} ({elapsed:.2f}s)", file=sys.stderr)
        raise SystemExit(completed.returncode)
    print(f"passed: {label} ({elapsed:.2f}s)", flush=True)
    return elapsed


def commands(profile, skip_tests, skip_benchmarks):
    executable = sys.executable
    result = [
        (
            "byte-compile",
            [executable, "-m", "compileall", "-q", str(ROOT)],
        ),
        (
            "API reference synchronization",
            [executable, str(TOOLS / "build_api_reference.py"), "--check"],
        ),
        (
            "library catalog synchronization",
            [executable, str(TOOLS / "build_library_catalog.py"), "--check"],
        ),
        (
            "API description quality",
            [
                executable,
                str(TOOLS / "build_library_catalog.py"),
                "--audit-descriptions",
            ],
        ),
        (
            "recursion audit",
            [executable, str(TOOLS / "audit_recursion.py")],
        ),
    ]
    if not skip_tests:
        targets = [str(ROOT / "verify")] if profile == "full" else [
            str(path) for path in QUICK_TESTS
        ]
        result.append(
            (
                f"{profile} tests",
                [executable, "-m", "pytest", "-q", *targets],
            )
        )
    if not skip_benchmarks:
        result.append(
            (
                f"{profile} performance regression",
                [
                    executable,
                    str(TOOLS / "run_benchmarks.py"),
                    "--profile",
                    profile,
                ],
            )
        )
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Check library_codex without changing tracked source files."
    )
    parser.add_argument(
        "--profile",
        choices=("quick", "full"),
        default="quick",
        help="quick checks changed/high-risk areas; full checks the complete suite",
    )
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--skip-benchmarks", action="store_true")
    args = parser.parse_args()

    started = time.perf_counter()
    timings = []
    for label, command in commands(
        args.profile, args.skip_tests, args.skip_benchmarks
    ):
        timings.append((label, run_step(label, command)))

    total = time.perf_counter() - started
    print("\n== summary ==")
    for label, elapsed in timings:
        print(f"{label}: {elapsed:.2f}s")
    print(f"all {args.profile} checks passed in {total:.2f}s")


if __name__ == "__main__":
    main()
