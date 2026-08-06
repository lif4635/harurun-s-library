"""Run only the checks affected by the current library_codex changes."""

import argparse
import ast
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from category_config import DATA_STRUCTURE_CATEGORIES, SOURCE_CATEGORIES


def normalize_path(value):
    path = Path(str(value).replace("\\", "/"))
    try:
        relative = path.resolve().relative_to(ROOT.resolve()).as_posix()
        return "library_codex/" + relative
    except (OSError, ValueError):
        pass
    try:
        return path.resolve().relative_to(REPOSITORY.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix().lstrip("./")


def git_lines(*arguments):
    completed = subprocess.run(
        ["git", "-C", str(REPOSITORY), *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        raise SystemExit(completed.stderr.strip() or "git diff failed")
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def changed_paths(base=None, explicit=()):
    if explicit:
        return sorted({normalize_path(path) for path in explicit})
    if base:
        paths = set(git_lines("diff", "--name-only", base, "--"))
        paths.update(git_lines("ls-files", "--others", "--exclude-standard"))
        return sorted(paths)
    paths = set(git_lines("diff", "--name-only", "HEAD", "--"))
    paths.update(git_lines("diff", "--name-only", "--cached", "--"))
    paths.update(git_lines("ls-files", "--others", "--exclude-standard"))
    return sorted(paths)


def source_module_key(path):
    parts = normalize_path(path).split("/")
    if len(parts) != 3 or parts[0] != "library_codex":
        return None
    category, filename = parts[1:]
    if category not in SOURCE_CATEGORIES or not filename.endswith(".py"):
        return None
    if filename.startswith("_"):
        return None
    return f"{category}/{filename[:-3]}"


def module_key_from_import(module_name):
    parts = module_name.split(".")
    if parts and parts[0] == "library_codex":
        parts = parts[1:]
    if len(parts) < 2 or parts[0] not in SOURCE_CATEGORIES:
        return None
    return f"{parts[0]}/{parts[1]}"


def imported_module_keys(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeError):
        return set()
    result = set()
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
        elif isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        for name in names:
            key = module_key_from_import(name)
            if key:
                result.add(key)
    return result


def source_files():
    result = {}
    for category in sorted(SOURCE_CATEGORIES):
        for path in sorted((ROOT / category).glob("*.py")):
            key = source_module_key(path)
            if key:
                result[key] = path
    return result


def affected_modules(direct):
    files = source_files()
    dependencies = {
        key: imported_module_keys(path)
        for key, path in files.items()
    }
    affected = set(direct)
    while True:
        added = {
            key for key, imported in dependencies.items()
            if key not in affected and imported & affected
        }
        if not added:
            return affected
        affected.update(added)


def imported_tests(modules):
    selected = set()
    for path in sorted((ROOT / "verify").rglob("test_*.py")):
        if imported_module_keys(path) & modules:
            selected.add(path)
    return selected


def plan_for(paths):
    paths = [normalize_path(path) for path in paths]
    direct = {key for key in map(source_module_key, paths) if key}
    affected = affected_modules(direct) if direct else set()
    tests = imported_tests(affected) if affected else set()

    for relative in paths:
        if relative.startswith("library_codex/verify/") and relative.endswith(".py"):
            path = REPOSITORY / relative
            if path.is_file():
                tests.add(path)

    source_changed = bool(direct)
    api_changed = source_changed or any(
        relative.startswith("library_codex/docs/api/")
        or relative in {
            "library_codex/tools/api_metadata.py",
            "library_codex/tools/build_api_reference.py",
        }
        for relative in paths
    )
    catalog_changed = api_changed or any(
        relative in {
            "library_codex/README.md",
            "library_codex/tools/build_library_catalog.py",
            "library_codex/tools/category_config.py",
        }
        for relative in paths
    )
    policy_changed = any(
        relative in {
            "AGENTS.md",
            ".github/pull_request_template.md",
            "library_codex/README.md",
            "library_codex/docs/CONTRIBUTING.md",
            "library_codex/tools/check_changed.py",
            "library_codex/tools/check_library.py",
        }
        for relative in paths
    )
    if api_changed:
        tests.add(ROOT / "verify" / "test_api_reference.py")
    if catalog_changed:
        tests.add(ROOT / "verify" / "test_library_catalog.py")
    if policy_changed:
        tests.add(ROOT / "verify" / "test_contribution_guide.py")
        tests.add(ROOT / "verify" / "test_changed_checks.py")
    if source_changed:
        tests.add(ROOT / "verify" / "test_module_boundaries.py")
    if any(key.split("/", 1)[0] in DATA_STRUCTURE_CATEGORIES for key in direct):
        tests.add(ROOT / "verify" / "data_structure" / "test_debug_output.py")

    categories_without_tests = {
        key.split("/", 1)[0]
        for key in direct
        if not any(key in imported_module_keys(path) for path in tests if path.is_file())
    }
    for category in categories_without_tests:
        directory = ROOT / "verify" / category
        if directory.is_dir():
            tests.add(directory)

    python_paths = [
        REPOSITORY / relative for relative in paths
        if relative.endswith(".py") and (REPOSITORY / relative).is_file()
    ]
    files = source_files()
    recursion_paths = [files[key] for key in sorted(direct) if key in files]
    return {
        "paths": paths,
        "direct": direct,
        "affected": affected,
        "tests": tests,
        "python_paths": python_paths,
        "recursion_paths": recursion_paths,
        "api_changed": api_changed,
        "catalog_changed": catalog_changed,
    }


def run_step(label, command):
    print(f"\n== {label} ==", flush=True)
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=REPOSITORY)
    elapsed = time.perf_counter() - started
    if completed.returncode:
        raise SystemExit(completed.returncode)
    print(f"passed: {label} ({elapsed:.2f}s)", flush=True)


def print_plan(plan):
    print("changed files:")
    for path in plan["paths"]:
        print("  ", path)
    if plan["affected"]:
        print("affected modules:")
        for key in sorted(plan["affected"]):
            suffix = " (changed)" if key in plan["direct"] else " (dependent)"
            print("  ", key + suffix)
    print("selected tests:")
    for path in sorted(plan["tests"]):
        print("  ", path.relative_to(ROOT).as_posix())
    if not plan["tests"]:
        print("   none")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="repository-relative changed files")
    parser.add_argument("--base", help="select files changed since this git revision")
    parser.add_argument("--list", action="store_true", help="show the selection without running it")
    parser.add_argument("--quick", action="store_true", help="run the checkpoint suite instead")
    parser.add_argument("--full", action="store_true", help="run the complete release suite instead")
    parser.add_argument("--benchmarks", action="store_true", help="add quick performance checks")
    args = parser.parse_args()

    if args.quick or args.full:
        command = [sys.executable, str(TOOLS / "check_library.py")]
        if args.full:
            command.extend(("--profile", "full"))
        raise SystemExit(subprocess.run(command, cwd=REPOSITORY).returncode)

    paths = changed_paths(args.base, args.paths)
    if not paths:
        print("No changed files. Use --base HEAD~1 to inspect the last commit.")
        return 0
    plan = plan_for(paths)
    print_plan(plan)
    if args.list:
        return 0

    if plan["python_paths"]:
        run_step(
            "changed Python syntax",
            [sys.executable, "-m", "py_compile", *map(str, plan["python_paths"])],
        )
    if plan["api_changed"]:
        run_step(
            "API reference synchronization",
            [sys.executable, str(TOOLS / "build_api_reference.py"), "--check"],
        )
    run_step(
        "library catalog synchronization",
        [sys.executable, str(TOOLS / "build_library_catalog.py"), "--check"],
    )
    if plan["recursion_paths"]:
        run_step(
            "changed-module recursion audit",
            [
                sys.executable,
                str(TOOLS / "audit_recursion.py"),
                *map(str, plan["recursion_paths"]),
            ],
        )
    if plan["tests"]:
        run_step(
            "affected tests",
            [sys.executable, "-m", "pytest", "-q", *map(str, sorted(plan["tests"]))],
        )
    if args.benchmarks:
        run_step(
            "quick performance regression",
            [sys.executable, str(TOOLS / "run_benchmarks.py"), "--profile", "quick"],
        )
    print("\nChanged-scope checks passed. Full checks were not run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
