import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
SUITE = REPOSITORY / "verify" / "library_checker"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(REPOSITORY))

from build_codon import atomic_write
from build_library_catalog import build_standalone_code
from library_codex.benchmarks.lc_problems import PROBLEMS, problem_module, standalone
from library_codex.benchmarks.library_checker_cases import standalone_source


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def save_json(path, value):
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def load_official(root):
    root = root.resolve()
    if not (root / "generate.py").is_file() or not (root / "common" / "testlib.h").is_file():
        raise ValueError("expected a library-checker-problems checkout")
    sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location("lc_official_generate", root / "generate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    paths = sorted(path for path in root.glob("*/*/info.toml") if path.relative_to(root).parts[0] != "test")
    problems = {}
    for path in paths:
        name = path.parent.name
        if not re.fullmatch(r"[A-Za-z0-9_]+", name) or name in problems:
            raise ValueError("invalid or duplicate problem name: " + name)
        problems[name] = module.Problem(root, path.parent)
    if not problems:
        raise ValueError("official problem list is empty")
    return problems


def solution_source(name):
    driver = SUITE / "drivers" / (name + ".py")
    if driver.is_file():
        source, dependencies = build_standalone_code(driver, ROOT)
        return source, dependencies
    if name in PROBLEMS:
        return standalone(name).decode(), [problem_module(name).MODULE]
    if name in {"set_xor_min", "vertex_add_subtree_sum"}:
        modules = ["ordered_set/BinaryTrie.py"] if name == "set_xor_min" else ["fenwick_tree/BIT.py", "tree/HeavyLightDecomposition.py"]
        return standalone_source(name).decode(), modules
    return None, []


def solution(name):
    source, modules = solution_source(name)
    return (ast.unparse(ast.parse(source)) + "\n" if source is not None else None), modules


def build_solution(name):
    source, modules = solution(name)
    if source is None:
        raise ValueError("no solution for " + name)
    path = SUITE / "solutions" / (name + ".py")
    if not path.is_file() or path.read_text(encoding="utf-8") != source:
        atomic_write(path, source)
    return path, modules


def case_names(problem):
    names = [Path(test["name"]).stem + "_" + str(i).zfill(2)
             for test in problem.config["tests"] for i in range(test["number"])]
    if not names or len(names) != len(set(names)) or any(not re.fullmatch(r"[A-Za-z0-9_-]+", name) for name in names):
        raise ValueError("empty or invalid official case list")
    return names


def reuse_tests(problem, root):
    if root is None:
        return 0
    previous = root.resolve() / problem.basedir.relative_to(problem.rootdir)
    expected = json.loads((problem.basedir / "hash.json").read_text())
    copied = 0
    for case in case_names(problem):
        for folder, suffix in (("in", ".in"), ("out", ".out")):
            source = previous / folder / (case + suffix)
            target = problem.basedir / folder / source.name
            if target.exists() or not source.is_file():
                continue
            if expected.get(source.name) != file_digest(source):
                continue
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(source, target)
            copied += 1
    return copied


def judge_case(command, checker, input_path, expected_path, actual_path, timeout):
    started = perf_counter()
    try:
        with input_path.open("rb") as stdin, actual_path.open("wb") as stdout:
            process = subprocess.run(command, stdin=stdin, stdout=stdout, stderr=subprocess.PIPE, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"status": "TLE", "seconds": perf_counter() - started}
    elapsed = perf_counter() - started
    if process.returncode:
        return {"status": "RE", "seconds": elapsed, "diagnostic": process.stderr.decode(errors="replace")[-2000:]}
    try:
        checked = subprocess.run([str(checker), str(input_path), str(actual_path), str(expected_path)],
                                 capture_output=True, timeout=max(30, timeout))
    except subprocess.TimeoutExpired:
        return {"status": "CHECKER_ERROR", "seconds": elapsed, "diagnostic": "checker timeout"}
    status = "AC" if checked.returncode == 0 else "WA" if checked.returncode in (1, 2) else "CHECKER_ERROR"
    return {"status": status, "seconds": elapsed,
            "diagnostic": (checked.stdout + checked.stderr).decode(errors="replace")[-2000:]}


def verification_key(problem_version, source_hash, runtime, timeout, runner_hash):
    return digest(json.dumps([problem_version, source_hash, runtime, timeout, runner_hash]).encode())


def complete_pass(report, names):
    cases = report.get("cases", [])
    return (report.get("status") == "local_passed"
            and report.get("expectedCases") == len(names)
            and [case.get("name") for case in cases] == names
            and all(case.get("status") == "AC" for case in cases))


def check_solutions():
    paths = sorted((SUITE / "solutions").glob("*.py"))
    expected_names = set(PROBLEMS) | {"set_xor_min", "vertex_add_subtree_sum"}
    expected_names.update(path.stem for path in (SUITE / "drivers").glob("*.py"))
    errors = []
    if {path.stem for path in paths} != expected_names:
        errors.append("standalone solution list is stale")
    for path in paths:
        source, _ = solution(path.stem)
        if source is None or path.read_text(encoding="utf-8") != source:
            errors.append("stale standalone solution: " + path.stem)
    return errors


def judge(name, problem, runtime, force=False, reuse=None):
    path, modules = build_solution(name)
    source = path.read_text(encoding="utf-8")
    version = problem.problem_version()
    timeout = float(problem.config["timelimit"])
    runtime_version = subprocess.check_output([runtime, "--version"], text=True).strip()
    environment = digest(json.dumps([runtime_version, platform.platform(), platform.node()]).encode())
    key = verification_key(version, digest(source.encode()), environment, timeout,
                           digest(Path(__file__).read_text(encoding="utf-8").encode()))
    names = case_names(problem)
    report_path = SUITE / "results" / (name + ".json")
    if report_path.is_file() and not force:
        previous = json.loads(report_path.read_text(encoding="utf-8"))
        if previous.get("verificationKey") == key and complete_pass(previous, names):
            print(name + ": cached local pass", flush=True)
            return True
    report = {"problem": name, "status": "incomplete", "verificationKey": key,
              "sourceSha256": digest(source.encode()), "modules": modules,
              "problemVersion": version, "runtime": runtime_version, "platform": platform.platform(),
              "environmentFingerprint": environment,
              "upstreamRevision": subprocess.check_output(["git", "-C", str(problem.rootdir), "rev-parse", "HEAD"], text=True).strip(),
              "timeLimitSeconds": timeout, "expectedCases": len(names), "cases": [],
              "verifiedAt": datetime.now(timezone.utc).isoformat(), "onlineSubmission": None}
    save_json(report_path, report)
    try:
        copied = reuse_tests(problem, reuse)
        if copied:
            print(f"{name}: reused {copied} hash-verified test files", flush=True)
        subprocess.run([sys.executable, str(problem.rootdir / "generate.py"), str(problem.basedir / "info.toml")],
                       cwd=problem.rootdir, check=True, timeout=1800)
        checker = problem.checker.with_suffix("")
        with tempfile.TemporaryDirectory(prefix="harurun-lc-") as directory:
            temporary = Path(directory)
            script = temporary / "main.py"
            script.write_text(source, encoding="utf-8")
            for case in names:
                result = judge_case([runtime, str(script)], checker, problem.basedir / "in" / (case + ".in"),
                                    problem.basedir / "out" / (case + ".out"), temporary / "actual.out", timeout)
                report["cases"].append(dict(name=case, **result))
                save_json(report_path, report)
                print(f"{name}/{case}: {result['status']} {result['seconds']:.3f}s", flush=True)
        report["status"] = "local_passed" if all(row["status"] == "AC" for row in report["cases"]) else "failed"
    except Exception as error:
        report["status"] = "error"
        report["diagnostic"] = str(error)
    save_json(report_path, report)
    return report["status"] == "local_passed"


def inventory(problems):
    rows = []
    for name, problem in sorted(problems.items()):
        source, modules = solution(name)
        status = "unimplemented" if source is None else "unverified"
        result = SUITE / "results" / (name + ".json")
        if source is not None and result.is_file():
            previous = json.loads(result.read_text(encoding="utf-8"))
            status = previous["status"] if previous.get("sourceSha256") == digest(source.encode()) and previous.get("problemVersion") == problem.problem_version() else "stale"
            if status == "local_passed" and not complete_pass(previous, case_names(problem)):
                status = "incomplete"
        rows.append({"name": name, "title": problem.config["title"],
                     "category": problem.basedir.relative_to(problem.rootdir).parts[0],
                     "url": "https://judge.yosupo.jp/problem/" + name, "status": status, "modules": modules,
                     "solution": "solutions/" + name + ".py" if source is not None else None,
                     "result": "results/" + name + ".json" if result.is_file() else None})
    value = {"schemaVersion": 1, "upstreamRevision": subprocess.check_output(
        ["git", "-C", str(next(iter(problems.values())).rootdir), "rev-parse", "HEAD"], text=True).strip(),
        "counts": {status: sum(row["status"] == status for row in rows) for status in sorted({row["status"] for row in rows})},
        "problems": rows}
    save_json(SUITE / "manifest.json", value)
    print(json.dumps(value["counts"], ensure_ascii=False), flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("list", "build", "test", "check"))
    parser.add_argument("problems", nargs="*")
    parser.add_argument("--official", type=Path)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--reuse-tests", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.command == "check":
        errors = check_solutions()
        if errors:
            raise SystemExit("\n".join(errors) + "\nRun check_library_checker.py build to refresh solutions.")
        print("Standalone solutions are current.")
        return
    if args.command == "build" and args.official is None:
        names = set(PROBLEMS) | {"set_xor_min", "vertex_add_subtree_sum"}
        names.update(path.stem for path in (SUITE / "drivers").glob("*.py"))
        for name in args.problems or sorted(names):
            if name not in names:
                parser.error("unknown solution: " + name)
            build_solution(name)
        return
    if args.official is None:
        parser.error("--official is required for list and test")
    problems = load_official(args.official)
    if any(name not in problems for name in args.problems):
        parser.error("unknown problem")
    selected = args.problems or [name for name in problems if solution(name)[0] is not None]
    failed = []
    for name in selected if args.command != "list" else []:
        if args.command == "build":
            build_solution(name)
        elif not judge(name, problems[name], args.python, args.force, args.reuse_tests):
            failed.append(name)
    inventory(problems)
    if failed:
        raise SystemExit("failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
