from math import comb

import pytest

from library_codex.combinatorics.QBinomial import QBinomial


def test_q_binomial_against_pascal_recurrence():
    mod = 998244353
    for q in (1, -1, 2, 3, 7):
        table = QBinomial(q, 100, mod)
        rows = [[1]]
        for n in range(1, 50):
            row = [0] * (n + 1)
            row[0] = row[n] = 1
            for k in range(1, n):
                row[k] = (rows[-1][k] + pow(q, n - k, mod) * rows[-1][k - 1]) % mod
            rows.append(row)
            for k in range(n + 1):
                assert table.C(n, k) == row[k]


def test_all_small_prime_orders_and_lucas():
    for mod in (2, 3, 5, 7, 11, 13, 17):
        for q in range(mod):
            table = QBinomial(q, 100, mod)
            row = [1]
            for n in range(1, 101):
                row = [1] + [(row[k] if k < n else 0) +
                    pow(q, n - k, mod) * row[k - 1] for k in range(1, n + 1)]
                row = [value % mod for value in row]
                for k in range(n + 1):
                    assert table.C(n, k) == row[k]
                assert table.C(n, -1) == table.C(n, n + 1) == 0


def test_above_preparation_and_extreme_cases():
    table = QBinomial(-1, 2, 101)
    for n in (50, 100, 1000, 10**30):
        for k in range(10):
            expected = 0 if n % 2 == 0 and k % 2 else comb(n // 2, k // 2) % 101
            assert table.C(n, k) == expected
    table = QBinomial(1, 5, 5)
    for n in range(100):
        for k in range(n + 1):
            assert table.C(n, k) == comb(n, k) % 5
    assert QBinomial(0, 0).C(10**100, 10**99) == 1
    assert QBinomial(2, 0).C(0, 0) == 1
    with pytest.raises(ValueError):
        QBinomial(2, 0).C(100, 5)
    for args in [(1, -1, 7), (1, 1, 1)]:
        with pytest.raises(ValueError):
            QBinomial(*args)
