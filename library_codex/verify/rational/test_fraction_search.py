from bisect import bisect_left, bisect_right
from fractions import Fraction
from math import gcd
from random import Random

import pytest

from library_codex.rational.FractionSearch import rational_bounds, stern_brocot_binary_search


def test_rational_bounds_exhaustive():
    for limit in range(1, 20):
        available = sorted({Fraction(a, b) for a in range(1, limit + 1) for b in range(1, limit + 1)})
        for a in range(1, 40):
            for b in range(1, 40):
                target = Fraction(a, b)
                lower, upper = rational_bounds(a, b, limit)
                left = bisect_right(available, target) - 1
                right = bisect_left(available, target)
                expected_low = (available[left].numerator, available[left].denominator) if left >= 0 else (0, 1)
                expected_high = (available[right].numerator, available[right].denominator) if right < len(available) else (1, 0)
                assert lower == expected_low
                assert upper == expected_high


def test_exact_extreme_and_invalid():
    assert rational_bounds(14, 21, 3) == ((2, 3), (2, 3))
    assert rational_bounds(1, 10**100, 10**30) == ((0, 1), (1, 10**30))
    assert rational_bounds(10**100, 1, 10**30) == ((10**30, 1), (1, 0))
    for args in [(0, 1, 1), (1, 0, 1), (1, 1, 0), (-1, 2, 3)]:
        with pytest.raises(ValueError):
            rational_bounds(*args)


def test_large_bounds_certificate():
    rng = Random(4863)
    for _ in range(3000):
        numerator = rng.randrange(1, 10**30)
        denominator = rng.randrange(1, 10**30)
        limit = rng.randrange(1, 10**30)
        (a, b), (c, d) = rational_bounds(numerator, denominator, limit)
        assert max(a, b, c, d) <= limit
        assert a * denominator <= b * numerator
        assert c * denominator >= d * numerator
        assert gcd(a, b) == gcd(c, d) == 1
        if (a, b) == (c, d):
            assert a * denominator == b * numerator
        else:
            assert b * c - a * d == 1
            assert a + c > limit or b + d > limit


def test_stern_brocot_binary_search_against_enumeration():
    for limit in range(1, 80):
        fractions = [(0, 1)]
        for denominator in range(1, limit + 1):
            for numerator in range(1, limit + 1):
                if gcd(numerator, denominator) == 1:
                    fractions.append((numerator, denominator))
        fractions.sort(key=lambda value: value[0] / value[1])
        fractions.append((1, 0))
        expected_true = next(
            value for value in fractions
            if value[1] == 0 or value[0] * value[0] >= 2 * value[1] * value[1]
        )
        true_index = fractions.index(expected_true)
        expected_false = fractions[true_index - 1]
        actual = stern_brocot_binary_search(
            lambda value: value[0] * value[0] >= 2 * value[1] * value[1],
            limit,
        )
        assert actual == (expected_false, expected_true)


def test_stern_brocot_binary_search_boundary_cases():
    assert stern_brocot_binary_search(lambda value: True, 10) == (
        (0, 1), (0, 1)
    )
    assert stern_brocot_binary_search(lambda value: False, 0) == (
        (0, 1), (1, 0)
    )
