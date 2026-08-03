import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from library_codex.segment_tree.RangeAddAssignRangeStats import (
    INF,
    RangeAddAssignRangeStats,
)
from library_codex.segment_tree.RangeAffineRangeSum import RangeAffineRangeSum


def test_range_stats_random_against_list():
    rng = random.Random(8301)
    for n in (0, 1, 2, 3, 31, 32, 33, 100):
        values = [rng.randrange(-1000, 1001) for _ in range(n)]
        tree = RangeAddAssignRangeStats(values)
        for _ in range(5000):
            left = rng.randrange(n + 1)
            right = rng.randrange(left, n + 1)
            command = rng.randrange(9)
            if command == 0:
                value = rng.randrange(-1000, 1001)
                tree.range_add(left, right, value)
                values[left:right] = [item + value for item in values[left:right]]
            elif command == 1:
                value = rng.randrange(-1000, 1001)
                tree.range_assign(left, right, value)
                values[left:right] = [value] * (right - left)
            elif command == 2:
                assert tree.range_sum(left, right) == sum(values[left:right])
            elif command == 3:
                want = min(values[left:right]) if left < right else INF
                assert tree.range_min(left, right) == want
            elif command == 4:
                want = max(values[left:right]) if left < right else -INF
                assert tree.range_max(left, right) == want
            elif command == 5 and n:
                index = rng.randrange(n)
                value = rng.randrange(-1000, 1001)
                tree[index] = value
                values[index] = value
            elif command == 6 and n:
                index = rng.randrange(n)
                assert tree[index] == values[index]
            else:
                assert tree.all_sum() == sum(values)
                assert tree.all_min() == (min(values) if values else INF)
                assert tree.all_max() == (max(values) if values else -INF)


def test_affine_random_with_and_without_modulus():
    rng = random.Random(8302)
    for mod in (None, 998244353, 12):
        for n in (0, 1, 2, 17, 64):
            values = [rng.randrange(-100, 101) for _ in range(n)]
            if mod is not None:
                values = [value % mod for value in values]
            tree = RangeAffineRangeSum(values, mod)
            for _ in range(3000):
                left = rng.randrange(n + 1)
                right = rng.randrange(left, n + 1)
                if rng.randrange(3):
                    multiplier = rng.randrange(-5, 6)
                    addend = rng.randrange(-100, 101)
                    tree.apply(left, right, multiplier, addend)
                    values[left:right] = [
                        multiplier * value + addend for value in values[left:right]
                    ]
                    if mod is not None:
                        values[left:right] = [value % mod for value in values[left:right]]
                else:
                    want = sum(values[left:right])
                    if mod is not None:
                        want %= mod
                    assert tree.range_sum(left, right) == want
            assert tree.all_sum() == (sum(values) if mod is None else sum(values) % mod)
            assert [tree.get(index) for index in range(n)] == values


def test_large_integers_and_nonrecursive_scale():
    big = 10**80
    values = [-big, big, 0, big - 1, -big + 1]
    tree = RangeAddAssignRangeStats(values)
    tree.range_add(0, 4, big * 3)
    values[:4] = [value + big * 3 for value in values[:4]]
    tree.range_assign(1, 3, -big * 7)
    values[1:3] = [-big * 7] * 2
    assert tree.range_sum(0, 5) == sum(values)
    assert tree.range_min(0, 5) == min(values)
    assert tree.range_max(0, 5) == max(values)

    n = 200000
    tree = RangeAddAssignRangeStats(n)
    tree.range_add(0, n, 7)
    tree.range_assign(1000, n - 1000, 11)
    assert tree.range_sum(0, n) == 2000 * 7 + (n - 2000) * 11
    assert tree.range_min(0, n) == 7
    assert tree.range_max(0, n) == 11

    affine = RangeAffineRangeSum(n, 998244353)
    affine.apply(0, n, 3, 5)
    affine.apply(123, n - 321, 7, 9)
    assert affine.range_sum(0, 123) == 123 * 5
