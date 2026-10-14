from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent


def test_contribution_contract_is_installed():
    agents = REPOSITORY / "AGENTS.md"
    guide = ROOT / "docs" / "CONTRIBUTING.md"
    page_guide = ROOT / "docs" / "PAGE_CONTENT_GUIDE.md"
    pull_request = REPOSITORY / ".github" / "pull_request_template.md"

    assert agents.is_file()
    assert guide.is_file()
    assert page_guide.is_file()
    assert pull_request.is_file()

    agent_text = agents.read_text(encoding="utf-8")
    guide_text = guide.read_text(encoding="utf-8")
    page_guide_text = page_guide.read_text(encoding="utf-8")
    article_readme_text = (
        ROOT / "docs" / "articles" / "README.md"
    ).read_text(encoding="utf-8")
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
        "PAGE_CONTENT_GUIDE.md",
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
        "create_module_article.py",
        "legacy_modules.txt",
        "短い配列例は一行",
        "## 完了チェックリスト",
    ):
        assert phrase in guide_text

    for phrase in (
        "包含関係は説明を参照",
        "自明な0-indexed注記",
        "API_DETAILS_BY_SYMBOL.argumentDescriptions",
        "markdown+tex",
        "サイトだけの説明上書きがない",
        "ページ内容チェックリスト",
        "docs/articles/<category>/<Module>.md",
        "一つの長い段落にせず",
        "一項目一判断",
        "短い配列・辺list・隣接listは一行",
        "独立したfunction、別々のclass、同じclassのmethod",
        "signatureを同じ位置から始め",
        "否定形の補足を重ねない",
        "複数の入口",
        "現在の標準構成",
        "signatureを先頭へ揃え",
        "`vertex: 頂点番号`のような説明は原則省き",
        "各function・constructor・methodに置きます",
    ):
        assert phrase in page_guide_text

    assert "種別はsignatureの後ろ" in article_readme_text
    assert "PAGE_CONTENT_GUIDE.md" in article_readme_text

    assert "docs/CONTRIBUTING.md" in readme_text
    assert "tools/check_changed.py" in readme_text
    assert "データ構造なら`tolist()`または`items()`" in pull_request_text
    assert "tools/check_changed.py" in pull_request_text


def test_readme_local_links():
    paths = [
        REPOSITORY / "README.md",
        ROOT / "README.md",
        REPOSITORY / "verify" / "library_checker" / "README.md",
        ROOT / "docs" / "BENCHMARKS.md",
    ]
    for path in paths:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if target.startswith(("https://", "http://", "#")):
                continue
            assert (path.parent / target.split("#")[0]).exists(), (path, target)


def test_readme_python_example():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    examples = re.findall(r"```python\n(.*?)```", text, re.S)
    assert len(examples) == 1
    result = subprocess.run(
        [sys.executable, "-c", examples[0]], cwd=REPOSITORY,
        text=True, capture_output=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["10", "6"]
