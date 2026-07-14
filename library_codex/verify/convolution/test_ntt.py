import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.NTT import (
    NumberTheoreticTransform,
    convolution,
    convolution_any_mod,
    convolution_int,
    convolution_naive,
    convolution_ntt,
    get_ntt,
    primitive_root,
)


FRIENDLY_MODS = (
    998244353,
    924844033,
    1012924417,
    469762049,
    1811939329,
    2013265921,
)


def test_ntt_round_trip_and_primitive_roots():
    rng = random.Random(0)
    for mod in FRIENDLY_MODS:
        root = primitive_root(mod)
        assert pow(root, mod - 1, mod) == 1
        transform = NumberTheoreticTransform(mod, root)
        assert get_ntt(mod).primitive_root == root
        for exponent in range(11):
            size = 1 << exponent
            values = [rng.randrange(-mod, 2 * mod) for _ in range(size)]
            expected = [value % mod for value in values]
            transform.butterfly(values)
            transform.butterfly_inv(values)
            assert values == expected


def test_convolution_ntt_against_naive():
    rng = random.Random(1)
    for _ in range(5000):
        mod = rng.choice(FRIENDLY_MODS)
        first = [
            rng.randrange(-2 * mod, 2 * mod)
            for _ in range(rng.randrange(100))
        ]
        second = [
            rng.randrange(-2 * mod, 2 * mod)
            for _ in range(rng.randrange(100))
        ]
        assert convolution_ntt(first, second, mod) == convolution_naive(
            first, second, mod
        )
    values = list(range(100))
    assert convolution_ntt(values, values) == convolution_naive(
        values, values, 998244353
    )
    assert convolution_ntt([], values) == []


def test_arbitrary_mod_convolution():
    rng = random.Random(2)
    mods = (1, 2, 6, 97, 10**9 + 7, 2**31 - 1)
    for _ in range(1500):
        mod = rng.choice(mods)
        first = [rng.randrange(-10**9, 10**9) for _ in range(rng.randrange(90))]
        second = [rng.randrange(-10**9, 10**9) for _ in range(rng.randrange(90))]
        expected = convolution_naive(first, second, mod)
        assert convolution_any_mod(first, second, mod) == expected
        assert convolution(first, second, mod) == expected
    with pytest.raises(OverflowError):
        convolution_any_mod(
            [10**20] * 61,
            [10**20] * 61,
            10**20 + 39,
        )


def test_integer_convolution():
    rng = random.Random(3)
    for _ in range(2000):
        first = [rng.randrange(-10**6, 10**6) for _ in range(rng.randrange(100))]
        second = [rng.randrange(-10**6, 10**6) for _ in range(rng.randrange(100))]
        assert convolution_int(first, second) == convolution_naive(first, second)
    with pytest.raises(OverflowError):
        convolution_int([10**20] * 61, [10**20] * 61)


def test_length_validation():
    transform = NumberTheoreticTransform(17, 3)
    with pytest.raises(ValueError):
        transform.butterfly([0] * 3)
    with pytest.raises(ValueError):
        transform.butterfly([0] * 32)


def test_large_without_recursion():
    size = 200000
    first = [index % 1000 for index in range(size)]
    second = [1] * size
    result = convolution_ntt(first, second)
    assert len(result) == 2 * size - 1
    assert result[size - 1] == sum(first) % 998244353


if __name__ == "__main__":
    test_ntt_round_trip_and_primitive_roots()
    test_convolution_ntt_against_naive()
    test_arbitrary_mod_convolution()
    test_integer_convolution()
    test_length_validation()
    test_large_without_recursion()
