"""Run the library performance checks and optionally write JSON results."""

import argparse
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
BASELINE = TOOLS / "benchmark_baseline.json"


def execute(script, arguments):
    command = [sys.executable, str(TOOLS / script), *arguments]
    completed = subprocess.run(
        command,
        cwd=ROOT.parent,
        check=True,
        text=True,
        capture_output=True,
    )
    output = completed.stdout.strip()
    print(output)
    total_match = re.search(r"\btotal=([0-9.]+)s", output)
    checksum_match = re.search(r"\bchecksum=([^\s]+)", output)
    return {
        "command": command[1:],
        "output": output,
        "total_seconds": float(total_match.group(1)) if total_match else None,
        "checksum": checksum_match.group(1) if checksum_match else None,
    }


def advanced_flow(profile):
    arguments = (
        ["--vertices", "300", "--density", "0.12", "--repeat", "3"]
        if profile == "full"
        else ["--vertices", "180", "--density", "0.08", "--repeat", "1"]
    )
    result = execute("benchmark_advanced_flow.py", arguments)
    dinic = re.search(r"Dinic:\s+([0-9.]+)s", result["output"])
    push = re.search(r"PushRelabel:\s+([0-9.]+)s", result["output"])
    result["dinic_seconds"] = float(dinic.group(1))
    result["push_relabel_seconds"] = float(push.group(1))
    return result


def csr_cases(profile):
    size = ["--vertices", "100000", "--edges", "500000"] if profile == "full" else [
        "--vertices", "20000", "--edges", "100000"
    ]
    results = {}
    for algorithm in ("dijkstra", "scc", "lowlink"):
        pair = {}
        for backend in ("list", "csr"):
            measurements = [
                execute(
                    "benchmark_csr_graph.py",
                    ["--algorithm", algorithm, "--backend", backend, *size],
                )
                for _ in range(3)
            ]
            checksums = {measurement["checksum"] for measurement in measurements}
            if len(checksums) != 1:
                raise AssertionError(
                    f"unstable CSR checksum: {algorithm}/{backend}"
                )
            seconds = [measurement["total_seconds"] for measurement in measurements]
            median_seconds = statistics.median(seconds)
            representative = min(
                measurements,
                key=lambda measurement: abs(
                    measurement["total_seconds"] - median_seconds
                ),
            )
            pair[backend] = dict(representative)
            pair[backend]["total_seconds"] = median_seconds
            pair[backend]["measurements_seconds"] = seconds
        if pair["list"]["checksum"] != pair["csr"]["checksum"]:
            raise AssertionError(f"CSR checksum mismatch: {algorithm}")
        pair["speedup"] = pair["list"]["total_seconds"] / pair["csr"]["total_seconds"]
        results[algorithm] = pair
    return results


def range_tree_cases(profile):
    size = ["--size", "200000", "--queries", "200000"] if profile == "full" else [
        "--size", "50000", "--queries", "50000"
    ]
    stats = {}
    for backend in ("generic", "beats", "specialized"):
        stats[backend] = execute(
            "benchmark_int_range_tree.py", ["--backend", backend, *size]
        )
    checksums = {result["checksum"] for result in stats.values()}
    if len(checksums) != 1:
        raise AssertionError("range-stats checksum mismatch")
    stats["generic_speedup"] = stats["generic"]["total_seconds"] / stats["specialized"]["total_seconds"]
    stats["beats_speedup"] = stats["beats"]["total_seconds"] / stats["specialized"]["total_seconds"]

    affine = {}
    for backend in ("generic", "specialized"):
        affine[backend] = execute(
            "benchmark_int_range_tree.py",
            ["--workload", "affine", "--backend", backend, *size],
        )
    if affine["generic"]["checksum"] != affine["specialized"]["checksum"]:
        raise AssertionError("range-affine checksum mismatch")
    affine["speedup"] = affine["generic"]["total_seconds"] / affine["specialized"]["total_seconds"]
    return {"stats": stats, "affine": affine}


def fps998_cases(profile):
    arguments = (
        ["--size", "65536", "--composition-size", "16384", "--repeat", "5"]
        if profile == "full"
        else ["--size", "16384", "--composition-size", "4096", "--repeat", "3"]
    )
    results = {}
    for backend in ("generic", "specialized"):
        result = execute(
            "benchmark_fps998.py", ["--backend", backend, *arguments]
        )
        for operation in ("multiply", "inverse", "exp", "composition_inv"):
            matched = re.search(
                rf"\b{operation}=([0-9.]+)s", result["output"]
            )
            result[f"{operation}_seconds"] = float(matched.group(1))
        results[backend] = result
    if results["generic"]["checksum"] != results["specialized"]["checksum"]:
        raise AssertionError("FPS998 checksum mismatch")
    results["speedup"] = (
        results["generic"]["total_seconds"]
        / results["specialized"]["total_seconds"]
    )
    return results


def check_thresholds(results, baseline):
    speedups = {
        "csr_dijkstra": results["csr"]["dijkstra"]["speedup"],
        "csr_scc": results["csr"]["scc"]["speedup"],
        "csr_lowlink": results["csr"]["lowlink"]["speedup"],
        "range_stats_generic": results["range_tree"]["stats"]["generic_speedup"],
        "range_stats_beats": results["range_tree"]["stats"]["beats_speedup"],
        "range_affine": results["range_tree"]["affine"]["speedup"],
        "fps998_total": results["fps998"]["speedup"],
    }
    failures = []
    for name, minimum in baseline["minimum_speedup"].items():
        actual = speedups[name]
        if actual < minimum:
            failures.append(f"{name}: {actual:.3f}x < {minimum:.3f}x")
    return speedups, failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-check", action="store_true")
    args = parser.parse_args()
    baseline_data = json.loads(BASELINE.read_text(encoding="utf-8"))
    results = {
        "profile": args.profile,
        "advanced_flow": advanced_flow(args.profile),
        "csr": csr_cases(args.profile),
        "range_tree": range_tree_cases(args.profile),
        "fps998": fps998_cases(args.profile),
    }
    speedups, failures = check_thresholds(results, baseline_data[args.profile])
    results["speedups"] = speedups
    results["threshold_failures"] = failures
    encoded = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    if failures and not args.no_check:
        for failure in failures:
            print("PERFORMANCE REGRESSION:", failure, file=sys.stderr)
        raise SystemExit(1)
    print("performance checks passed")


if __name__ == "__main__":
    main()
