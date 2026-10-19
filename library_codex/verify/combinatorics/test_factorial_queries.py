import math
import random

import pytest

from library_codex.combinatorics.FactorialQueries import _extend_samples, factorials


def test_small_and_order():
    rng = random.Random(547823)
    indices = list(range(200)) + [rng.randrange(200) for _ in range(400)]
    rng.shuffle(indices)
    original = indices[:]
    assert factorials(indices) == [math.factorial(n) % 998244353 for n in indices]
    assert indices == original
    assert factorials(iter([5, 0, 5, 1])) == [120, 1, 120, 1]
    assert factorials([]) == []


def test_block_boundaries():
    indices = [262143, 262144, 262145, 262146, 4096 * 65 - 1, 4096 * 65,
               4096 * 65 + 1, 500000, 0, 1, 262145]
    expected = [1] * (max(indices) + 1)
    for i in range(1, len(expected)):
        expected[i] = expected[i - 1] * i % 998244353
    assert factorials(indices) == [expected[n] for n in indices]


def test_wilson_and_modulus():
    mod = 998244353
    indices = [mod - i for i in range(1, 30)] + [mod, mod + 1, 10 ** 30]
    expected = [(-pow(math.factorial(i - 1), -1, mod) * (-1) ** (i - 1)) % mod
                for i in range(1, 30)] + [0, 0, 0]
    assert factorials(indices) == expected
    assert factorials([mod, mod * 2]) == [0, 0]
    with pytest.raises(ValueError):
        factorials([0, -1])


def test_complements_and_duplicates():
    mod = 998244353
    rng = random.Random(10623)
    small = [rng.randrange(300000, 600000) for _ in range(100)]
    expected = [1] * (max(small) + 1)
    for i in range(1, len(expected)):
        expected[i] = expected[i - 1] * i % mod
    indices = small + [mod - 1 - n for n in small] + small[:10]
    actual = factorials(indices)
    assert actual[:100] == [expected[n] for n in small]
    assert actual[-10:] == actual[:10]
    for i, n in enumerate(small):
        assert actual[i] * actual[100 + i] % mod == (1 if n & 1 else mod - 1)


def test_sampling_extension():
    mod = 998244353
    inverse = [0] + [pow(i, -1, mod) for i in range(1, 1000)]
    rng = random.Random(48213)
    for size in [1, 2, 3, 7, 16, 33, 64, 129]:
        coefficients = [rng.randrange(mod) for _ in range(size)]
        values = [sum(c * pow(x, i, mod) for i, c in enumerate(coefficients)) % mod
                  for x in range(size * 4)]
        assert _extend_samples(values[:size], size * 4, inverse) == values
        assert _extend_samples(values[:size], size // 2, inverse) == values[:size // 2]
