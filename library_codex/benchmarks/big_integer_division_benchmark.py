import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import statistics
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", choices=("selected", "builtin", "uncached", "newton"))
    parser.add_argument("--radix", type=int, choices=(10, 16), default=16)
    parser.add_argument("--official", type=Path)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--cases", nargs="+", default=["length_ratio_integer_00", "a_max_b_random_01", "small_00"])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.worker:
        from library_codex.number_theory import BigIntegerDivision as division
        if args.worker in ("uncached", "newton"):
            from library_codex.benchmarks.variants import big_integer_division_newton as division
        if args.worker == "uncached":
            class NoCache(dict):
                def get(self, key):
                    return None
            original = division._decimal
            division._decimal = lambda value, powers, inverses: original(value, powers, NoCache())
        read = sys.stdin.readline
        answers = []
        if args.worker == "builtin" and args.radix == 10:
            sys.set_int_max_str_digits(0)
        for _ in range(int(read())):
            first, second = read().split()
            if args.worker == "builtin":
                q, r = divmod(int(first, args.radix), int(second, args.radix))
                result = (str(q), str(r)) if args.radix == 10 else (format(q, "X"), format(r, "X"))
            else:
                function = division.divide_decimal if args.radix == 10 else division.divide_hex
                result = function(first, second)
            answers.append(" ".join(result))
        sys.stdout.write("\n".join(answers) + "\n")
        return
    from library_codex.benchmarks.official_comparison import measure
    from library_codex.benchmarks.official_benchmark import runtime_info
    from library_codex.tools.check_library_checker import file_digest, save_json
    if args.official is None or args.repeat < 1:
        parser.error("require --official and repeat >= 1")
    name = "division_of_big_integers" if args.radix == 10 else "division_of_hex_big_integers"
    problem = args.official / "big_integer" / name
    hashes = json.loads((problem / "hash.json").read_text())
    for case in args.cases:
        if Path(case).name != case:
            parser.error("invalid case name")
        for directory, suffix in (("in", ".in"), ("out", ".out")):
            path = problem / directory / (case + suffix)
            if file_digest(path) != hashes.get(path.name):
                raise ValueError("official case hash mismatch: " + str(path))
    variants = {"selected": "builtin divmod; balanced decimal conversion with powers of five", "newton": "integer Newton reciprocal; cached conversion divisors"}
    variants["uncached" if args.radix == 10 else "builtin"] = (
        "recompute reciprocal at every decimal output split" if args.radix == 10 else "PyPy builtin int, divmod and hexadecimal format"
    )
    report = {
        "measuredAt": datetime.now(timezone.utc).isoformat(),
        "environment": runtime_info(sys.executable),
        "problem": name,
        "repeat": args.repeat,
        "sourceSha256": hashlib.sha256((ROOT / "library_codex/number_theory/BigIntegerDivision.py").read_text().encode()).hexdigest(),
        "baselineSha256": hashlib.sha256((ROOT / "library_codex/benchmarks/variants/big_integer_division_newton.py").read_text().encode()).hexdigest(),
        "harnessSha256": hashlib.sha256(Path(__file__).read_text().encode()).hexdigest(),
        "checkerSha256": file_digest(problem / "checker"),
        "upstreamRevision": subprocess.check_output(["git", "-C", str(args.official), "rev-parse", "HEAD"], text=True).strip(),
        "protocol": "sequential fresh PyPy processes, shuffled variants, startup/JIT/I/O included, official checker each run, GNU time RSS, no memory limit",
        "variants": variants,
        "results": [],
    }
    output_file = args.output or ROOT / "library_codex/benchmarks/results" / (name + "_comparison.json")
    with tempfile.TemporaryDirectory(prefix="harurun-division-") as directory:
        temporary = Path(directory)
        for case in args.cases:
            samples = {variant: [] for variant in variants}
            stdin = problem / "in" / (case + ".in")
            expected = problem / "out" / (case + ".out")
            for iteration in range(args.repeat):
                order = list(samples)
                random.Random(92108 + iteration).shuffle(order)
                for variant in order:
                    output = temporary / "output"
                    command = [sys.executable, str(Path(__file__).resolve()), "--worker", variant, "--radix", str(args.radix)]
                    elapsed, rss = measure(command, stdin, output, temporary / "rss", 120)
                    checked = subprocess.run([str(problem / "checker"), str(stdin), str(output), str(expected)], capture_output=True, timeout=30)
                    if checked.returncode:
                        raise ValueError(checked.stderr.decode(errors="replace"))
                    samples[variant].append({"seconds": elapsed, "peakRssKiB": rss, "outputSha256": file_digest(output)})
            row = {"case": case, "inputSha256": file_digest(stdin), "expectedSha256": file_digest(expected), "implementations": {}}
            for variant, values in samples.items():
                row["implementations"][variant] = {
                    "samples": values,
                    "medianSeconds": statistics.median(value["seconds"] for value in values),
                    "peakRssKiB": max(value["peakRssKiB"] for value in values),
                }
            report["results"].append(row)
            save_json(output_file, report)
            print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
