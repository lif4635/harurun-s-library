import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_api_reference_is_current():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "build_api_reference.py"), "--check"],
        cwd=ROOT.parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert result.returncode == 0, result.stdout


def test_api_reference_local_links():
    errors = []
    line_counts = {}
    for document in sorted((ROOT / "docs").rglob("*.md")):
        text = document.read_text(encoding="utf-8")
        for raw in re.findall(r"\]\(([^)]+)\)", text):
            if raw.startswith(("http://", "https://", "#")):
                continue
            path_text, _, anchor = raw.partition("#")
            target = (document.parent / path_text).resolve()
            if not target.exists():
                errors.append("%s: missing %s" % (document.relative_to(ROOT), raw))
                continue
            if anchor.startswith("L") and anchor[1:].isdigit():
                line = int(anchor[1:])
                if target not in line_counts:
                    with target.open(encoding="utf-8") as source:
                        line_counts[target] = sum(1 for _ in source)
                if not 1 <= line <= line_counts[target]:
                    errors.append(
                        "%s: invalid line %s (file has %d lines)"
                        % (document.relative_to(ROOT), raw, line_counts[target])
                    )
    assert not errors, "\n".join(errors[:30])


def test_api_reference_has_actionable_semantics():
    documents = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "docs" / "api").rglob("*.md"))
        if path.name != "README.md"
    }
    assert documents
    assert all("## できること" in text for text in documents.values())

    forbidden = (
        "を実行する。",
        "を計算して返す。",
        "詳細はclass/moduleの説明に従う。",
        "APIの文脈に従う",
    )
    errors = []
    for path, text in documents.items():
        for phrase in forbidden:
            if phrase in text:
                errors.append("%s: contains %s" % (path, phrase))
    assert not errors, "\n".join(errors[:30])

    csr = documents["docs/api/graph/CSRGraph.md"]
    assert "tuple[list[number], list[int]]" in csr
    assert "iterator[tuple[int, number, int]]" in csr
    assert "tuple[list[int], list[list[int]]]" in csr

    factorization = documents["docs/api/prime/Factorization.md"]
    assert "64-bit確率的分解" not in factorization
    assert "素数判定 O(log N)" in factorization
    assert "期待 O(N^(1/4) log N)" in factorization
    assert "dict[int, int]" in factorization
    assert "list[int] — 素因数を重複込み" in factorization
