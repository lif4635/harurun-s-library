import itertools
import random

import pytest

from library_codex.optimization.FixedSizeSubsetSum import fixed_size_subset_sums


def brute(values, k):
    return sorted({sum(chosen) for chosen in itertools.combinations(sorted(set(values)), k)})


def test_random_small_and_duplicates():
    rng = random.Random(17291)
    for n in range(13):
        for _ in range(30):
            values = [rng.randrange(-15, 16) for _ in range(n)]
            k = rng.randrange(n + 2)
            assert fixed_size_subset_sums(values, k) == brute(values, k)
    assert fixed_size_subset_sums([2, 2, 3], 2) == [5]
    with pytest.raises(ValueError):
        fixed_size_subset_sums([1, 2], -1)


def test_bitset_branch_against_set_dp():
    rng = random.Random(91)
    for _ in range(15):
        values = sorted(rng.sample(range(-100, 150), 24))
        k = rng.randrange(5, 20)
        dp = [{0}] + [set() for _ in range(k)]
        for i, value in enumerate(values):
            for count in range(min(i + 1, k), 0, -1):
                dp[count].update(previous + value for previous in dp[count - 1])
        assert fixed_size_subset_sums(values, k) == sorted(dp[k])


def test_arithmetic_progression_complement_and_huge_values():
    for k in (0, 1, 5, 30, 59, 60, 61):
        values = [10**30 + 17 * i for i in range(60)]
        low = k * (k - 1) // 2
        high = k * (119 - k) // 2
        expected = [k * 10**30 + 17 * s for s in range(low, high + 1)] if k <= 60 else []
        assert fixed_size_subset_sums(values, k) == expected
    values = [10**60, -(10**50), 17, 3]
    assert fixed_size_subset_sums(values, 2) == brute(values, 2)
