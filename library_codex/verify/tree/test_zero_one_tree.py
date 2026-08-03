import itertools
import random
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
