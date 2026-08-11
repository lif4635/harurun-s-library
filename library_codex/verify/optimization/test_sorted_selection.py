import random

import pytest

from library_codex.optimization.SortedListsSelection import kth as lists_kth
from library_codex.optimization.SortedListsSelection import take as lists_take
from library_codex.optimization.SortedMatrixSelection import kth as matrix_kth
from library_codex.optimization.SortedMatrixSelection import take as matrix_take


def _merged_entries(rows):
    return sorted(
        (value, row, index)
        for row, values in enumerate(rows)
        for index, value in enumerate(values)
    )


def _expected_counts(entries, row_count, k):
    result = [0] * row_count
    for _, row, _ in entries[:k]:
        result[row] += 1
    return result


def test_sorted_lists_random_against_stable_merge():
    random.seed(20260812)
    for row_count in range(1, 9):
        for _ in range(100):
            rows = [
                sorted(random.randrange(-5, 6) for _ in range(random.randrange(9)))
                for _ in range(row_count)
            ]
            entries = _merged_entries(rows)
            for k in range(len(entries) + 1):
                assert lists_take(rows, k) == _expected_counts(entries, row_count, k)
                if k < len(entries):
                    assert lists_kth(rows, k) == entries[k][0]


def test_sorted_lists_boundaries():
    assert lists_take([], 0) == []
    assert lists_take([[], [1, 2]], 2) == [0, 2]
    with pytest.raises(IndexError):
        lists_take([[1]], 2)
    with pytest.raises(IndexError):
        lists_kth([], 0)


def test_sorted_matrix_random_against_stable_merge():
    random.seed(20260813)
    for row_count in range(1, 8):
        for column_count in range(1, 8):
            for _ in range(35):
                row_offset = []
                value = random.randrange(-8, 1)
                for _ in range(row_count):
                    value += random.randrange(3)
                    row_offset.append(value)
                column_offset = []
                value = 0
                for _ in range(column_count):
                    value += random.randrange(3)
                    column_offset.append(value)
                matrix = [
                    [row_offset[i] + column_offset[j] for j in range(column_count)]
                    for i in range(row_count)
                ]
                entries = _merged_entries(matrix)
                for k in range(len(entries) + 1):
                    assert matrix_take(matrix, k) == _expected_counts(
                        entries, row_count, k
                    )
                    if k < len(entries):
                        assert matrix_kth(matrix, k) == entries[k][0]


def test_sorted_matrix_boundaries():
    assert matrix_take([], 0) == []
    with pytest.raises(IndexError):
        matrix_kth([], 0)
    with pytest.raises(ValueError):
        matrix_take([[1], [2, 3]], 1)
