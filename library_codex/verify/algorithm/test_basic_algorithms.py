import itertools
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from algorithm.BasicAlgorithms import (  # noqa: E402
    Doubling,
    Mo,
    binary_search_int,
    coordinate_compress,
    fibonacci,
    inversion_count,
    knapsack_01_max,
    longest_increasing_subsequence,
    merge_intervals,
    subset_sum_possible,
    subset_sum_restore,
)


def test_fibonacci_and_binary_search():
    a, b = 0, 1
    for n in range(1000):
        assert fibonacci(n) == a
        assert fibonacci(n, 97) == a % 97
        a, b = b, a + b
    for target in range(-100, 101):
        assert binary_search_int(lambda x: x >= target, target - 1000,
                                 target + 1000) == target


def test_inversion_lis_against_subsequences():
    rng = random.Random(90)
    for n in range(11):
        for _ in range(300):
            values = [rng.randrange(-5, 6) for _ in range(n)]
            expected_inv = sum(values[i] > values[j]
                               for i in range(n) for j in range(i + 1, n))
            assert inversion_count(values) == expected_inv
            for strict in (False, True):
                expected = 0
                for mask in range(1 << n):
                    seq = [values[i] for i in range(n) if mask >> i & 1]
                    valid = all(seq[i] < seq[i + 1] if strict
                                else seq[i] <= seq[i + 1]
                                for i in range(len(seq) - 1))
                    if valid:
                        expected = max(expected, len(seq))
                length, indices, sequence = longest_increasing_subsequence(
                    values, strict, True
                )
                assert length == expected == len(indices) == len(sequence)
                assert sequence == [values[i] for i in indices]


def test_knapsack_and_subset_sum_against_subsets():
    rng = random.Random(91)
    for n in range(13):
        for _ in range(250):
            weights = [rng.randrange(11) for _ in range(n)]
            values = [rng.randrange(-10, 20) for _ in range(n)]
            capacity = rng.randrange(35)
            expected = max(
                sum(values[i] for i in range(n) if mask >> i & 1)
                for mask in range(1 << n)
                if sum(weights[i] for i in range(n) if mask >> i & 1) <= capacity
            )
            assert knapsack_01_max(weights, values, capacity) == expected
            target = rng.randrange(35)
            bits = subset_sum_possible(weights, target)
            possible = any(sum(weights[i] for i in range(n) if mask >> i & 1) == target
                           for mask in range(1 << n))
            assert bool(bits >> target & 1) == possible
            restored = subset_sum_restore(weights, target)
            assert (restored is not None) == possible
            if restored is not None:
                assert len(restored) == len(set(restored))
                assert sum(weights[i] for i in restored) == target


def test_mo_doubling_and_small_utilities():
    rng = random.Random(92)
    values = [rng.randrange(100) for _ in range(500)]
    queries = [(rng.randrange(501), rng.randrange(501)) for _ in range(2000)]
    queries = [(min(l, r), max(l, r)) for l, r in queries]
    mo = Mo(len(values), len(queries))
    for query in queries:
        mo.add_query(*query)
    current = 0
    add = lambda i: None
    # Closures using a box keep the callback path representative.
    box = [0]
    def add_value(i):
        box[0] += values[i]
    def remove_value(i):
        box[0] -= values[i]
    answer = mo.run(add_value, add_value, remove_value, remove_value,
                    lambda: box[0])
    assert answer == [sum(values[l:r]) for l, r in queries]

    successor = [rng.randrange(100) for _ in range(100)]
    weight = [rng.randrange(-10, 11) for _ in range(100)]
    doubling = Doubling(successor, 10_000, weight)
    for _ in range(3000):
        start = rng.randrange(100)
        steps = rng.randrange(10_001)
        vertex = start
        total = 0
        for _ in range(steps):
            total += weight[vertex]
            vertex = successor[vertex]
        assert doubling.jump(start, steps) == vertex
        assert doubling.jump_with_sum(start, steps) == (vertex, total)

    ordered, mapping = coordinate_compress([3, 1, 3, -2])
    assert ordered == [-2, 1, 3] and [mapping[x] for x in ordered] == [0, 1, 2]
    assert merge_intervals([(1, 3), (3, 5), (8, 9)]) == [(1, 5), (8, 9)]
    assert merge_intervals([(1, 3), (3, 5)], False) == [(1, 3), (3, 5)]
