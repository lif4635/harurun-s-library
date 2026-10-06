import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import signal
import statistics
import subprocess
import sys
import tempfile
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.benchmarks.library_checker import verify_source
from library_codex.tools.check_library_checker import file_digest, save_json


def measure(command, input_path, output_path, rss_path, timeout):
    started = perf_counter()
    with input_path.open("rb") as stdin, output_path.open("wb") as stdout:
        process = subprocess.Popen(["/usr/bin/time", "-f", "%M", "-o", str(rss_path), *command],
                                   stdin=stdin, stdout=stdout, stderr=subprocess.PIPE,
                                   start_new_session=True)
        try:
            _, error = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
            raise
    elapsed = perf_counter() - started
    if process.returncode:
        raise RuntimeError(error.decode(errors="replace"))
    return elapsed, int(rss_path.read_text().strip())


def compare(args):
    snapshot = json.loads(args.snapshot.read_text())
    selected = [row for row in snapshot["submissions"] if row["id"] in args.reviewed]
    if {row["id"] for row in selected} != set(args.reviewed):
        raise ValueError("reviewed submission missing from snapshot")
    if snapshot["language"] not in ("pypy3", "python3"):
        raise ValueError("Python source snapshot required")
    if args.problem.name != snapshot["problem"]:
        raise ValueError("problem and snapshot mismatch")
    sources = {str(row["id"]): verify_source(args.snapshot.parent, row) for row in selected}
    for entry in args.variant:
        name, path = entry.split("=", 1)
        if not name or name in sources:
            raise ValueError("duplicate or empty variant name")
        sources[name] = Path(path).resolve()
    if not sources:
        raise ValueError("at least one reviewed submission or variant is required")
    expected_hashes = json.loads((args.problem / "hash.json").read_text())
    cases = []
    for name in args.cases:
        if Path(name).name != name or name in cases:
            raise ValueError("invalid or duplicate case name")
        for directory, suffix in (("in", ".in"), ("out", ".out")):
            path = args.problem / directory / (name + suffix)
            if file_digest(path) != expected_hashes.get(path.name):
                raise ValueError("official test hash mismatch: " + str(path))
        cases.append(name)
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(),
                  problem=snapshot["problem"], snapshot=snapshot,
                  officialHashSha256=file_digest(args.problem / "hash.json"),
                  checkerSha256=file_digest(args.problem / "checker"),
                  upstreamRevision=subprocess.check_output(
                      ["git", "-C", str(args.problem), "rev-parse", "HEAD"], text=True).strip(),
                  runtime=subprocess.check_output([args.python, "--version"], text=True).strip(),
                  repeat=args.repeat, seed=args.seed,
                  sourceSha256={name: file_digest(path) for name, path in sources.items()},
                  protocol="fresh processes, shuffled order, official checker, wall time including I/O and JIT",
                  results=[])
    with tempfile.TemporaryDirectory(prefix="harurun-comparison-") as directory:
        temporary = Path(directory)
        scripts = {}
        for name, source in sources.items():
            path = temporary / (str(len(scripts)) + ".py")
            path.write_bytes(source.read_bytes())
            scripts[name] = path
        for case in cases:
            samples = {name: [] for name in scripts}
            input_path = args.problem / "in" / (case + ".in")
            expected_path = args.problem / "out" / (case + ".out")
            for iteration in range(args.repeat):
                order = list(scripts)
                random.Random(args.seed + iteration).shuffle(order)
                for name in order:
                    output_path = temporary / "actual.txt"
                    elapsed, rss = measure([args.python, str(scripts[name])], input_path,
                                           output_path, temporary / "rss.txt", args.timeout)
                    checked = subprocess.run([str(args.problem / "checker"), str(input_path),
                                              str(output_path), str(expected_path)],
                                             capture_output=True, timeout=30)
                    if checked.returncode:
                        raise ValueError(name + "/" + case + ": " + checked.stderr.decode(errors="replace"))
                    samples[name].append(dict(seconds=elapsed, peakRssKiB=rss,
                                              outputSha256=file_digest(output_path)))
            result = dict(case=case, inputSha256=file_digest(input_path),
                          implementations={name: dict(samples=values,
                              medianSeconds=statistics.median(v["seconds"] for v in values),
                              peakRssKiB=max(v["peakRssKiB"] for v in values))
                              for name, values in samples.items()})
            report["results"].append(result)
            save_json(args.output, report)
            print(json.dumps(result), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--reviewed", type=int, nargs="+", default=[])
    parser.add_argument("--problem", type=Path, required=True)
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--variant", action="append", default=[])
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--seed", type=int, default=92471)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.repeat < 1 or args.timeout <= 0:
        parser.error("repeat and timeout must be positive")
    compare(args)


if __name__ == "__main__":
    main()
