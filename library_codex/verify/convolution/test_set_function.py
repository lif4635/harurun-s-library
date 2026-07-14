import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.SetFunction import (
    SubsetConvolution,
    bitwise_and_convolution,
    bitwise_or_convolution,
    bitwise_xor_convolution,
    set_series_exponential,
    set_series_logarithm,
    subset_convolution,
    subset_mobius_transform,
    subset_zeta_transform,
    superset_mobius_transform,
    superset_zeta_transform,
    walsh_hadamard_transform,
)


MOD = 998244353


def brute_subset(first, second, mod=MOD):
    result = [0] * len(first)
    for mask in range(len(first)):
        subset = mask
        while True:
            result[mask] += first[subset] * second[mask ^ subset]
            if subset == 0:
                break
            subset = (subset - 1) & mask
        result[mask] %= mod
    return result


def brute_bitwise(first, second, operation):
    result = [0] * len(first)
    for left, left_value in enumerate(first):
        for right, right_value in enumerate(second):
            result[operation(left, right)] += left_value * right_value
    return [value % MOD for value in result]


def test_zeta_mobius_transforms_against_definitions():
    rng = random.Random(0)
    for bits in range(9):
        size = 1 << bits
        for _ in range(300):
            values = [rng.randrange(-1000, 1000) for _ in range(size)]
            subset_expected = [sum(
                values[submask]
                for submask in range(size)
                if submask & mask == submask
            ) for mask in range(size)]
            superset_expected = [sum(
                values[supermask]
                for supermask in range(size)
                if supermask & mask == mask
            ) for mask in range(size)]
            transformed = subset_zeta_transform(values[:])
            assert transformed == subset_expected
            assert subset_mobius_transform(transformed) == values
            transformed = superset_zeta_transform(values[:])
            assert transformed == superset_expected
            assert superset_mobius_transform(transformed) == values
            transformed = subset_zeta_transform(values[:], MOD)
            assert subset_mobius_transform(transformed, MOD) == [
                value % MOD for value in values
            ]


def test_bitwise_convolutions_against_brute():
    rng = random.Random(1)
    for _ in range(3000):
        size = 1 << rng.randrange(7)
        first = [rng.randrange(MOD) for _ in range(size)]
        second = [rng.randrange(MOD) for _ in range(size)]
        assert bitwise_or_convolution(first, second) == brute_bitwise(
            first, second, int.__or__
        )
        assert bitwise_and_convolution(first, second) == brute_bitwise(
            first, second, int.__and__
        )
        assert bitwise_xor_convolution(first, second) == brute_bitwise(
            first, second, int.__xor__
        )
        transformed = walsh_hadamard_transform(first[:])
        assert walsh_hadamard_transform(transformed, True) == first


def test_subset_convolution_division_and_transpose():
    rng = random.Random(2)
    engine = SubsetConvolution()
    for _ in range(5000):
        size = 1 << rng.randrange(9)
        first = [rng.randrange(MOD) for _ in range(size)]
        second = [rng.randrange(MOD) for _ in range(size)]
        expected = brute_subset(first, second)
        assert subset_convolution(first, second) == expected
        assert engine.multiply(first, second) == expected
        if second[0] == 0:
            second[0] = 1
        product = engine.multiply(first, second)
        assert engine.divide(product, second) == first
        transposed = engine.transpose_multiply(first, second)
        expected_transposed = brute_subset(first[::-1], second)
        expected_transposed.reverse()
        assert transposed == expected_transposed


def test_set_series_exp_log_are_inverse():
    rng = random.Random(3)
    for bits in range(9):
        size = 1 << bits
        for _ in range(300):
            series = [0] + [rng.randrange(MOD) for _ in range(size - 1)]
            exponential = set_series_exponential(series)
            assert exponential[0] == 1
            assert set_series_logarithm(exponential) == series
    with pytest.raises(ValueError):
        set_series_exponential([1, 2])
    with pytest.raises(ValueError):
        set_series_logarithm([0, 2])


def test_validation_and_large_without_recursion():
    with pytest.raises(ValueError):
        subset_zeta_transform([])
    with pytest.raises(ValueError):
        subset_zeta_transform([1, 2, 3])
    with pytest.raises(ValueError):
        bitwise_or_convolution([1], [1, 2])
    size = 1 << 15
    first = [index % 1000 for index in range(size)]
    second = [(index * index + 1) % MOD for index in range(size)]
    result = subset_convolution(first, second)
    assert len(result) == size
    assert result[0] == first[0] * second[0] % MOD
    assert result[-1] == brute_subset(first, second)[-1]


if __name__ == "__main__":
    test_zeta_mobius_transforms_against_definitions()
    test_bitwise_convolutions_against_brute()
    test_subset_convolution_division_and_transpose()
    test_set_series_exp_log_are_inverse()
    test_validation_and_large_without_recursion()
