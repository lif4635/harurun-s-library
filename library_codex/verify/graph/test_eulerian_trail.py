import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.EulerianTrail import (
    eulerian_cycle,
    eulerian_trail,
    eulerian_trails,
)


def brute_exists(n, edges, directed):
    m = len(edges)
    if m == 0:
        return True
    states = {(0, v) for v in range(n)}
    for _ in range(m):
        nxt = set()
        for mask, u in states:
            for eid, (a, b) in enumerate(edges):
                if mask >> eid & 1:
                    continue
                if a == u:
                    nxt.add((mask | 1 << eid, b))
                if not directed and b == u:
                    nxt.add((mask | 1 << eid, a))
        states = nxt
    return bool(states)


def validate(edges, directed, result, all_edges=True):
    vertices, trail = result
    assert len(vertices) == len(trail) + 1
    assert len(set(trail)) == len(trail)
    assert all(0 <= eid < len(edges) for eid in trail)
    if all_edges:
        assert sorted(trail) == list(range(len(edges)))
    for u, v, eid in zip(vertices, vertices[1:], trail):
        a, b = edges[eid]
        if directed:
            assert (u, v) == (a, b)
        else:
            assert (u, v) == (a, b) or (u, v) == (b, a)


def test_exhaustive_random():
    for directed in (False, True):
        for n in range(1, 6):
            for _ in range(2000):
                m = random.randrange(9)
                edges = [(random.randrange(n), random.randrange(n)) for _ in range(m)]
                result = eulerian_trail(n, edges, directed)
                assert (result is not None) == brute_exists(n, edges, directed)
                if result is not None:
                    validate(edges, directed, result)
                    cycle = eulerian_cycle(n, edges, directed)
                    assert (cycle is not None) == (result[0][0] == result[0][-1])


def test_start_and_disconnected():
    edges = [(0, 1), (1, 2)]
    assert eulerian_trail(3, edges, True, 1) is None
    validate(edges, True, eulerian_trail(3, edges, True, 0))
    assert eulerian_trail(4, [(0, 1), (2, 3)], False) is None
    assert eulerian_trail(0, [], False) == ([], [])
    assert eulerian_cycle(0, [], False) == ([], [])

    edges = [(0, 1), (2, 3)]
    trails = eulerian_trails(5, edges, False)
    assert len(trails) == 2
    used = []
    for result in trails:
        validate(edges, False, result, False)
        used.extend(result[1])
    assert sorted(used) == [0, 1]
    assert eulerian_trails(3, [(0, 1), (0, 2), (1, 2)], False) is not None
    assert eulerian_trails(4, [(0, 1), (0, 2), (0, 3)], False) is None


def test_large_without_recursion():
    n = 200000
    edges = [(i, i + 1) for i in range(n - 1)]
    result = eulerian_trail(n, edges, True)
    assert result[0] == list(range(n))
    assert result[1] == list(range(n - 1))


if __name__ == "__main__":
    random.seed(0)
    test_exhaustive_random()
    test_start_and_disconnected()
    test_large_without_recursion()
