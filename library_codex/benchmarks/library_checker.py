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
from urllib.parse import urlencode
from urllib.request import urlopen


API = "https://v3.api.judge.yosupo.jp"
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from library_codex.benchmarks.lc_problems import PROBLEMS, problem_module, standalone


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".lc-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def request(path, **parameters):
    url = API + path
    if parameters:
        url += "?" + urlencode(parameters)
    with urlopen(url, timeout=30) as response:
        return json.load(response)


def select_latest(rows, problem, language):
    return [row for row in rows if row["problem_name"] == problem
            and row["status"] == "AC" and row["is_latest"]
            and (not language or row["lang"] == language)]


def fetch(args):
    before = request("/problems/" + args.problem)
    languages = request("/langs")["langs"]
    rows = []
    skip = 0
    while len(rows) < args.top:
        result = request("/submissions", problem=args.problem, status="AC",
                         lang=args.language, order="+time", skip=skip, limit=100)
        page = result["submissions"]
        rows.extend(select_latest(page, args.problem, args.language))
        skip += len(page)
        if not page or skip >= result["count"]:
            break
    selected = []
    for row in rows[:args.top]:
        submission = request("/submissions/" + str(row["id"]))
        current = submission["overview"]
        if not select_latest([current], args.problem, args.language):
            raise ValueError("submission changed during retrieval")
        source = submission["source"].encode()
        suffix = ".py" if current["lang"] in {"pypy3", "python3"} else ".cpp"
        filename = str(row["id"]) + suffix
        atomic_write(args.cache / filename, source)
        selected.append(dict(current, sourceFile=filename,
                             sourceSha256=hashlib.sha256(source).hexdigest(),
                             url="https://judge.yosupo.jp/submission/" + str(row["id"])))
    after = request("/problems/" + args.problem)
    if before != after:
        raise ValueError("problem version changed during retrieval; retry")
    snapshot = dict(retrievedAt=datetime.now(timezone.utc).isoformat(),
                    api=API, problem=args.problem, problemInfo=after,
                    language=args.language, languages=languages,
                    selection="AC, is_latest, ascending judge time; ties may vary",
                    submissions=selected)
    path = args.cache / (args.problem + "-" + args.language + ".json")
    atomic_write(path, json_bytes(snapshot))
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))


def verify_source(cache, row):
    path = (cache / row["sourceFile"]).resolve()
    if path.parent != cache.resolve():
        raise ValueError("source path leaves the cache")
    if hashlib.sha256(path.read_bytes()).hexdigest() != row["sourceSha256"]:
        raise ValueError("source hash mismatch")
    return path


def run_once(command, input_path, timeout, directory):
    timing = directory / "timing.txt"
    start = perf_counter()
    with input_path.open("rb") as stream:
        completed = subprocess.run(
            ["/usr/bin/time", "-f", "%M", "-o", str(timing), *command],
            stdin=stream, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=directory, timeout=timeout, check=True,
        )
    elapsed = perf_counter() - start
    return completed.stdout.split(), elapsed, int(timing.read_text())


def compare(args):
    from library_codex.benchmarks.library_checker_cases import make_case, standalone_source

    snapshot = json.loads(args.snapshot.read_text())
    if snapshot["language"] not in {"pypy3", "python3"}:
        raise ValueError("runner currently supports reviewed Python sources only")
    ids = set(args.reviewed)
    selected = [row for row in snapshot["submissions"] if row["id"] in ids]
    if ids != {row["id"] for row in selected} or not ids:
        raise ValueError("explicit reviewed submission IDs are required")
    sources = {str(row["id"]): verify_source(args.snapshot.parent, row).read_bytes()
               for row in selected}
    sources["library"] = standalone_source(snapshot["problem"])
    if getattr(args, "baseline", None) is not None:
        sources["before"] = args.baseline.read_bytes()
    if getattr(args, "candidate", None) is not None:
        sources["candidate"] = args.candidate.read_bytes()
    if snapshot["problem"] in PROBLEMS and not getattr(args, "no_variants", False):
        for variant in getattr(problem_module(snapshot["problem"]), "VARIANTS", {}):
            sources["library_" + variant] = standalone(snapshot["problem"], variant)
    if snapshot["problem"] == "vertex_add_subtree_sum":
        sources["library_dsu"] = standalone_source("subtree_dsu")
    report = dict(snapshot=snapshot, runtime=subprocess.check_output(
        [args.python, "--version"], text=True).strip(), host=platform.platform(),
        measuredAt=datetime.now(timezone.utc).isoformat(),
        timing="fresh process, regular-file stdin, I/O and startup included",
        sourceHashes={name: hashlib.sha256(code).hexdigest() for name, code in sources.items()},
        repeat=args.repeat, seed=args.seed, results=[])
    with tempfile.TemporaryDirectory(prefix="lc-bench-") as temporary:
        directory = Path(temporary)
        commands = {}
        for name, code in sources.items():
            script = directory / (name + ".py")
            script.write_bytes(code)
            commands[name] = [args.python, str(script)]
        families = args.families or (problem_module(snapshot["problem"]).FAMILIES
            if snapshot["problem"] in PROBLEMS else
            ("random", "chain", "star", "balanced") if snapshot["problem"] == "vertex_add_subtree_sum"
            else ("random", "dense", "duplicates", "prefix"))
        for family in families:
            data, expected = make_case(snapshot["problem"], args.size, family, args.seed)
            path = directory / "input.txt"
            path.write_bytes(data)
            samples = {name: [] for name in commands}
            output = None
            for round_id in range(args.repeat):
                order = list(commands)
                random.Random(args.seed + round_id).shuffle(order)
                for name in order:
                    actual, elapsed, rss = run_once(commands[name], path, args.timeout, directory)
                    if output is None:
                        output = actual
                    if actual != output or (expected is not None and actual != expected):
                        raise ValueError("output mismatch: " + name + " / " + family)
                    samples[name].append((elapsed, rss))
            row = dict(family=family, size=args.size,
                       inputSha256=hashlib.sha256(data).hexdigest(),
                       outputSha256=hashlib.sha256(b"\n".join(output)).hexdigest(),
                       outputTokens=len(output), bruteChecked=expected is not None,
                       implementations={name: dict(seconds=[x[0] for x in values],
                           medianSeconds=statistics.median(x[0] for x in values),
                           peakRssKiB=max(x[1] for x in values))
                           for name, values in samples.items()})
            report["results"].append(row)
            atomic_write(args.output, json_bytes(report))
            print(json.dumps(row), flush=True)


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    fetcher = commands.add_parser("fetch")
    fetcher.add_argument("--problem", choices=["set_xor_min", "vertex_add_subtree_sum", *PROBLEMS], required=True)
    fetcher.add_argument("--language", choices=["pypy3", "python3", "cpp", "cpp17"], default="pypy3")
    fetcher.add_argument("--top", type=int, default=2)
    fetcher.add_argument("--cache", type=Path, required=True)
    runner = commands.add_parser("compare")
    runner.add_argument("--snapshot", type=Path, required=True)
    runner.add_argument("--reviewed", type=int, nargs="+", required=True)
    runner.add_argument("--python", default=sys.executable)
    runner.add_argument("--size", type=int, default=100000)
    runner.add_argument("--families", nargs="+")
    runner.add_argument("--seed", type=int, default=92471)
    runner.add_argument("--repeat", type=int, default=5)
    runner.add_argument("--timeout", type=float, default=60)
    runner.add_argument("--output", type=Path, required=True)
    runner.add_argument("--baseline", type=Path)
    runner.add_argument("--candidate", type=Path)
    runner.add_argument("--no-variants", action="store_true")
    args = parser.parse_args()
    if args.command == "fetch":
        if not 1 <= args.top <= 10:
            parser.error("top must be between 1 and 10")
        fetch(args)
    else:
        if args.size < 2 or args.repeat < 1 or args.timeout <= 0:
            parser.error("invalid size, repeat or timeout")
        compare(args)


if __name__ == "__main__":
    main()
