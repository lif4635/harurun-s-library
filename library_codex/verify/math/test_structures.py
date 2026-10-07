import itertools
import math
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.algebra.Affine import Affine  # noqa: E402
from library_codex.game.GrundyNumbers import grundy_numbers  # noqa: E402


def test_affine_composition():
    rng = random.Random(120)
    for mod in (None, 998244353):
        for _ in range(10_000):
            left = Affine(rng.randrange(-100, 101), rng.randrange(-100, 101), mod)
            right = Affine(rng.randrange(-100, 101), rng.randrange(-100, 101), mod)
            value = rng.randrange(-100, 101)
            assert (left * right)(value) == right(left(value))


def test_grundy_numbers_random_dag():
    rng = random.Random(123)
    for n in range(100):
        for _ in range(20):
            graph = [[] for _ in range(n)]
            for u in range(n):
                for v in range(u + 1, n):
                    if rng.randrange(20) == 0:
                        graph[u].append(v)
            grundy = grundy_numbers(graph)
            for v in range(n - 1, -1, -1):
                reachable = {grundy[to] for to in graph[v]}
                expected = 0
                while expected in reachable:
                    expected += 1
                assert grundy[v] == expected
    assert grundy_numbers([[1], [0]]) is None
