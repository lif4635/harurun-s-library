import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.convolution.LinearRecurrence import (
    berlekamp_massey,
    berlekamp_massey_polynomial,
    bostan_mori,
    kitamasa,
    linear_recurrence_nth,
    nth_term,
)


MOD = 998244353


def generate(initial, coefficients, size, mod=MOD):
    result = [value % mod for value in initial]
    order = len(coefficients)
    while len(result) < size:
        result.append(sum(
            coefficients[index] * result[-1 - index]
            for index in range(order)
        ) % mod)
    return result[:size]


def slow_nth(initial, coefficients, index, mod=MOD):
    order = len(coefficients)
    if index < order:
        return initial[index] % mod

    def combine(first, second):
        product = [0] * (2 * order - 1)
        for left, left_value in enumerate(first):
            for right, right_value in enumerate(second):
                product[left + right] = (
                    product[left + right] + left_value * right_value
                ) % mod
        for degree in range(2 * order - 2, order - 1, -1):
            value = product[degree]
            for offset, coefficient in enumerate(coefficients):
                target = degree - 1 - offset
                product[target] = (
                    product[target] + value * coefficient
                ) % mod
        return product[:order]

    result = [1] + [0] * (order - 1)
    base = [0] * order
    if order == 1:
        base[0] = coefficients[0] % mod
    else:
        base[1] = 1
    power = index
    while power:
        if power & 1:
            result = combine(result, base)
        base = combine(base, base)
        power >>= 1
    return sum(result[i] * initial[i] for i in range(order)) % mod


def rational_coefficients(numerator, denominator, size, mod=MOD):
    inverse = pow(denominator[0], -1, mod)
    result = []
    for index in range(size):
        value = numerator[index] if index < len(numerator) else 0
        for offset in range(1, min(index + 1, len(denominator))):
            value -= denominator[offset] * result[index - offset]
        result.append(value * inverse % mod)
    return result


def test_berlekamp_massey_and_nth_term_random():
    rng = random.Random(0)
    for _ in range(1500):
        order = rng.randrange(1, 12)
        coefficients = [rng.randrange(MOD) for _ in range(order)]
        initial = [rng.randrange(MOD) for _ in range(order)]
        sequence = generate(initial, coefficients, 5 * order + 20)
        found = berlekamp_massey(sequence)
        polynomial = berlekamp_massey_polynomial(sequence)
        assert polynomial == [1] + [-value % MOD for value in found]
        for index in range(len(found), len(sequence)):
            assert sequence[index] == sum(
                found[offset] * sequence[index - 1 - offset]
                for offset in range(len(found))
            ) % MOD
        target = rng.randrange(10**18)
        expected = slow_nth(initial, coefficients, target)
        assert linear_recurrence_nth(initial, coefficients, target) == expected
        assert nth_term(target, sequence) == expected
        characteristic = [1] + [-value % MOD for value in coefficients]
        assert kitamasa(target, characteristic, initial) == expected


def test_bostan_mori_against_series_expansion():
    rng = random.Random(1)
    for _ in range(5000):
        denominator = [rng.randrange(1, MOD)] + [
            rng.randrange(MOD) for _ in range(rng.randrange(12))
        ]
        numerator = [rng.randrange(MOD) for _ in range(rng.randrange(16))]
        index = rng.randrange(100)
        expected = rational_coefficients(
            numerator, denominator, index + 1
        )[index]
        assert bostan_mori(index, numerator, denominator) == expected


def test_other_prime_and_edge_cases():
    mod = 10**9 + 7
    fibonacci = [0, 1]
    for _ in range(100):
        fibonacci.append((fibonacci[-1] + fibonacci[-2]) % mod)
    assert berlekamp_massey(fibonacci, mod) == [1, 1]
    assert nth_term(10**18, fibonacci, mod) == slow_nth(
        [0, 1], [1, 1], 10**18, mod
    )
    assert berlekamp_massey([0] * 100) == []
    assert nth_term(10**18, [0] * 100) == 0
    assert bostan_mori(5, [1, 2, 3, 4, 5, 6], [1, -1]) == 21
    assert bostan_mori(1, [7], [1]) == 0
    assert bostan_mori(10**18, [7], [1]) == 0
    with pytest.raises(ValueError):
        bostan_mori(-1, [1], [1])
    with pytest.raises(ZeroDivisionError):
        bostan_mori(0, [1], [])
    with pytest.raises(ValueError):
        linear_recurrence_nth([1], [1, 1], 10)


def test_large_order_without_recursion():
    order = 20000
    coefficients = [0] * order
    coefficients[0] = 1
    coefficients[-1] = 1
    initial = [index % MOD for index in range(order)]
    result = linear_recurrence_nth(initial, coefficients, 10**18)
    assert 0 <= result < MOD


if __name__ == "__main__":
    test_berlekamp_massey_and_nth_term_random()
    test_bostan_mori_against_series_expansion()
    test_other_prime_and_edge_cases()
    test_large_order_without_recursion()
