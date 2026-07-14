import random
import sys
from math import gcd, lcm
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.ArithmeticConvolution import (
    divisor_mobius_transform,
    divisor_zeta_transform,
    gcd_convolution,
    lcm_convolution,
    multiple_mobius_transform,
    multiple_zeta_transform,
)


MOD = 998244353


def test_divisor_multiple_transforms_against_definitions():
    rng = random.Random(0)
    for limit in range(1, 300):
        values = [0] + [rng.randrange(-1000, 1000) for _ in range(limit)]
        expected_divisor = [0] + [sum(
            values[divisor]
            for divisor in range(1, value + 1)
            if value % divisor == 0
        ) for value in range(1, limit + 1)]
        expected_multiple = [0] + [sum(
            values[multiple]
            for multiple in range(value, limit + 1, value)
        ) for value in range(1, limit + 1)]
        transformed = divisor_zeta_transform(values[:])
        assert transformed == expected_divisor
        assert divisor_mobius_transform(transformed) == values
        transformed = multiple_zeta_transform(values[:])
        assert transformed == expected_multiple
        assert multiple_mobius_transform(transformed) == values


def test_gcd_lcm_convolution_against_brute():
    rng = random.Random(1)
    for _ in range(3000):
        limit = rng.randrange(1, 100)
        first = [0] + [rng.randrange(MOD) for _ in range(limit)]
        second = [0] + [rng.randrange(MOD) for _ in range(limit)]
        expected_gcd = [0] * (limit + 1)
        expected_lcm = [0] * (limit + 1)
        for left in range(1, limit + 1):
            for right in range(1, limit + 1):
                product = first[left] * second[right]
                expected_gcd[gcd(left, right)] += product
                current_lcm = lcm(left, right)
                if current_lcm <= limit:
                    expected_lcm[current_lcm] += product
        expected_gcd = [value % MOD for value in expected_gcd]
        expected_lcm = [value % MOD for value in expected_lcm]
        assert gcd_convolution(first, second) == expected_gcd
        assert lcm_convolution(first, second) == expected_lcm


def test_large_without_recursion():
    limit = 500000
    first = [0] + [index % 1000 for index in range(1, limit + 1)]
    second = [0] + [(index * index + 1) % MOD for index in range(1, limit + 1)]
    gcd_result = gcd_convolution(first, second)
    lcm_result = lcm_convolution(first, second)
    assert len(gcd_result) == len(lcm_result) == limit + 1
    assert gcd_result[limit] == first[limit] * second[limit] % MOD
    assert lcm_result[1] == first[1] * second[1] % MOD


if __name__ == "__main__":
    test_divisor_multiple_transforms_against_definitions()
    test_gcd_lcm_convolution_against_brute()
    test_large_without_recursion()
