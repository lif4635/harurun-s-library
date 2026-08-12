import random

from library_codex.range_query.StaticRangeDistinct import StaticRangeDistinct
from library_codex.range_query.WeightedWaveletMatrix import WeightedWaveletMatrix


def test_static_range_distinct_random():
    rng = random.Random(918273)
    for size in range(35):
        for _ in range(12):
            values = [rng.randrange(-5, 7) for _ in range(size)]
            query = StaticRangeDistinct(values)
            for _ in range(80):
                left = rng.randrange(size + 1)
                right = rng.randrange(left, size + 1)
                assert query.count(left, right) == len(set(values[left:right]))


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
                expected = sum(
                    weight for value, weight in zip(
                        values[left:right], weights[left:right]
                    ) if lower <= value < upper
                )
                assert matrix.total(left, right) == sum(weights[left:right])
                assert matrix.sum_lt(left, right, upper) == sum(
                    weight for value, weight in zip(
                        values[left:right], weights[left:right]
                    ) if value < upper
                )
                assert matrix.range_sum(
                    left, right, lower, upper
                ) == expected

                length = right - left
                k = rng.randrange(length + 1)
                ordered = sorted(
                    zip(values[left:right], range(length), weights[left:right])
                )
                assert matrix.sum_k_smallest(left, right, k) == sum(
                    item[2] for item in ordered[:k]
                )
                assert matrix.sum_k_largest(left, right, k) == sum(
                    item[2] for item in ordered[length - k:]
                )


def test_weighted_wavelet_matrix_default_weights():
    values = [5, -2, 5, 1, 3]
    matrix = WeightedWaveletMatrix(values)
    assert matrix.range_sum(0, 5, 0, 5) == 4
    assert matrix.sum_k_smallest(0, 5, 3) == 2
    assert matrix.sum_k_largest(1, 5, 2) == 8

