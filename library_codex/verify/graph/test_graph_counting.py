import itertools
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.graph.GraphCounting import (  # noqa: E402
    chromatic_polynomial,
    count_directed_spanning_trees,
    count_eulerian_circuits,
    count_undirected_spanning_trees,
    evaluate_polynomial,
)


MOD = 998244353


def _graph(n, edges):
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    return graph


def _proper_colorings(n, edges, colors):
    answer = 0
    for assignment in itertools.product(range(colors), repeat=n):
        if all(assignment[u] != assignment[v] for u, v in edges):
            answer += 1
    return answer


def test_chromatic_polynomial_against_color_assignments():
    rng = random.Random(50)
    for n in range(7):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(40 if n <= 4 else 8):
            edges = [edge for edge in possible if rng.randrange(2)]
            coefficients = chromatic_polynomial(_graph(n, edges), MOD)
            assert len(coefficients) == n + 1
            for colors in range(n + 2):
                assert evaluate_polynomial(coefficients, colors, MOD) == (
                    _proper_colorings(n, edges, colors) % MOD
                )


def _connected(n, undirected_edges):
    if n == 0:
        return True
    graph = [[] for _ in range(n)]
    for u, v in undirected_edges:
        graph[u].append(v)
        graph[v].append(u)
    seen = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for to in graph[v]:
            if to not in seen:
                seen.add(to)
                stack.append(to)
    return len(seen) == n


def test_undirected_spanning_tree_weighted_against_subsets():
    rng = random.Random(51)
    for n in range(1, 8):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(300):
            rng.shuffle(possible)
            edges = [(u, v, rng.randrange(1, 6))
                     for u, v in possible[:rng.randrange(min(10, len(possible)) + 1)]]
            expected = 0
            for selected in itertools.combinations(range(len(edges)), n - 1):
                if _connected(n, [(edges[i][0], edges[i][1]) for i in selected]):
                    product = 1
                    for i in selected:
                        product *= edges[i][2]
                    expected += product
            assert count_undirected_spanning_trees(n, edges) == expected % MOD


def _directed_tree(n, root, edges, selected, toward):
    graph = [[] for _ in range(n)]
    for edge_id in selected:
        u, v, _ = edges[edge_id]
        if toward:
            graph[u].append(v)
        else:
            graph[v].append(u)
    for start in range(n):
        seen = set()
        v = start
        while v != root and v not in seen and len(graph[v]) == 1:
            seen.add(v)
            v = graph[v][0]
        if v != root:
            return False
    return True


def test_directed_spanning_tree_both_orientations():
    rng = random.Random(52)
    for n in range(1, 7):
        possible = [(u, v) for u in range(n) for v in range(n) if u != v]
        for _ in range(350):
            rng.shuffle(possible)
            edges = [(u, v, rng.randrange(1, 5))
                     for u, v in possible[:rng.randrange(min(10, len(possible)) + 1)]]
            root = rng.randrange(n)
            for toward in (False, True):
                expected = 0
                for selected in itertools.combinations(range(len(edges)), n - 1):
                    oriented = edges if toward else [(v, u, w) for u, v, w in edges]
                    if _directed_tree(n, root, oriented, selected, True):
                        product = 1
                        for i in selected:
                            product *= edges[i][2]
                        expected += product
                assert count_directed_spanning_trees(
                    n, edges, root, toward
                ) == expected % MOD


def test_eulerian_circuit_best_theorem_cases():
    assert count_eulerian_circuits(5, []) == 1
    assert count_eulerian_circuits(3, [(0, 1), (1, 2), (2, 0)]) == 1
    assert count_eulerian_circuits(2, [(0, 1, 2), (1, 0, 2)]) == 2
    assert count_eulerian_circuits(2, [(0, 1, 2), (1, 0, 1)]) == 0
    # Complete directed graph on 3 vertices: t_root=3, product(1!)=1.
    edges = [(u, v) for u in range(3) for v in range(3) if u != v]
    assert count_eulerian_circuits(3, edges, 0) == 3
