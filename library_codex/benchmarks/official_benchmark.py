import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.benchmarks.official_comparison import measure
from library_codex.tools.check_library_checker import (
    SUITE, case_names, complete_pass, digest, file_digest, load_official,
    save_json, solution,
)
from library_codex.tools.build_codon import atomic_write


def runtime_info(runtime):
    version = subprocess.check_output([runtime, "--version"], text=True).strip()
    if "PyPy" not in version:
        raise ValueError("this benchmark requires PyPy")
    cpu = platform.processor()
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        for line in cpuinfo.read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    return dict(runtime=version, platform=platform.platform(), cpu=cpu,
                machine=platform.machine())


def select_cases(verification, names, source_hash, version, slowest):
    if not complete_pass(verification, names):
        raise ValueError("complete official verification required")
    if verification.get("sourceSha256") != source_hash or verification.get("problemVersion") != version:
        raise ValueError("official verification is stale")
    rows = sorted(verification["cases"], key=lambda row: (-row["seconds"], row["name"]))
    return [row["name"] for row in (rows[:slowest] if slowest else rows)]


def benchmark(name, problem, runtime, repeat, slowest, output_dir, seed=92471):
    if repeat < 1 or slowest < 0:
        raise ValueError("repeat must be positive and slowest nonnegative")
    environment = runtime_info(runtime)
    source, modules = solution(name)
    if source is None:
        raise ValueError("no solution: " + name)
    source_hash = digest(source.encode())
    verification_path = SUITE / "results" / (name + ".json")
    verification = json.loads(verification_path.read_text())
    version = problem.problem_version()
    names = select_cases(verification, case_names(problem), source_hash, version, slowest)
    hashes_path = problem.basedir / "hash.json"
    hashes = json.loads(hashes_path.read_text())
    for case in names:
        for directory, suffix in (("in", ".in"), ("out", ".out")):
            path = problem.basedir / directory / (case + suffix)
            if hashes.get(path.name) != file_digest(path):
                raise ValueError("official test hash mismatch: " + str(path))
    checker = problem.checker.with_suffix("")
    report = dict(schemaVersion=1, problem=name, measuredAt=datetime.now(timezone.utc).isoformat(),
                  environment=environment, sourceSha256=source_hash, modules=modules,
                  problemVersion=version, officialHashSha256=file_digest(hashes_path),
                  checkerSha256=file_digest(checker), verificationSha256=file_digest(verification_path),
                  upstreamRevision=subprocess.check_output(
                      ["git", "-C", str(problem.rootdir), "rev-parse", "HEAD"], text=True).strip(),
                  repeat=repeat, seed=seed, officialCases=len(case_names(problem)),
                  selection="all official cases" if slowest == 0 else "slowest cases in preceding full verification",
                  selectedCases=names, timeLimitSeconds=float(problem.config["timelimit"]),
                  protocol="sequential fresh PyPy processes; startup, JIT and I/O included; shuffled case order; official checker; peak RSS from GNU time; memory limit not enforced",
                  results=[])
    samples = {case: [] for case in names}
    with tempfile.TemporaryDirectory(prefix="harurun-official-benchmark-") as directory:
        temporary = Path(directory)
        script = temporary / "main.py"
        script.write_text(source)
        for iteration in range(repeat):
            order = names.copy()
            random.Random(seed + iteration).shuffle(order)
            for case in order:
                input_path = problem.basedir / "in" / (case + ".in")
                expected_path = problem.basedir / "out" / (case + ".out")
                output_path = temporary / "actual.out"
                elapsed, rss = measure([runtime, str(script)], input_path, output_path,
                                       temporary / "rss.txt", max(30, report["timeLimitSeconds"]))
                checked = subprocess.run([str(checker), str(input_path), str(output_path), str(expected_path)],
                                         capture_output=True, timeout=30)
                if checked.returncode:
                    raise ValueError(name + "/" + case + ": " + checked.stderr.decode(errors="replace"))
                samples[case].append(dict(seconds=elapsed, peakRssKiB=rss,
                                          outputSha256=file_digest(output_path)))
        for case in names:
            values = samples[case]
            times = [row["seconds"] for row in values]
            report["results"].append(dict(case=case,
                inputSha256=hashes[case + ".in"], expectedSha256=hashes[case + ".out"],
                samples=values, medianSeconds=statistics.median(times),
                minSeconds=min(times), maxSeconds=max(times),
                peakRssKiB=max(row["peakRssKiB"] for row in values)))
    save_json(output_dir / (name + ".json"), report)
    print(json.dumps(dict(problem=name, cases=len(names), repeat=repeat,
        maxMedianSeconds=max(row["medianSeconds"] for row in report["results"]),
        peakRssKiB=max(row["peakRssKiB"] for row in report["results"]))), flush=True)
    return report


def write_summary(output_dir):
    lines = ["# PyPy公式ケースのベンチマーク", "",
             "公式全件検証後、各問題で時間のかかったケースを再測定した記録。時間は起動・JIT・入出力込みの中央値、メモリは測定中の最大RSS。オンライン提出は行わない。", "",
             "全公式ケースの判定・単発時間は `../results/`、各回の時間・RSS・入力とソースのhashはリンク先のJSONを参照。環境が違う記録間の速度は直接比較しない。", "",
             "| 問題 | 測定ケース / 公式全件 | 反復数 | 最大中央値（秒） | 最大RSS（MiB） | ソース同期 |",
             "| --- | ---: | ---: | ---: | ---: | --- |"]
    for path in sorted(output_dir.glob("*.json")):
        report = json.loads(path.read_text())
        source, _ = solution(report["problem"])
        current = source is not None and digest(source.encode()) == report["sourceSha256"]
        seconds = max(row["medianSeconds"] for row in report["results"])
        rss = max(row["peakRssKiB"] for row in report["results"]) / 1024
        lines.append(f"| [{report['problem']}]({path.name}) | {len(report['results'])} / {report['officialCases']} | {report['repeat']} | {seconds:.3f} | {rss:.1f} | {'一致' if current else '要再測定'} |")
    atomic_write(output_dir / "README.md", "\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("problems", nargs="+")
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--slowest", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=SUITE / "benchmarks")
    args = parser.parse_args()
    if args.repeat < 1 or args.slowest < 0:
        parser.error("repeat must be positive and slowest nonnegative")
    problems = load_official(args.official)
    if any(name not in problems for name in args.problems):
        parser.error("unknown problem")
    for name in args.problems:
        benchmark(name, problems[name], args.python, args.repeat, args.slowest, args.output_dir)
    write_summary(args.output_dir)


if __name__ == "__main__":
    main()
