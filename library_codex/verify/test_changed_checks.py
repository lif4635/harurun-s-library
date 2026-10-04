import importlib.util
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "check_changed.py"
SPEC = importlib.util.spec_from_file_location("check_changed", SCRIPT)
CHECK_CHANGED = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_CHANGED)


def relative_tests(plan):
    return {
        path.relative_to(ROOT).as_posix()
        for path in plan["tests"]
    }


def test_source_module_key_accepts_only_public_modules():
    assert CHECK_CHANGED.source_module_key(
        "library_codex/segment_tree/SegTree.py"
    ) == "segment_tree/SegTree"
    assert CHECK_CHANGED.source_module_key(
        "library_codex/verify/data_structure/test_debug_output.py"
    ) is None
    assert CHECK_CHANGED.source_module_key("README.md") is None


def test_codon_changes_select_native_regression():
    for path in ("library_codex/templates/codon_header.codon", "library_codex/convolution/NTT998.py"):
        assert "verify/test_codon.py" in relative_tests(CHECK_CHANGED.plan_for([path]))


def test_official_benchmark_changes_select_own_tests():
    for name in ("official_benchmark", "official_comparison", "library_checker"):
        selected = relative_tests(CHECK_CHANGED.plan_for(["library_codex/benchmarks/" + name + ".py"]))
        assert "verify/test_official_benchmark.py" in selected
        assert "verify/test_official_comparison.py" in selected


def test_library_checker_changes_select_runner_tests():
    for path in ("verify/library_checker/drivers/aplusb.py", "library_codex/tools/check_library_checker.py"):
        assert "verify/test_official_library_checker.py" in relative_tests(CHECK_CHANGED.plan_for([path]))


def test_segment_tree_change_selects_dependents_and_relevant_tests():
    plan = CHECK_CHANGED.plan_for(
        ["library_codex/segment_tree/SegTree.py"]
    )
    tests = relative_tests(plan)
    assert "segment_tree/SegTree" in plan["direct"]
    assert plan["direct"] <= plan["affected"]
    assert "verify/data_structure/test_basic_data_structures.py" in tests
    assert "verify/data_structure/test_debug_output.py" in tests
    assert "verify/test_api_reference.py" in tests
    assert "verify/test_library_catalog.py" in tests
    assert plan["recursion_paths"]


def test_catalog_metadata_change_selects_catalog_contract_test():
    plan = CHECK_CHANGED.plan_for(["library_codex/tools/api_metadata.py"])
    tests = relative_tests(plan)
    assert plan["catalog_changed"]
    assert "verify/test_library_catalog.py" in tests


def test_article_change_selects_catalog_contract_test():
    plan = CHECK_CHANGED.plan_for([
        "library_codex/docs/articles/tree/AuxiliaryTree.md"
    ])
    tests = relative_tests(plan)
    assert plan["catalog_changed"]
    assert "verify/test_library_catalog.py" in tests


def test_policy_change_does_not_select_the_full_suite():
    plan = CHECK_CHANGED.plan_for(["AGENTS.md"])
    tests = relative_tests(plan)
    assert tests == {
        "verify/test_changed_checks.py",
        "verify/test_contribution_guide.py",
    }
    assert not plan["affected"]
    assert not plan["api_changed"]


def test_changed_paths_ignores_line_ending_only_differences(monkeypatch, tmp_path):
    def git(*arguments):
        subprocess.run(["git", "-C", str(tmp_path), *arguments], check=True, capture_output=True)

    git("init")
    git("config", "core.autocrlf", "false")
    git("config", "core.safecrlf", "false")
    for name in ("same.py", "staged.py", "変更 file.py", "deleted.py"):
        (tmp_path / name).write_bytes(b"value = 1\n")
    git("add", ".")
    git("-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-m", "initial")
    (tmp_path / "same.py").write_bytes(b"value = 1\r\n")
    (tmp_path / "staged.py").write_bytes(b"value = 1\r\n")
    git("add", "staged.py")
    (tmp_path / "変更 file.py").write_bytes(b"value = 2\r\n")
    (tmp_path / "new file.py").write_bytes(b"")
    (tmp_path / "empty.py").write_bytes(b"")
    git("add", "empty.py")
    (tmp_path / "deleted.py").unlink()
    monkeypatch.setattr(CHECK_CHANGED, "REPOSITORY", tmp_path)
    expected = sorted(["変更 file.py", "new file.py", "empty.py", "deleted.py"])
    assert CHECK_CHANGED.changed_paths() == expected
    assert CHECK_CHANGED.changed_paths(base="HEAD") == expected
