import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import tempfile
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def worker(case, variant):
    from library_codex.string_sequence.EditDistance import edit_distance, edit_distance_bounded, _edit_distance_dp
    from library_codex.fps.SparseFormalPowerSeries import sparse_differential
    from library_codex.fps998.FPS import fps_div, fps_exp
    rng = random.Random(77182)
    if case.startswith("fps"):
        size = 8192 if case == "fps8192" else 65536
        data = [size, [0, 1], [1, -2, 1]]
        started = perf_counter()
        if variant == "differential":
            value = sparse_differential([1], [1, -2, 1], size)
        else:
            value = fps_exp(fps_div([0, 1], [1, -1], size), size)
    else:
        if case == "tiny":
            a, b = [rng.randrange(4) for _ in range(24)], [rng.randrange(4) for _ in range(24)]
            repeat = 2000
        elif case == "distinct":
            a, b = list(range(4000)), list(range(1, 4001))
            repeat = 1
        elif case == "near":
            a = [rng.randrange(4) for _ in range(4000)]
            b = a.copy()
            b[700], b[2700] = 9, 9
            repeat = 1
        elif case == "unequal":
            a, b = [1] * 16000, [2] * 16
            repeat = 1
        else:
            a, b = [rng.randrange(4) for _ in range(4000)], [rng.randrange(4) for _ in range(4000)]
            repeat = 1
        data = [a, b, repeat]
        started = perf_counter()
        for _ in range(repeat):
            value = _edit_distance_dp(a, b) if variant == "dp" else edit_distance_bounded(a, b, 8) if variant == "bounded" else edit_distance(a, b)
    elapsed = perf_counter() - started
    print(json.dumps(dict(seconds=elapsed, inputSha256=hashlib.sha256(json.dumps(data).encode()).hexdigest(), resultSha256=hashlib.sha256(json.dumps(value).encode()).hexdigest())))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", nargs=2)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--output", type=Path, default=ROOT / "verify/library_checker/benchmarks/comparisons/reference-expansion.json")
    args = parser.parse_args()
    if args.worker:
        worker(*args.worker)
        return
    version = subprocess.check_output([args.python, "--version"], text=True).strip()
    if "PyPy" not in version:
        raise ValueError("PyPy required")
    if args.cpu is not None:
        os.sched_setaffinity(0, {args.cpu})
    rows = []
    with tempfile.TemporaryDirectory() as directory:
        rss_file = Path(directory) / "rss"
        for case in ("tiny", "random", "distinct", "near", "unequal", "fps8192", "fps65536"):
            variants = ["dense", "differential"] if case.startswith("fps") else ["dp", "bitset", "bounded"] if case == "near" else ["dp", "bitset"]
            samples = {variant: [] for variant in variants}
            answer = fingerprint = None
            for iteration in range(args.repeat):
                order = variants.copy()
                random.Random(77182 + iteration).shuffle(order)
                for variant in order:
                    started = perf_counter()
                    run = subprocess.run(["/usr/bin/time", "-f", "%M", "-o", str(rss_file), args.python, str(Path(__file__).resolve()), "--worker", case, variant], capture_output=True, text=True, check=True, timeout=180)
                    sample = json.loads(run.stdout)
                    sample.update(wallSeconds=perf_counter() - started, peakRssKiB=int(rss_file.read_text().strip()))
                    if answer is None:
                        answer, fingerprint = sample["resultSha256"], sample["inputSha256"]
                    assert (sample["resultSha256"], sample["inputSha256"]) == (answer, fingerprint)
                    samples[variant].append(sample)
                    print(case, variant, iteration + 1, round(sample["seconds"], 6), sample["peakRssKiB"], flush=True)
            rows.append(dict(case=case, samples=samples, summary={key: dict(medianSeconds=statistics.median(v["seconds"] for v in values), peakRssKiB=max(v["peakRssKiB"] for v in values)) for key, values in samples.items()}))
    source_paths = ["string_sequence/EditDistance.py", "fps/SparseFormalPowerSeries.py", "fps998/FPS.py"]
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(), environment=dict(runtime=version, platform=platform.platform(), cpuInfo=Path("/proc/cpuinfo").read_text().split("model name", 1)[1].splitlines()[0].lstrip("\t: "), affinity=sorted(os.sched_getaffinity(0))), repeat=args.repeat, protocol="sequential fresh PyPy processes; deterministic shared input; shuffled variant order; core time and startup-inclusive wall time; GNU time peak RSS; no memory limit", sourceSha256={p: hashlib.sha256((ROOT / "library_codex" / p).read_bytes()).hexdigest() for p in source_paths}, results=rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    json.loads(temporary.read_text())
    temporary.replace(args.output)


if __name__ == "__main__":
    main()
