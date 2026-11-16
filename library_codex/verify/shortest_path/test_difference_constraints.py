import random

import pytest

from library_codex.shortest_path.DifferenceConstraints import DifferenceConstraints


def test_against_floyd_warshall():
    rng = random.Random(7192)
    for n in range(1, 9):
        for _ in range(100):
            system = DifferenceConstraints(n)
            edges = [(rng.randrange(n + 1), rng.randrange(n + 1), rng.randrange(-5, 10)) for _ in range(rng.randrange(25))]
            inf = float("inf")
            distance = [[0 if u == v else inf for v in range(n + 1)] for u in range(n + 1)]
            for u, v, weight in edges:
                system.add(None if u == n else u, None if v == n else v, weight)
                distance[u][v] = min(distance[u][v], weight)
            for k in range(n + 1):
                for u in range(n + 1):
                    for v in range(n + 1):
                        distance[u][v] = min(distance[u][v], distance[u][k] + distance[k][v])
            feasible = all(distance[v][v] >= 0 for v in range(n + 1))
            values = system.solve()
            assert (values is not None) == feasible
            assert system.solve() == values
            if not feasible:
                with pytest.raises(ValueError):
                    system.bounds()
                continue
            assert all((values + [0])[v] - (values + [0])[u] <= weight for u, v, weight in edges)
            for source in range(n + 1):
                bounds = system.bounds(None if source == n else source)
                assert bounds == [(None if distance[v][source] == inf else -distance[v][source], None if distance[source][v] == inf else distance[source][v]) for v in range(n)]


def test_fix_range_invalidation_and_debug():
    system = DifferenceConstraints(3)
    system.add(0, 1, 5, lower=2)
    system.fix(0, 10)
    system.add(1, 2, 3)
    assert system.bounds() == [(10, 10), (12, 15), (None, 18)]
    assert system.bounds(0) == [(0, 0), (2, 5), (None, 8)]
    old = system.solve()
    old[0] = -100
    assert system.solve()[0] == 10
    assert str(system) == str(system.items())
    assert repr(system).startswith("DifferenceConstraints(n=3,")
    system.add(0, 1, 1)
    assert system.solve() is None
    assert DifferenceConstraints(0).solve() == []
    with pytest.raises(IndexError):
        system.fix(-1, 0)
    with pytest.raises(ValueError):
        DifferenceConstraints(-1)
