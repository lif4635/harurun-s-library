import random

import pytest

from library_codex.range_query.WeightedWaveletMatrix import WeightedWaveletMatrix


def test_weighted_wavelet_matrix_random():
    rng = random.Random(271828)
    for size in range(30):
        for _ in range(8):
            values = [rng.randrange(-8, 9) for _ in range(size)]
            weights = [rng.randrange(-20, 21) for _ in range(size)]
            matrix = WeightedWaveletMatrix(values, weights)
            for _ in range(60):
                left = rng.randrange(size + 1)
                right = rng.randrange(left, size + 1)
                lower = rng.randrange(-10, 11)
                upper = rng.randrange(lower, 12)
                pairs = list(zip(values[left:right], weights[left:right]))
                selected = [weight for value, weight in pairs if value < upper]
                assert matrix.total(left, right) == sum(weights[left:right])
                assert matrix.sum_lt(left, right, upper) == sum(selected)
                assert matrix.count_sum_lt(left, right, upper) == (len(selected), sum(selected))
                assert matrix.range_sum(left, right, lower, upper) == sum(
                    weight for value, weight in pairs if lower <= value < upper
                )
                length = right - left
                k = rng.randrange(length + 1)
                ordered = sorted(zip(values[left:right], range(length), weights[left:right]))
                assert matrix.sum_k_smallest(left, right, k) == sum(item[2] for item in ordered[:k])
                assert matrix.sum_k_largest(left, right, k) == sum(item[2] for item in ordered[length - k:])


def test_default_weights():
    matrix = WeightedWaveletMatrix([5, -2, 5, 1, 3])
    assert matrix.range_sum(0, 5, 0, 5) == 4
    assert matrix.sum_k_smallest(0, 5, 3) == 2
    assert matrix.sum_k_largest(1, 5, 2) == 8
    assert matrix.count_sum_lt(0, 5, 5) == (3, 2)
    assert matrix.count_sum_lt(0, 5, 6) == (5, 12)


def test_count_sum_boundaries_and_noninteger_keys():
    matrix = WeightedWaveletMatrix(["c", "a", "b", "a"], [10**100, -3, 4, 8])
    assert matrix.count_sum_lt(0, 4, "a") == (0, 0)
    assert matrix.count_sum_lt(0, 4, "b") == (2, 5)
    assert matrix.count_sum_lt(0, 4, "d") == (4, 10**100 + 9)
    assert matrix.count_sum_lt(1, 3, "c") == (2, 1)
    assert matrix.count_sum_lt(2, 2, "b") == (0, 0)
    assert WeightedWaveletMatrix([]).count_sum_lt(0, 0, 0) == (0, 0)
    for left, right in [(-1, 2), (1, 0), (0, 5)]:
        with pytest.raises(IndexError):
            matrix.count_sum_lt(left, right, "b")


def test_packed_word_boundaries():
    values = [i % 17 for i in range(257)]
    matrix = WeightedWaveletMatrix(values)
    for left in [0, 1, 63, 64, 65, 127, 128, 256, 257]:
        for right in [left, 257]:
            for upper in [-1, 0, 1, 8, 16, 17, 100]:
                selected = [v for v in values[left:right] if v < upper]
                assert matrix.count_sum_lt(left, right, upper) == (len(selected), sum(selected))
