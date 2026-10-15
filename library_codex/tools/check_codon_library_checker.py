import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import statistics
import subprocess
import sys
import tempfile
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.tools import build_codon
from library_codex.tools import check_library_checker as lc
from library_codex.benchmarks.official_benchmark import runtime_info
from library_codex.benchmarks.official_comparison import measure


PROBLEMS = {
    "scc": "graph_connectivity/StronglyConnectedComponents",
    "two_sat": "graph/TwoSAT",
}
OUTPUT = lc.SUITE / "codon"


class DriverTransformer(ast.NodeTransformer):
    def visit_Assign(self, node):
        node = self.generic_visit(node)
        if any(isinstance(target, (ast.Tuple, ast.List)) for target in node.targets) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "map":
            node.value = ast.Call(ast.Name("list", ast.Load()), [node.value], [])
        return node

    def visit_Call(self, node):
        node = self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "print" and any(isinstance(arg, ast.Starred) for arg in node.args):
            if node.keywords:
                raise ValueError("unsupported starred print options")
            parts = []
            for arg in node.args:
                if isinstance(arg, ast.Starred):
                    parts.append(ast.ListComp(ast.Call(ast.Name("str", ast.Load()), [ast.Name("_codon_item", ast.Load())], []), [ast.comprehension(ast.Name("_codon_item", ast.Store()), arg.value, [], 0)]))
                else:
                    parts.append(ast.List([ast.Call(ast.Name("str", ast.Load()), [arg], [])], ast.Load()))
            result = parts[0]
            for part in parts[1:]:
                result = ast.BinOp(result, ast.Add(), part)
            node.args = [ast.Call(ast.Attribute(ast.Constant(" "), "join", ast.Load()), [result], [])]
        return node


def solution(name):
    module = PROBLEMS[name]
    tree = ast.parse((lc.SUITE / "drivers" / (name + ".py")).read_text(encoding="utf-8"))
    body = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("library_codex."):
            if node.module != "library_codex." + module.replace("/", "."):
                raise ValueError("unverified Codon driver dependency: " + node.module)
            continue
        body.append(node)
    tree.body = body
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and ast.unparse(node.value) == "sys.stdin.buffer":
            node.value = ast.parse("sys.stdin", mode="eval").body
    tree = DriverTransformer().visit(tree)
    return build_codon.generate(module) + "\n" + ast.unparse(ast.fix_missing_locations(tree)) + "\n"


def build(check=False):
    valid = True
    for name in PROBLEMS:
        source = solution(name)
        path = OUTPUT / "solutions" / (name + ".codon")
        if not path.is_file() or path.read_text(encoding="utf-8") != source:
            if check:
                print("stale Codon solution: " + name)
                valid = False
            else:
                build_codon.atomic_write(path, source)
    return valid


def verify(name, problem, codon, pypy, repeat):
    if repeat < 1:
        raise ValueError("repeat must be positive")
    version = subprocess.check_output([codon, "--version"], text=True).strip()
    if version != "0.19.3":
        raise ValueError("Codon 0.19.3 required")
    source = solution(name)
    reference, _ = lc.solution(name)
    names = lc.case_names(problem)
    limit = float(problem.config["timelimit"])
    subprocess.run([sys.executable, str(problem.rootdir / "generate.py"), str(problem.basedir / "info.toml")], cwd=problem.rootdir, check=True, timeout=1800)
    hashes = json.loads((problem.basedir / "hash.json").read_text())
    for case in names:
        for directory, suffix in (("in", ".in"), ("out", ".out")):
            path = problem.basedir / directory / (case + suffix)
            if lc.file_digest(path) != hashes.get(path.name):
                raise ValueError("official test hash mismatch: " + str(path))
    checker = problem.checker.with_suffix("")
    report = dict(schemaVersion=1, problem=name, module=PROBLEMS[name], status="incomplete",
                  verifiedAt=datetime.now(timezone.utc).isoformat(), compilerVersion=version,
                  environment=runtime_info(pypy), sourceSha256=lc.digest(source.encode()),
                  pypySourceSha256=lc.digest(reference.encode()), problemVersion=problem.problem_version(),
                  runnerSha256=lc.file_digest(Path(__file__)), checkerSha256=lc.file_digest(checker),
                  timeLimitSeconds=limit, expectedCases=len(names), cases=[], benchmarks=[], repeat=repeat,
                  protocol="sequential fresh processes; compilation excluded; startup and IO included; official checker; GNU time peak RSS; memory limit not enforced",
                  onlineSubmission=None)
    with tempfile.TemporaryDirectory(prefix="harurun-codon-official-") as directory:
        folder = Path(directory)
        native = folder / "main.codon"
        native.write_text(source, encoding="utf-8")
        original = folder / "main.py"
        original.write_text(reference, encoding="utf-8")
        executable = folder / "main"
        started = perf_counter()
        compiled = subprocess.run([codon, "build", "--release", "-o", str(executable), str(native)], capture_output=True, text=True, timeout=180)
        report["compileSeconds"] = perf_counter() - started
        if compiled.returncode:
            raise RuntimeError(compiled.stdout + compiled.stderr)
        report["binarySha256"] = lc.file_digest(executable)
        commands = {"codon": [str(executable)], "pypy": [pypy, str(original)]}
        for case in names:
            result = lc.judge_case(commands["codon"], checker, problem.basedir / "in" / (case + ".in"), problem.basedir / "out" / (case + ".out"), folder / "actual.out", limit)
            report["cases"].append(dict(name=case, **result))
            print(f"{name}/{case}: {result['status']} {result['seconds']:.3f}s", flush=True)
        report["status"] = "local_passed" if all(row["status"] == "AC" for row in report["cases"]) else "failed"
        if report["status"] != "local_passed":
            lc.save_json(OUTPUT / "failures" / (name + ".json"), report)
            raise ValueError("Codon official tests failed: " + name)
        selected = sorted(report["cases"], key=lambda row: (-row["seconds"], row["name"]))[:3]
        for row in selected:
            case = row["name"]
            samples = {variant: [] for variant in commands}
            for iteration in range(repeat):
                order = list(commands)
                random.Random(417 + iteration).shuffle(order)
                for variant in order:
                    actual = folder / "actual.out"
                    input_path = problem.basedir / "in" / (case + ".in")
                    expected = problem.basedir / "out" / (case + ".out")
                    elapsed, rss = measure(commands[variant], input_path, actual, folder / "rss.txt", max(30, limit))
                    checked = subprocess.run([str(checker), str(input_path), str(actual), str(expected)], capture_output=True, timeout=30)
                    if checked.returncode:
                        raise ValueError(variant + " output failed checker: " + checked.stderr.decode(errors="replace"))
                    samples[variant].append(dict(seconds=elapsed, peakRssKiB=rss, outputSha256=lc.file_digest(actual)))
            report["benchmarks"].append(dict(case=case, inputSha256=hashes[case + ".in"], expectedSha256=hashes[case + ".out"], samples=samples,
                medianSeconds={variant: statistics.median(row["seconds"] for row in values) for variant, values in samples.items()}))
    lc.save_json(OUTPUT / "results" / (name + ".json"), report)
    print(json.dumps({"problem": name, "status": report["status"], "cases": len(names), "benchmarks": [{"case": row["case"], **row["medianSeconds"]} for row in report["benchmarks"]]}), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "check", "test"))
    parser.add_argument("problems", nargs="*")
    parser.add_argument("--official", type=Path)
    parser.add_argument("--codon", default="codon")
    parser.add_argument("--pypy", default="pypy3")
    parser.add_argument("--repeat", type=int, default=5)
    args = parser.parse_args()
    if any(name not in PROBLEMS for name in args.problems) or args.repeat < 1:
        parser.error("unknown problem or nonpositive repeat")
    if args.command == "test" and args.official is None:
        parser.error("--official required")
    if not build(args.command == "check"):
        raise SystemExit(1)
    if args.command == "test":
        official = lc.load_official(args.official)
        for name in args.problems or PROBLEMS:
            verify(name, official[name], args.codon, args.pypy, args.repeat)


if __name__ == "__main__":
    main()
