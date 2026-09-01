import json
import re
import runpy
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_name_only_metadata_does_not_cross_module_boundaries():
    metadata = runpy.run_path(str(ROOT / "tools" / "api_metadata.py"))
    catalog = json.loads((ROOT / "library-catalog.json").read_text(encoding="utf-8"))
    modules_by_name = {}
    for module in catalog["modules"]:
        symbols = list(module["functions"])
        for class_item in module["classes"]:
            symbols.extend(class_item["methods"])
        for symbol in symbols:
            modules_by_name.setdefault(symbol["name"], set()).add(module["modulePath"])

    for field in ("PURPOSE_BY_NAME", "RETURN_DETAILS"):
        shared = metadata.get("SHARED_PURPOSE_NAMES", set()) if field == "PURPOSE_BY_NAME" else set()
        collisions = {
            name: sorted(modules_by_name[name])
            for name in metadata[field]
            if len(modules_by_name.get(name, ())) > 1
            and name not in shared
        }
        assert not collisions, (
            f"{field} contains names shared by multiple modules; "
            f"move them to API_DETAILS_BY_SYMBOL: {collisions}"
        )


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
        "包含関係はAPIの説明を参照",
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

    auxiliary = documents["docs/api/tree/AuxiliaryTree.md"]
    assert "(auxiliary, original_vertices)" in auxiliary
    assert "圧縮木の隣接リスト" in auxiliary
    assert "任意の頂点集合から圧縮木を繰り返し構築" in auxiliary

    centroid = documents["docs/api/tree/CentroidDecomposition.md"]
    assert r"\operatorname{dist}(\mathrm{vertex},u)" in centroid
    assert "add・setで更新" in centroid

    increasing = documents["docs/api/fps/IncreasingSequences.md"]
    assert "$\\mathrm{lower}_i \\le x_i < \\mathrm{upper}_i$" in increasing
    assert "位置 $i$ では $\\mathrm{lower}_i$ を含む" in increasing

    stirling = documents["docs/api/combinatorial_series/StirlingNumbers.md"]
    assert "$\\mathrm{result}[n]=c(n,\\mathrm{column})$" in stirling
    assert "求める最大の第1引数 $n$。この値を含む" in stirling

    combination = documents["docs/api/combinatorics/Combination.md"]
    assert r"$\binom{n}{k}" in combination

    min_plus = documents["docs/api/convolution/MinPlusConvolution.md"]
    assert r"$c_k=\min_{i+j=k}" in min_plus
    assert "minplus_conv_convex(first, second)" in min_plus
    assert "O(N+M)" in min_plus
    assert "O(len(first) * len(second))" not in min_plus

    fps = documents["docs/api/fps/FormalPowerSeries.md"]
    assert r"\pmod{x^{\mathrm{degree}}}" in fps

    fenwick = documents["docs/api/fenwick_tree/BIT.md"]
    assert r"\sum_{i=\mathrm{left}}^{\mathrm{right}-1}a_i" in fenwick

    segtree = documents["docs/api/segment_tree/SegTree.md"]
    assert r"\operatorname{op}(a_{\mathrm{left}}" in segtree

    assert "docs/api/algorithm/BasicAlgorithms.md" not in documents
    assert "docs/api/algorithm/MiscAlgorithms.md" not in documents
    assert "docs/api/random/Random.md" in documents
    assert all("| alias |" not in text for text in documents.values())
    assert all("## Module aliases" not in text for text in documents.values())
    assert all(
        "各操作の計算量はAPI表を参照" not in text
        for text in documents.values()
    )
    assert all(
        "| signature | 用途 | 引数 | 返り値 | 計算量 |" in text
        for text in documents.values()
        if "## Functions" in text
    )

    permutation_group = documents["docs/api/algorithm/PermutationGroup.md"]
    assert "list[list[list[int]]]" in permutation_group
    assert "level長が[0, 2, 3]" in permutation_group

    permutation_tree = documents["docs/api/algorithm/PermutationTree.md"]
    assert "list[tuple[int, int]]" in permutation_tree
    assert "permutation[left:right]の値集合が連続整数" in permutation_tree
    assert "構築 O(N log N) time・O(N) memory" in permutation_tree

    middle_product = documents["docs/api/convolution/MiddleProduct.md"]
    assert "middle_product(first, second, mod=DEFAULT_MOD)" in middle_product
    assert r"c[i]=\sum_{j=0}^{m-1}" in middle_product

    range_set = documents["docs/api/ordered_set/RangeSet.md"]
    assert r"$[\mathrm{left},\mathrm{right})$" in range_set
    assert "数学的な開区間を意味しない" in range_set
