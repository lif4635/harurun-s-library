import pytest

from library_codex.combinatorial_series.StirlingNumbers import (
    stirling_first_column,
    stirling_first_row,
    stirling_second_column,
    stirling_second_row,
)


def tables(size, mod):
    first = [[1]]
    second = [[1]]
    for n in range(1, size + 1):
        a = [0] * (n + 1)
        b = [0] * (n + 1)
        for k in range(1, n + 1):
            a[k] = (first[-1][k - 1] + (n - 1) * (first[-1][k] if k < n else 0)) % mod
            b[k] = (second[-1][k - 1] + k * (second[-1][k] if k < n else 0)) % mod
        first.append(a)
        second.append(b)
    return first, second


def test_rows_and_columns_against_recurrences():
    for mod in (2, 3, 17, 257, 998244353, 1000000007):
        size = min(35, mod - 1)
        first, second = tables(size, mod)
        for n in range(size + 1):
            assert stirling_first_row(n, mod) == first[n]
            assert stirling_first_row(n, mod, signed=True) == [
                (-value if (n - k) & 1 else value) % mod for k, value in enumerate(first[n])
            ]
            assert stirling_second_row(n, mod) == second[n]
            for k in range(n + 1):
                assert stirling_first_column(k, n, mod) == [
                    first[i][k] if k <= i else 0 for i in range(n + 1)
                ]
                assert stirling_second_column(k, n, mod) == [
                    second[i][k] if k <= i else 0 for i in range(n + 1)
                ]


def test_columns_across_transform_and_truncation_boundaries():
    for mod in (998244353, 1000000007):
        first, second = tables(260, mod)
        for n in (63, 64, 65, 127, 128, 129, 255, 256, 260):
            for k in (0, 1, 2, 3, 4, 16, n // 2, n - 2, n - 1, n):
                assert stirling_first_column(k, n, mod) == [
                    first[i][k] if k <= i else 0 for i in range(n + 1)
                ]
                assert stirling_second_column(k, n, mod) == [
                    second[i][k] if k <= i else 0 for i in range(n + 1)
                ]


def test_column_validation():
    for function in (stirling_first_column, stirling_second_column):
        assert function(0, 0) == [1]
        assert function(2, 1) == []
        for k in range(3):
            with pytest.raises(ValueError):
                function(k, 17, 17)
        with pytest.raises(ValueError):
            function(-1, 3)
        with pytest.raises(ValueError):
            function(1, -1)
