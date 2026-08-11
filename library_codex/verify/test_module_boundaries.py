import ast
from pathlib import Path

from library_codex.tools.category_config import SOURCE_CATEGORIES


ROOT = Path(__file__).resolve().parents[1]
REMOVED_UMBRELLA_MODULES = {
    "convolution/AdvancedConvolution.py",
    "convolution/AdvancedSeries.py",
    "convolution/FPSWrappers.py",
    "convolution/PolynomialAlgorithms.py",
    "convolution/SeriesSequences.py",
    "data_structure/AdvancedCollections.py",
    "data_structure/AdvancedOrdered.py",
    "data_structure/AdvancedRangeStructures.py",
    "data_structure/Collections.py",
    "data_structure/IntRangeTree.py",
    "data_structure/LinearOptimization.py",
    "data_structure/RectangleQuery.py",
    "data_structure/SWAG.py",
    "game/GameTheory.py",
    "graph/ExpandedGraph.py",
    "graph/GraphEnumeration.py",
    "graph/GraphMatching.py",
    "graph/GraphOptimization.py",
    "graph/ShortestPath.py",
    "heuristic/Heuristics.py",
    "math/AlgebraExtras.py",
    "math/Combinatorics.py",
    "math/NumberTheoryExtras.py",
    "math/Structures.py",
    "optimization/AdvancedDP.py",
    "optimization/Optimization.py",
    "tree/TreeAlgorithms.py",
}


def test_module_boundaries_and_descriptions_are_reviewed():
    modules = {
        path.relative_to(ROOT).as_posix(): path
        for category in SOURCE_CATEGORIES
        for path in (ROOT / category).glob("*.py")
        if not path.name.startswith("_")
    }
    assert not (REMOVED_UMBRELLA_MODULES & modules.keys())

    segment_tree = ast.parse(modules["segment_tree/SegTree.py"].read_text(encoding="utf-8"))
    assert [node.name for node in segment_tree.body if isinstance(node, ast.ClassDef)] == ["SegTree"]

    union_find = ast.parse(modules["union_find/UnionFind.py"].read_text(encoding="utf-8"))
    assert [node.name for node in union_find.body if isinstance(node, ast.ClassDef)] == ["UnionFind"]

    dijkstra = ast.parse(modules["shortest_path/Dijkstra.py"].read_text(encoding="utf-8"))
    assert [
        node.name for node in dijkstra.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")
    ] == ["dijkstra"]


def test_source_categories_do_not_become_unbounded_catch_alls():
    counts = {
        category: sum(
            1 for path in (ROOT / category).glob("*.py")
            if not path.name.startswith("_")
        )
        for category in SOURCE_CATEGORIES
    }
    # 32 is a generous safety rail, not a target. Split a category when its
    # concepts become hard to scan; do not move a 21st module just for a count.
    assert max(counts.values()) <= 32, counts
