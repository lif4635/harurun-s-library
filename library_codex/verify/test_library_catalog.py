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


def test_atomic_write_preserves_previous_catalog_on_validation_failure(tmp_path):
    output = tmp_path / "library-catalog.json"
    output.write_text('{"known": "good"}\n', encoding="utf-8")
    before = output.read_bytes()
    with pytest.raises(ValueError, match="schemaVersion"):
        CATALOG.write_catalog_atomic(output, {"schemaVersion": -1}, ROOT)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))
