import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.NTT998 import MOD, multiply
from library_codex.fps998.NTT2D import intt2d, multiply2d, ntt2d
from library_codex.fps998.SubsetSum import multiset_sum, subset_sum


def test_fps998_subset_and_multiset_generating_functions():
    rng = random.Random(9986)
    for _ in range(500):
        size = rng.randrange(1, 45)
        counts = [0] + [rng.randrange(4) for _ in range(size - 1)]
        expected_subset = [1] + [0] * (size - 1)
        expected_multiset = [1] + [0] * (size - 1)
        for weight in range(1, size):
            for _ in range(counts[weight]):
                for total in range(size - 1, weight - 1, -1):
                    expected_subset[total] += expected_subset[total - weight]
                    expected_subset[total] %= MOD
                for total in range(weight, size):
                    expected_multiset[total] += expected_multiset[total - weight]
                    expected_multiset[total] %= MOD
        assert subset_sum(counts) == expected_subset
        assert multiset_sum(counts) == expected_multiset


def _naive_multiply2d(first, second):
    rows = len(first) + len(second) - 1
    columns = len(first[0]) + len(second[0]) - 1
    result = [[0] * columns for _ in range(rows)]
    for row1, values1 in enumerate(first):
        for column1, value1 in enumerate(values1):
            for row2, values2 in enumerate(second):
                for column2, value2 in enumerate(values2):
                    result[row1 + row2][column1 + column2] += value1 * value2
                    result[row1 + row2][column1 + column2] %= MOD
    return result


def test_fps998_ntt2d_round_trip_and_multiply():
    rng = random.Random(9987)
    for rows in (1, 2, 4, 8):
        for columns in (1, 2, 4, 8):
            matrix = [
                [rng.randrange(-MOD, 2 * MOD) for _ in range(columns)]
                for _ in range(rows)
            ]
            expected = [[value % MOD for value in row] for row in matrix]
            assert ntt2d(matrix) is matrix
            assert intt2d(matrix) is matrix
            assert matrix == expected
    for _ in range(300):
        first_rows = rng.randrange(1, 6)
        first_columns = rng.randrange(1, 6)
        first = [
            [rng.randrange(MOD) for _ in range(first_columns)]
            for _ in range(first_rows)
        ]
        second_rows = rng.randrange(1, 6)
        second_columns = rng.randrange(1, 6)
        second = [
            [rng.randrange(MOD) for _ in range(second_columns)]
            for _ in range(second_rows)
        ]
        assert multiply2d(first, second) == _naive_multiply2d(first, second)


if __name__ == "__main__":
    test_fps998_subset_and_multiset_generating_functions()
    test_fps998_ntt2d_round_trip_and_multiply()
