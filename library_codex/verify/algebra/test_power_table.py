import random

import pytest

from library_codex.algebra.PowerTable import power_table


def test_matches_builtin_power():
    rng = random.Random(63091)
    for limit in (0, 1, 2, 127, 128, 129, 257, 1000):
        for exponent in (0, 1, 2, 3, 4, 37, 10 ** 18):
            for mod in (1, 2, 4, 12, 17, 101, 998244353, -17):
                assert power_table(limit, exponent, mod) == [
                    pow(value, exponent, mod) for value in range(limit + 1)
                ]
    for _ in range(100):
        limit = rng.randrange(1500)
        exponent = rng.randrange(100000)
        mod = rng.randrange(1, 500)
        assert power_table(limit, exponent, mod) == [
            pow(value, exponent, mod) for value in range(limit + 1)
        ]


def test_exact_powers_and_invalid_arguments():
    for exponent in range(15):
        assert power_table(100, exponent) == [value ** exponent for value in range(101)]
    with pytest.raises(ValueError):
        power_table(-1, 3)
    with pytest.raises(ValueError):
        power_table(100, -1, 17)
    with pytest.raises(ValueError):
        power_table(1000, 4, 0)


def test_large_composite_factorization():
    limit = 1000000
    exponent = 100003
    mod = 1000
    table = power_table(limit, exponent, mod)
    assert len(table) == limit + 1
    for index in range(0, limit + 1, 97):
        assert table[index] == pow(index, exponent, mod)
    for index in (65536, 59049, 999983, 999999, 1000000):
        assert table[index] == pow(index, exponent, mod)
