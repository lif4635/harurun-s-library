import json
from pathlib import Path
import random
import re

import pytest

from library_codex.graph_connectivity.OfflineDynamicSum import OfflineDynamicSum


def component(graph, start):
    seen = {start}
    stack = [start]
    while stack:
        for v in graph[stack.pop()]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def test_random_graph_updates_and_component_additions():
    for seed in range(16):
        rng = random.Random(seed)
        n = 1 + seed
        values = [rng.randrange(-100, 101) for _ in range(n)]
        solver = OfflineDynamicSum(values)
        graph = [set() for _ in range(n)]
        expected = []
        for step in range(900):
            u, v = rng.randrange(n), rng.randrange(n)
            kind = rng.randrange(5)
            if kind < 2:
                if v in graph[u]:
                    solver.remove_edge(u, v)
                    graph[u].discard(v)
                    graph[v].discard(u)
                else:
                    solver.add_edge(u, v)
                    graph[u].add(v)
                    graph[v].add(u)
            elif kind == 2:
                delta = rng.randrange(-100, 101)
                solver.add(u, delta)
                values[u] += delta
            elif kind == 3:
                delta = rng.randrange(-100, 101)
                solver.add_component(u, delta)
                for vertex in component(graph, u):
                    values[vertex] += delta
            else:
                assert solver.query(u) == len(expected)
                expected.append(sum(values[vertex] for vertex in component(graph, u)))
            if step in (0, 127, 512, 899):
                assert solver.solve() == expected
        assert solver.solve() == solver.solve() == expected


def test_pending_component_add_survives_splits_and_rejoins():
    solver = OfflineDynamicSum([1, 2, 3, 4])
    solver.add_edge(0, 1)
    solver.add_edge(1, 2)
    solver.add_edge(2, 0)
    solver.add_component(0, 10)
    solver.remove_edge(1, 2)
    solver.query(2)
    solver.remove_edge(0, 2)
    solver.add(2, -5)
    solver.query(2)
    solver.add_component(0, 100)
    solver.query(1)
    solver.add_edge(2, 3)
    solver.query(3)
    solver.add_edge(0, 3)
    solver.query(2)
    assert solver.solve() == [36, 8, 223, 12, 235]


def test_empty_invalid_and_non_power_of_two_event_counts():
    assert OfflineDynamicSum([]).solve() == []
    solver = OfflineDynamicSum([0, 1])
    with pytest.raises(IndexError):
        solver.query(-1)
    with pytest.raises(IndexError):
        solver.add_edge(0, 2)
    with pytest.raises(ValueError):
        solver.remove_edge(0, 1)
    solver.add_edge(0, 1)
    with pytest.raises(ValueError):
        solver.add_edge(1, 0)
    assert solver.solve() == []
    solver.remove_edge(1, 0)
    for count in range(1, 36):
        solver.query(0)
        assert solver.solve() == [0] * count
    solver.add_component(1, 10**80)
    solver.query(1)
    assert solver.solve()[-1] == 10**80 + 1


def test_offline_dynamic_sum_catalog_and_article():
    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / "library-catalog.json").read_text())
    module = next(m for m in data["modules"] if m["modulePath"] == "library_codex.graph_connectivity.OfflineDynamicSum")
    assert module["bundledDependencies"] == []
    namespace = {}
    exec(module["standaloneCode"], namespace)
    graph = namespace["OfflineDynamicSum"]([3])
    graph.query(0)
    assert graph.solve() == [3]
    for example in re.findall(r"```python\n(.*?)\n```", module["article"]["markdown"], re.S):
        exec(example, {})
