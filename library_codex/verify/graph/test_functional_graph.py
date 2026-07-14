import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.graph.FunctionalGraph import FunctionalGraph


def orbit(to, s):
    pos = {}
    path = []
    u = s
    while u not in pos:
        pos[u] = len(path)
        path.append(u)
        u = to[u]
    return path, pos[u]


def brute_move(to, s, k):
    path, begin = orbit(to, s)
    if k < len(path):
        return path[k]
    return path[begin + (k - begin) % (len(path) - begin)]


def test_random():
    for n in range(1, 100):
        to = [random.randrange(n) for _ in range(n)]
        fg = FunctionalGraph(to)
        for s in range(n):
            path, begin = orbit(to, s)
            cycle = fg.get_cycle(s)
            assert fg.depth[s] == begin
            assert fg.root(s) == path[begin]
            assert fg.in_cycle(s) == (begin == 0)
            assert fg.cycle_size(s) == len(path) - begin
            assert fg.reachable_size(s) == len(path)
            assert set(cycle) == set(path[begin:])
            assert all(to[cycle[i]] == cycle[(i + 1) % len(cycle)] for i in range(len(cycle)))

            for k in (0, 1, n, n * 3 + 7, 10**18 + random.randrange(1000)):
                assert fg.move(s, k) == brute_move(to, s, k)

        for _ in range(500):
            u = random.randrange(n)
            v = random.randrange(n)
            path, _ = orbit(to, u)
            want = path.index(v) if v in path else -1
            assert fg.dist(u, v) == want


def test_long_path_without_recursion():
    n = 100000
    to = list(range(1, n)) + [n - 1]
    fg = FunctionalGraph(to)
    assert fg.depth[0] == n - 1
    assert fg.move(0, n - 2) == n - 2
    assert fg.move(0, 10**18) == n - 1
    assert fg.dist(0, n - 1) == n - 1
    assert fg.dist(n - 1, 0) == -1


if __name__ == "__main__":
    random.seed(0)
    test_random()
    test_long_path_without_recursion()
