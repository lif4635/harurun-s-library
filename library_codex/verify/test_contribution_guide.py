from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent


def test_contribution_contract_is_installed():
    agents = REPOSITORY / "AGENTS.md"
    guide = ROOT / "docs" / "CONTRIBUTING.md"
    pull_request = REPOSITORY / ".github" / "pull_request_template.md"

    assert agents.is_file()
    assert guide.is_file()
    assert pull_request.is_file()

    agent_text = agents.read_text(encoding="utf-8")
    guide_text = guide.read_text(encoding="utf-8")
    pull_request_text = pull_request.read_text(encoding="utf-8")
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in (
        "library_codex/docs/CONTRIBUTING.md",
        "1モジュール",
        "非可換",
        "tolist()",
        "items()",
        "check_changed.py",
        "check_library.py --profile full",
    ):
        assert phrase in agent_text

    for phrase in (
        "返り値の型と形式",
        "methodごとの時間計算量",
        "randomized test",
        "通常のPythonコード",
        "差分検査",
        "library-catalog.json",
        "SEARCH_TERMS_BY_MODULE",
        "build_library_catalog.py --check",
        "## 完了チェックリスト",
    ):
        assert phrase in guide_text

    assert "docs/CONTRIBUTING.md" in readme_text
    assert "tools/check_changed.py" in readme_text
    assert "データ構造なら`tolist()`または`items()`" in pull_request_text
    assert "tools/check_changed.py" in pull_request_text
