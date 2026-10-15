import random
import pytest
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.tree.TreeDistanceFrequency import (  # noqa: E402
    tree_distance_counts, _histogram_square,
)


def _brute(tree):
    n = len(tree)
    answer = [0] * n
    for start in range(n):
        distance = [-1] * n
        distance[start] = 0
        queue = [start]
        for v in queue:
            for to in tree[v]:
                if distance[to] == -1:
                    distance[to] = distance[v] + 1
                    queue.append(to)
        for target in range(start + 1, n):
            answer[distance[target]] += 1
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return answer


def test_tree_distance_frequency_against_all_pairs_bfs():
    rng = random.Random(60)
    for n in range(1, 100):
        for _ in range(5):
            tree = [[] for _ in range(n)]
            for v in range(1, n):
                parent = rng.randrange(v)
                tree[v].append(parent)
                tree[parent].append(v)
            expected = _brute(tree)
            actual = tree_distance_counts(tree)
            assert actual == expected
            with_same = expected[:]
            with_same[0] = n
            assert tree_distance_counts(tree, True) == with_same


def test_tree_distance_frequency_deep_path_nonrecursive():
    n = 10_000
    tree = [[] for _ in range(n)]
    for v in range(1, n):
        tree[v].append(v - 1)
        tree[v - 1].append(v)
    answer = tree_distance_counts(tree)
    assert len(answer) == n
    assert answer[0] == 0
    for distance in (1, 2, 17, n // 2, n - 1):
        assert answer[distance] == n - distance


def test_empty_star_and_invalid_graphs():
    assert tree_distance_counts([]) == []
    assert tree_distance_counts([[]]) == [0]
    assert tree_distance_counts([[]], True) == [1]
    n = 100000
    tree = [list(range(1, n))] + [[0] for _ in range(n - 1)]
    assert tree_distance_counts(tree) == [0, n - 1, (n - 1) * (n - 2) // 2]
    for graph in ([[1], [0], []], [[1, 2], [0, 2], [0, 1], []]):
        with pytest.raises(ValueError):
            tree_distance_counts(graph)


def test_histogram_single_two_and_three_prime_paths():
    rng = random.Random(3112)
    for scale in (1, 100000, 10 ** 10):
        values = [rng.randrange(10) * scale for _ in range(70)]
        expected = [0] * (2 * len(values) - 1)
        for i, a in enumerate(values):
            for j, b in enumerate(values):
                expected[i + j] += a * b
        assert _histogram_square(values) == expected
