import itertools
import random
import pytest
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.tree.ZeroOneTree import (  # noqa: E402
    min_block_inversions,
    min_inversions,
)


def _brute(parent, blocks):
    size = len(parent)
    answer = 10**30
    for order in itertools.permutations(range(size)):
        position = [0] * size
        for index, vertex in enumerate(order):
            position[vertex] = index
        if any(position[parent[vertex]] > position[vertex]
               for vertex in range(1, size)):
            continue
        sequence = []
        for vertex in order:
            zero, one = blocks[vertex]
            sequence.extend([0] * zero)
            sequence.extend([1] * one)
        one_count = inversions = 0
        for value in sequence:
            if value:
                one_count += 1
            else:
                inversions += one_count
        answer = min(answer, inversions)
    return answer


def test_zero_one_tree_against_topological_orders():
    rng = random.Random(413)
    for size in range(1, 9):
        for _ in range(25):
            parent = [0] + [rng.randrange(vertex) for vertex in range(1, size)]
            labels = [rng.randrange(2) for _ in range(size)]
            blocks = [(label == 0, label == 1) for label in labels]
            assert min_inversions(parent, labels) == _brute(parent, blocks)


def test_zero_one_tree_weighted_blocks():
    parent = [0, 0, 0, 1, 1, 2]
    zero = [1, 0, 2, 1, 0, 2]
    one = [0, 2, 0, 1, 2, 1]
    blocks = list(zip(zero, one))
    assert min_block_inversions(parent, zero, one) == _brute(parent, blocks)


def _check_order(parent, zero, one, root=0):
    answer, order = min_block_inversions(parent, zero, one, root, return_order=True)
    assert sorted(order) == list(range(len(parent)))
    position = {vertex: i for i, vertex in enumerate(order)}
    assert all(vertex == root or position[parent[vertex]] < position[vertex]
               for vertex in range(len(parent)))
    score = total = 0
    for vertex in order:
        score += total * zero[vertex]
        total += one[vertex]
    assert score == answer
    assert min_block_inversions(parent, zero, one, root) == answer
    return answer


def test_weighted_order_with_zero_blocks():
    rng = random.Random(94107)
    for size in range(1, 8):
        for _ in range(20):
            parent = [0] + [rng.randrange(i) for i in range(1, size)]
            zero = [rng.randrange(3) for _ in range(size)]
            one = [rng.randrange(3) for _ in range(size)]
            before = parent[:], zero[:], one[:]
            assert _check_order(parent, zero, one) == _brute(parent, list(zip(zero, one)))
            assert before == (parent, zero, one)


def test_order_relabeling_large_counts_and_validation():
    parent = [2, 0, -1, 2, 3]
    zero = [0, 10**50, 0, 1, 0]
    one = [0, 0, 10**60, 2, 3]
    _check_order(parent, zero, one, 2)
    assert min_inversions([0, 0, 1], [1, 0, 1], return_order=True) == (1, [0, 1, 2])
    assert min_block_inversions([0], [0], [0], return_order=True) == (0, [0])
    with pytest.raises(ValueError):
        min_block_inversions([0, 2, 1], [1]*3, [1]*3)
    with pytest.raises(ValueError):
        min_block_inversions([0], [-1], [1])
    with pytest.raises(ValueError):
        min_block_inversions([0], [], [1])
    with pytest.raises(IndexError):
        min_block_inversions([0, 9], [1, 1], [1, 1])


def test_deep_tree_and_weightless_vertices():
    n = 20000
    parent = [0] + list(range(n-1))
    assert min_block_inversions(parent, [0]*n, [0]*n, return_order=True) == (0, list(range(n)))


def test_zero_block_comparator_regression():
    parent = [0, 0, 1, 0, 3]
    zero = [0, 1, 1, 0, 1]
    one = [0, 0, 1, 0, 0]
    assert _check_order(parent, zero, one) == _brute(parent, list(zip(zero, one))) == 0
