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
    assert data["schemaVersion"] == 2
    assert data["textFormat"] == "markdown+tex"
    assert data["sourceRevision"]
    assert len(data["sourceFingerprint"]) == 64
    assert data["stats"]["modules"] == len(data["modules"])
    assert data["stats"]["articles"] == sum(
        module["article"] is not None for module in data["modules"]
    )
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
        if module["article"] is not None:
            assert module["article"]["title"]
            assert "## 主な機能" in module["article"]["markdown"]
            assert module["article"]["sourcePath"].startswith(
                "library_codex/docs/articles/"
            )
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


def test_authored_articles_cover_new_modules_and_reference_examples():
    CATALOG.load_configuration(ROOT)
    documents = CATALOG.validate_article_coverage(ROOT)
    assert ("range_query", "WeightedWaveletMatrix") in documents
    assert ("range_query", "StaticRangeDistinct") in documents
    assert ("graph_connectivity", "BridgeForest") in documents
    assert ("tree", "AuxiliaryTree") in documents
    assert ("tree", "CentroidDecomposition") in documents

    data = load_catalog()
    articles = {
        module["name"]: module["article"]
        for module in data["modules"] if module["article"] is not None
    }
    assert "original_vertices[i]" in articles["AuxiliaryTree"]["markdown"]
    assert "tree = [[1, 2], [0, 3, 4], [0], [1], [1]]" in articles["AuxiliaryTree"]["markdown"]
    assert "## 返り値\n\n- `original_vertices[i]`" in articles["AuxiliaryTree"]["markdown"]
    assert "## 注意点\n\n- " in articles["AuxiliaryTree"]["markdown"]
    assert "CentroidDistanceFenwick" in articles["CentroidDecomposition"]["markdown"]
    assert "独立したfunctionが一つ、classが二つ" in articles["CentroidDecomposition"]["markdown"]
    assert "subclassではありません" in articles["CentroidDecomposition"]["markdown"]
    assert "目的の異なる三つの入口" not in articles["CentroidDecomposition"]["markdown"]
    assert "range_sum" in articles["WeightedWaveletMatrix"]["markdown"]


def test_article_returns_and_notes_use_bullets(tmp_path):
    article = tmp_path / "Example.md"
    article.write_text(
        "# Example\n\n## 主な機能\n\n説明。\n\n## 返り値\n\n文章で連結する。\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="must use bullets"):
        CATALOG.parse_article(article)

    article.write_text(
        "# Example\n\n## 主な機能\n\nこのmoduleには目的の異なる三つの入口があります。\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="ambiguous API entry phrase"):
        CATALOG.parse_article(article)


def test_centroid_decomposition_classes_have_distinct_roles():
    data = load_catalog()
    module = module_by_path(data, "library_codex.tree.CentroidDecomposition")
    classes = {item["name"]: item for item in module["classes"]}

    decomposition = classes["CentroidDecomposition"]
    distance_query = classes["CentroidDistanceFenwick"]
    assert "頂点値の更新や総和は扱わない" in decomposition["description"]
    assert "内部隣接list" in next(
        method for method in decomposition["methods"] if method["name"] == "add_edge"
    )["returnDescription"]
    assert "点更新" in distance_query["description"]


def test_catalog_has_precise_group_middle_product_and_half_open_range_details():
    data = load_catalog()

    group = module_by_path(data, "library_codex.algorithm.PermutationGroup")
    simplify = next(
        item for item in group["functions"]
        if item["name"] == "simplify_permutation_subgroup"
    )
    assert simplify["returnFormat"] == "list[list[list[int]]]"
    assert "level長が[0, 2, 3]" in simplify["returnDescription"]

    middle = module_by_path(data, "library_codex.convolution.MiddleProduct")
    assert middle["functions"][0]["signature"] == (
        "middle_product(first, second, mod=DEFAULT_MOD)"
    )
    assert r"c[i]=\sum_{j=0}^{m-1}" in middle["functions"][0]["returnDescription"]

    ranges = module_by_path(data, "library_codex.ordered_set.RangeSet")
    methods = {
        method["name"]: method
        for class_item in ranges["classes"]
        for method in class_item["methods"]
    }
    assert "半開区間" in methods["add"]["description"]
    assert "数学的な開区間を意味しない" in methods["intervals"]["returnDescription"]
    assert "整数の個数ではない" in methods["__len__"]["returnDescription"]

    all_symbols = [
        symbol
        for module in data["modules"]
        for symbol in module["functions"] + [
            method
            for class_item in module["classes"]
            for method in class_item["methods"]
        ]
    ]
    assert all(
        symbol["complexity"] != "各操作の計算量はAPI表を参照"
        for symbol in all_symbols
    )
    assert all(symbol["complexity"] != "実装依存" for symbol in all_symbols)
    assert all(
        "数値または入力要素型" not in symbol["returnDescription"]
        for symbol in all_symbols
    )
    assert all(
        symbol["returnDescription"] not in {
            "上記の処理結果。",
            "このAPIの結果を呼び出し順・添字順に格納したリスト。",
        }
        for symbol in all_symbols
    )


def test_integer_utilities_and_bit_use_the_new_public_api_only():
    data = load_catalog()
    integers = module_by_path(data, "library_codex.algorithm.IntegerUtilities")
    assert [item["name"] for item in integers["functions"]] == ["integer_nth_root"]

    bit = module_by_path(data, "library_codex.fenwick_tree.BIT")
    bit_class = next(item for item in bit["classes"] if item["name"] == "BIT")
    method_names = {item["name"] for item in bit_class["methods"]}
    assert {"add", "prefix_sum", "sum", "get", "set", "lower_bound"} <= method_names
    assert {"sum0", "prod", "bisect_left"}.isdisjoint(method_names)
    assert not any(
        module["modulePath"] == "library_codex.fenwick_tree.FenwickTree"
        for module in data["modules"]
    )


def test_accelerated_modules_publish_the_new_api_and_complexities():
    data = load_catalog()

    polynomial = module_by_path(data, "library_codex.polynomial.PolynomialGCD")
    polynomial_functions = {
        item["name"]: item for item in polynomial["functions"]
    }
    assert "Half-GCD" in polynomial_functions["polynomial_gcd"]["complexity"]
    extended = polynomial_functions["polynomial_extended_gcd"]
    assert extended["returnFormat"] == "tuple[list[int], list[int], list[int]]"
    assert [part["name"] for part in extended["returnParts"]] == ["g", "s", "t"]

    resultant = module_by_path(
        data, "library_codex.polynomial.PolynomialResultant"
    )
    assert "Half-GCD" in resultant["functions"][0]["complexity"]

    sortable = module_by_path(
        data, "library_codex.segment_tree.SortableSegmentTree"
    )
    sortable_class = next(
        item for item in sortable["classes"]
        if item["name"] == "SortableSegmentTree"
    )
    assert "block_size" not in sortable_class["constructor"]
    sortable_methods = {
        item["name"]: item for item in sortable_class["methods"]
    }
    assert "set" not in sortable_methods
    assert sortable_methods["query"]["complexity"].startswith("O(log N)")
    assert sortable_methods["update"]["complexity"].startswith("O(log N)")

    kd_tree = module_by_path(data, "library_codex.spatial_structure.LazyKDTree")
    kd_class = next(
        item for item in kd_tree["classes"] if item["name"] == "LazyKDTree"
    )
    assert kd_class["constructorComplexity"].startswith("O(N log N)")


def test_catalog_contains_required_search_terms_and_lazy_boundaries():
    data = load_catalog()
    lazy = module_by_path(data, "library_codex.segment_tree.LazySegTree")
    fenwick = module_by_path(data, "library_codex.fenwick_tree.BIT")
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


def test_fps998_family_is_complete_and_isolated_from_generic_ntt():
    data = load_catalog()
    required = {
        "library_codex.convolution.NTT998": {
            "ntt", "intt", "multiply", "square",
        },
        "library_codex.fps998.FPS": {
            "shrink", "fps_add", "fps_sub", "fps_neg", "fps_diff",
            "fps_integral", "fps_eval", "fps_inv", "fps_log",
            "fps_exp", "fps_pow", "fps_sqrt", "fps_div",
            "taylor_shift", "fps_product",
        },
        "library_codex.polynomial.PolynomialDivision998": {
            "poly_div", "poly_mod", "poly_divmod",
        },
        "library_codex.fps998.Composition": {
            "fps_compose", "fps_compositional_inv",
        },
        "library_codex.fps998.PowerProjection": {
            "power_projection", "power_coefficient",
        },
        "library_codex.fps998.LinearRecurrence": {
            "berlekamp_massey", "bostan_mori",
            "linear_recurrence_nth", "nth_term",
        },
        "library_codex.fps998.SubsetSum": {
            "subset_sum", "multiset_sum",
        },
        "library_codex.fps998.NTT2D": {
            "ntt2d", "intt2d", "multiply2d",
        },
    }
    forbidden = (
        "def primitive_root",
        "def convolution_any_mod",
        "class NumberTheoreticTransform",
        "library_codex.convolution.NTT import",
    )
    for module_path, names in required.items():
        module = module_by_path(data, module_path)
        assert {item["name"] for item in module["functions"]} == names
        assert module["categoryLabel"] in {
            "畳み込み", "FPS (998244353)", "多項式",
        }
        assert not any(token in module["standaloneCode"] for token in forbidden)

    fps = module_by_path(data, "library_codex.fps998.FPS")
    namespace = {"__name__": "__fps998_standalone_test__"}
    exec(compile(fps["standaloneCode"], "<FPS998 standalone>", "exec"), namespace)
    inverse = namespace["fps_inv"]([1, 2, 3], 16)
    product = namespace["multiply"]([1, 2, 3], inverse)[:16]
    assert product == [1] + [0] * 15


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


def test_class_detail_metadata_rejects_removed_constructor_argument(monkeypatch):
    CATALOG.load_configuration(ROOT)
    monkeypatch.setattr(
        CATALOG,
        "CLASS_DETAILS_BY_SYMBOL",
        {
            ("optimization/LARSCH.py", "LARSCH"): {
                "argumentDescriptions": {"removed": "存在しない引数"},
            }
        },
    )
    with pytest.raises(ValueError, match="unknown constructor argument"):
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

    larsch = module_by_path(data, "library_codex.optimization.LARSCH")
    larsch_class = next(
        item for item in larsch["classes"] if item["name"] == "LARSCH"
    )
    constructor_arguments = {
        item["name"]: item["description"]
        for item in larsch_class["constructorArgumentDetails"]
    }
    assert "下三角行列" in constructor_arguments["value"]
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

    fenwick = module_by_path(data, "library_codex.fenwick_tree.BIT")
    fenwick_class = next(item for item in fenwick["classes"] if item["name"] == "BIT")
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


def test_internal_bundle_dependencies_are_catalog_inputs(monkeypatch):
    CATALOG.load_configuration(ROOT)
    gcd_source = ROOT / "polynomial" / "PolynomialGCD.py"
    gcd_doc = ROOT / "docs" / "api" / "polynomial" / "PolynomialGCD.md"
    half_gcd = ROOT / "polynomial" / "_HalfGCD.py"
    assert half_gcd in CATALOG.catalog_input_paths(ROOT)

    before = CATALOG.module_input_fingerprint(gcd_source, gcd_doc, ROOT)
    original_dependencies = CATALOG.internal_dependencies

    def replace_half_gcd(source_path, library_root):
        dependencies = original_dependencies(source_path, library_root)
        if source_path == gcd_source:
            dependencies.append(ROOT / "random" / "RandomGraph.py")
        return dependencies

    monkeypatch.setattr(CATALOG, "internal_dependencies", replace_half_gcd)
    after = CATALOG.module_input_fingerprint(gcd_source, gcd_doc, ROOT)
    assert after != before


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


def test_catalog_has_no_vague_public_api_descriptions():
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assert CATALOG.description_quality_issues(data) == []


def test_description_audit_detects_generic_return_and_tuple_parts():
    data = {
        "modules": [{
            "modulePath": "library_codex.example.Sample",
            "functions": [{
                "name": "query",
                "description": "指定した対象への問い合わせ結果を返す。",
                "returnFormat": "tuple[int, int]",
                "returnDescription": "指定した範囲の集計結果。",
            }],
            "classes": [],
        }],
    }
    reasons = {
        issue["reason"] for issue in CATALOG.description_quality_issues(data)
    }
    assert reasons == {"generic-purpose", "generic-return", "tuple-parts-missing"}
