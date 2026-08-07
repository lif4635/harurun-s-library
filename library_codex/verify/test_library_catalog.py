import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "build_library_catalog.py"
CATALOG_PATH = ROOT / "library-catalog.json"
SPEC = importlib.util.spec_from_file_location("build_library_catalog", SCRIPT)
CATALOG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CATALOG)


def load_catalog():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def module_by_path(data, module_path):
    return next(module for module in data["modules"] if module["modulePath"] == module_path)


def test_library_catalog_is_current():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT.parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert result.returncode == 0, result.stdout


def test_catalog_schema_has_explicit_symbol_names_and_live_counts():
    data = load_catalog()
    assert data["schemaVersion"] == 1
    assert data["textFormat"] == "markdown+tex"
    assert data["sourceRevision"]
    assert len(data["sourceFingerprint"]) == 64
    assert data["stats"]["modules"] == len(data["modules"])
    assert data["stats"]["functions"] == sum(
        len(module["functions"]) for module in data["modules"]
    )
    assert data["stats"]["classes"] == sum(
        len(module["classes"]) for module in data["modules"]
    )
    assert data["stats"]["methods"] == sum(
        len(class_item["methods"])
        for module in data["modules"]
        for class_item in module["classes"]
    )
    for module in data["modules"]:
        assert module["name"]
        assert module["modulePath"]
        assert module["sourceCode"]
        assert module["standaloneCode"]
        for symbol in module["functions"]:
            assert symbol["name"]
            assert symbol["signature"].split("(", 1)[0] == symbol["name"]
        for class_item in module["classes"]:
            assert class_item["name"]
            assert class_item["constructor"]
            assert class_item["constructorCreates"]
            assert not class_item["constructorCreates"].startswith("初期化した ")
            for method in class_item["methods"]:
                assert method["name"]
                assert method["signature"].split("(", 1)[0] == method["name"]


def test_catalog_contains_required_search_terms_and_lazy_boundaries():
    data = load_catalog()
    lazy = module_by_path(data, "library_codex.segment_tree.LazySegTree")
    fenwick = module_by_path(data, "library_codex.fenwick_tree.FenwickTree")
    assert "遅延セグ木" in lazy["searchTerms"]
    assert "BIT" in fenwick["searchTerms"]
    lazy_class = next(item for item in lazy["classes"] if item["name"] == "LazySegTree")
    methods = {method["name"]: method for method in lazy_class["methods"]}
    assert {"max_right", "min_left"} <= set(methods)
    assert "右端二分探索" in methods["max_right"]["searchTerms"]
    assert "左端二分探索" in methods["min_left"]["searchTerms"]


def test_standalone_code_executes_without_library_imports():
    data = load_catalog()
    lazy = module_by_path(data, "library_codex.segment_tree.LazySegTree")
    namespace = {"__name__": "__catalog_standalone_test__"}
    exec(compile(lazy["standaloneCode"], "<LazySegTree standalone>", "exec"), namespace)
    assert "LazySegTree" in namespace


def test_search_metadata_rejects_removed_module_and_symbol(monkeypatch):
    CATALOG.load_configuration(ROOT)
    monkeypatch.setattr(
        CATALOG,
        "SEARCH_TERMS_BY_MODULE",
        {"segment_tree/Removed.py": ("removed",)},
    )
    with pytest.raises(ValueError, match="unknown module"):
        CATALOG.validate_search_metadata(ROOT)

    monkeypatch.setattr(CATALOG, "SEARCH_TERMS_BY_MODULE", {})
    monkeypatch.setattr(
        CATALOG,
        "SEARCH_TERMS_BY_SYMBOL",
        {("segment_tree/LazySegTree.py", "removed_method"): ("removed",)},
    )
    with pytest.raises(ValueError, match="unknown symbol"):
        CATALOG.validate_search_metadata(ROOT)


def test_search_metadata_rejects_empty_and_duplicate_terms():
    with pytest.raises(ValueError, match="empty search term"):
        CATALOG.validate_term_sequence("example", ("",))
    with pytest.raises(ValueError, match="duplicate search terms"):
        CATALOG.validate_term_sequence("example", ("BIT", "bit"))


def test_api_detail_metadata_rejects_removed_symbol(monkeypatch):
    CATALOG.load_configuration(ROOT)
    monkeypatch.setattr(
        CATALOG,
        "API_DETAILS_BY_SYMBOL",
        {
            ("tree/AuxiliaryTree.py", "AuxiliaryTree", "removed"): {
                "description": "removed",
            }
        },
    )
    with pytest.raises(ValueError, match="unknown symbol"):
        CATALOG.validate_api_details_metadata(ROOT)


def test_api_detail_metadata_rejects_removed_argument(monkeypatch):
    CATALOG.load_configuration(ROOT)
    monkeypatch.setattr(
        CATALOG,
        "API_DETAILS_BY_SYMBOL",
        {
            ("fps/IncreasingSequences.py", None, "count_increasing_sequences"): {
                "argumentDescriptions": {"removed": "存在しない引数"},
            }
        },
    )
    with pytest.raises(ValueError, match="unknown argument"):
        CATALOG.validate_api_details_metadata(ROOT)


def test_catalog_preserves_markdown_math_and_exact_bounds():
    data = load_catalog()
    increasing = module_by_path(
        data, "library_codex.fps.IncreasingSequences"
    )
    count = increasing["functions"][0]
    assert "$\\mathrm{lower}_i \\le x_i" in count["description"]
    arguments = {
        item["name"]: item["description"] for item in count["argumentDetails"]
    }
    assert "含む" in arguments["lower"]
    assert "含まない" in arguments["upper"]
    assert "APIの説明を参照" not in count["arguments"]

    stirling = module_by_path(
        data, "library_codex.combinatorial_series.StirlingNumbers"
    )
    first_column = next(
        item for item in stirling["functions"]
        if item["name"] == "stirling_first_column"
    )
    assert "この値を含む" in first_column["arguments"]
    assert "$\\mathrm{result}[n]=c(n,\\mathrm{column})$" in (
        first_column["returnDescription"]
    )

    assert CATALOG.localize_prose(
        r"shiftした結果 $f(x+\mathrm{shift})$"
    ) == r"シフトした結果 $f(x+\mathrm{shift})$"


def test_structured_returns_and_constructor_capabilities_are_explicit():
    data = load_catalog()
    auxiliary = module_by_path(data, "library_codex.tree.AuxiliaryTree")
    auxiliary_class = next(
        item for item in auxiliary["classes"] if item["name"] == "AuxiliaryTree"
    )
    get = next(item for item in auxiliary_class["methods"] if item["name"] == "get")
    assert get["returnFormat"] == "(auxiliary, original_vertices)"
    assert [part["name"] for part in get["returnParts"]] == [
        "auxiliary",
        "original_vertices",
    ]
    assert "元の木の頂点番号" in get["returnParts"][1]["description"]

    centroid = module_by_path(data, "library_codex.tree.CentroidDecomposition")
    distance_fenwick = next(
        item
        for item in centroid["classes"]
        if item["name"] == "CentroidDistanceFenwick"
    )
    assert "add・set" in distance_fenwick["constructorCreates"]
    query = next(
        item for item in distance_fenwick["methods"] if item["name"] == "query"
    )
    assert query["returnFormat"] == "number"
    assert "\\operatorname{dist}(\\mathrm{vertex},u)" in query["returnDescription"]

    audited_paths = {
        issue["path"] for issue in CATALOG.description_quality_issues(data)
    }
    assert not any("AuxiliaryTree" in path for path in audited_paths)
    assert not any("CentroidDistanceFenwick" in path for path in audited_paths)


def test_math_descriptions_cover_common_library_families():
    data = load_catalog()

    combination = module_by_path(data, "library_codex.combinatorics.Combination")
    comb = next(item for item in combination["classes"] if item["name"] == "Comb")
    choose = next(item for item in comb["methods"] if item["name"] == "C")
    assert "$\\binom{n}{k}" in choose["description"]

    min_plus = module_by_path(data, "library_codex.convolution.MinPlusConvolution")
    min_plus_functions = {item["name"]: item for item in min_plus["functions"]}
    assert set(min_plus_functions) == {"minplus_conv", "minplus_conv_convex"}
    assert "$c_k=\\min_{i+j=k}" in min_plus_functions["minplus_conv"]["description"]
    assert min_plus_functions["minplus_conv"]["complexity"].startswith("O(A log(")
    assert min_plus_functions["minplus_conv_convex"]["complexity"] == "O(N+M)"
    assert "高速minplus" in min_plus["searchTerms"]
    assert "離散凸" in min_plus_functions["minplus_conv"]["argumentDetails"][1]["description"]

    fps = module_by_path(data, "library_codex.fps.FormalPowerSeries")
    inverse = next(item for item in fps["functions"] if item["name"] == "fps_inverse")
    assert "\\pmod{x^{\\mathrm{degree}}}" in inverse["returnDescription"]

    fenwick = module_by_path(data, "library_codex.fenwick_tree.FenwickTree")
    fenwick_class = next(item for item in fenwick["classes"] if item["name"] == "FenwickTree")
    range_sum = next(item for item in fenwick_class["methods"] if item["name"] == "sum")
    assert "\\sum_{i=\\mathrm{left}}^{\\mathrm{right}-1}a_i" in range_sum["returnDescription"]

    segtree = module_by_path(data, "library_codex.segment_tree.SegTree")
    segtree_class = next(item for item in segtree["classes"] if item["name"] == "SegTree")
    prod = next(item for item in segtree_class["methods"] if item["name"] == "prod")
    assert "$\\operatorname{op}(a_{\\mathrm{left}}" in prod["returnDescription"]

    assert all(
        not class_item["description"].endswith("を扱う。")
        for module in data["modules"]
        for class_item in module["classes"]
    )


def test_same_named_apis_keep_module_specific_meanings():
    data = load_catalog()

    composition = module_by_path(data, "library_codex.fps.PolynomialComposition")
    compose = next(item for item in composition["functions"] if item["name"] == "composition")
    assert compose["returnFormat"] == "list[int]"
    assert "$f(g(x))" in compose["description"]
    assert "total" not in compose["returnDescription"]

    hld = module_by_path(data, "library_codex.tree.HeavyLightDecomposition")
    hld_class = next(item for item in hld["classes"] if item["name"] == "HeavyLightDecomposition")
    hld_path = next(item for item in hld_class["methods"] if item["name"] == "path")
    assert hld_path["returnFormat"] == "list[tuple[int, int]]"
    assert "半開区間" in hld_path["returnDescription"]

    random_graph = module_by_path(data, "library_codex.random.RandomGraph")
    generator = next(
        item for item in random_graph["classes"]
        if item["name"] == "UndirectedGraphGenerator"
    )
    random_path = next(item for item in generator["methods"] if item["name"] == "path")
    assert random_path["returnFormat"] == "Graph"

    factorization = module_by_path(data, "library_codex.prime.Factorization")
    factor_count = next(
        item for item in factorization["functions"] if item["name"] == "factor_count"
    )
    sieve = module_by_path(data, "library_codex.prime.Sieve")
    linear_sieve = next(item for item in sieve["classes"] if item["name"] == "LinearSieve")
    sieve_factor_count = next(
        item for item in linear_sieve["methods"] if item["name"] == "factor_count"
    )
    assert factor_count["returnFormat"] == "dict[int, int]"
    assert sieve_factor_count["returnFormat"] == "list[tuple[int, int]]"


def test_stale_fingerprint_is_detected(monkeypatch, tmp_path):
    data = load_catalog()
    copied = tmp_path / "library-catalog.json"
    copied.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(
        CATALOG,
        "catalog_input_stamp",
        lambda paths, base: "1" * 64,
    )
    monkeypatch.setattr(
        CATALOG,
        "catalog_fingerprints",
        lambda library_root, documents: (
            "0" * 64,
            data["generatorFingerprint"],
        ),
    )
    with pytest.raises(ValueError, match="catalog is stale"):
        CATALOG.check_catalog(ROOT, copied)


def test_incremental_build_reparses_only_changed_module_and_dependents(
    monkeypatch, tmp_path
):
    data = load_catalog()
    copied = tmp_path / "library-catalog.json"
    copied.write_bytes(CATALOG_PATH.read_bytes())
    original_module_fingerprint = CATALOG.module_input_fingerprint

    def changed_combination(source_path, document_path, library_root):
        value = original_module_fingerprint(source_path, document_path, library_root)
        return "f" * 64 if source_path.name == "Combination.py" else value

    monkeypatch.setattr(CATALOG, "module_input_fingerprint", changed_combination)
    monkeypatch.setattr(
        CATALOG,
        "catalog_input_stamp",
        lambda paths, base: "d" * 64,
    )
    monkeypatch.setattr(
        CATALOG,
        "catalog_fingerprints",
        lambda library_root, documents: (
            "e" * 64,
            data["generatorFingerprint"],
        ),
    )
    rebuilt, reparsed = CATALOG.build_catalog(ROOT, copied)
    assert 0 < reparsed < len(rebuilt["modules"])
    changed = {
        (module["category"], module["name"])
        for module in rebuilt["modules"]
        if module["inputFingerprint"] == "f" * 64
    }
    assert changed == {("combinatorics", "Combination")}


def test_module_scoped_metadata_changes_only_its_fingerprint(monkeypatch):
    CATALOG.load_configuration(ROOT)
    auxiliary_source = ROOT / "tree" / "AuxiliaryTree.py"
    auxiliary_doc = ROOT / "docs" / "api" / "tree" / "AuxiliaryTree.md"
    combination_source = ROOT / "combinatorics" / "Combination.py"
    combination_doc = ROOT / "docs" / "api" / "combinatorics" / "Combination.md"
    before_auxiliary = CATALOG.module_input_fingerprint(
        auxiliary_source, auxiliary_doc, ROOT
    )
    before_combination = CATALOG.module_input_fingerprint(
        combination_source, combination_doc, ROOT
    )
    changed = dict(CATALOG.API_DETAILS_BY_SYMBOL)
    key = ("tree/AuxiliaryTree.py", "AuxiliaryTree", "get")
    changed[key] = dict(changed[key], description="changed for test")
    monkeypatch.setattr(CATALOG, "API_DETAILS_BY_SYMBOL", changed)
    assert CATALOG.module_input_fingerprint(
        auxiliary_source, auxiliary_doc, ROOT
    ) != before_auxiliary
    assert CATALOG.module_input_fingerprint(
        combination_source, combination_doc, ROOT
    ) == before_combination


def test_atomic_write_preserves_previous_catalog_on_validation_failure(tmp_path):
    output = tmp_path / "library-catalog.json"
    output.write_text('{"known": "good"}\n', encoding="utf-8")
    before = output.read_bytes()
    with pytest.raises(ValueError, match="schemaVersion"):
        CATALOG.write_catalog_atomic(output, {"schemaVersion": -1}, ROOT)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))
