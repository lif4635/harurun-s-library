import importlib.util
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


def test_changed_paths_ignores_line_ending_only_differences(monkeypatch):
    calls = []

    def fake_git_lines(*arguments):
        calls.append(arguments)
        return []

    monkeypatch.setattr(CHECK_CHANGED, "git_lines", fake_git_lines)
    assert CHECK_CHANGED.changed_paths() == []
    diff_calls = [call for call in calls if call[0] == "diff"]
    assert diff_calls
    assert all("--ignore-space-at-eol" in call for call in diff_calls)
