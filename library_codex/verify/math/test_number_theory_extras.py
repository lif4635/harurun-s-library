import random
from math import gcd

from library_codex.math.NumberTheoryExtras import (
    FastPower,
    GaussianInteger,
    RationalNumberSearch,
    ceil_div,
    floor_div,
    gaussian_gcd,
    quadratic_equation_mod,
    strict_ceil_div,
    strict_floor_div,
    tetration_mod,
    two_square_representations,
)


def _tower(base, height):
    value = 1
    for _ in range(height):
        value = base ** value
    return value


def test_integer_division_quadratic_and_fast_power():
    for numerator in range(-30, 31):
        for denominator in range(-10, 11):
            if denominator == 0:
                continue
            assert floor_div(numerator, denominator) <= numerator / denominator
            assert ceil_div(numerator, denominator) >= numerator / denominator
            assert strict_floor_div(numerator, denominator) < numerator / denominator
            assert strict_ceil_div(numerator, denominator) > numerator / denominator
    for prime in (2, 3, 5, 7, 17, 101):
        for a in range(prime):
            for b in range(prime):
                for c in range(prime):
                    if a == b == c == 0:
                        continue
                    expected = [x for x in range(prime)
                                if (a * x * x + b * x + c) % prime == 0]
                    assert quadratic_equation_mod(a, b, c, prime) == expected
    fixed = FastPower(1234567, 998244353, (1 << 50) - 1)
    rng = random.Random(41)
    for _ in range(1000):
        exponent = rng.randrange(1 << 50)
        assert fixed(exponent) == pow(1234567, exponent, 998244353)


def test_tetration_exhaustive_manageable_towers():
    for base in range(5):
        for height in range(4):
            exact = _tower(base, height)
            for modulus in range(1, 100):
                assert tetration_mod(base, height, modulus) == exact % modulus
    # Heights too large to materialize still satisfy known cycles.
    assert tetration_mod(2, 10, 1000) == 736
    assert tetration_mod(3, 7, 100) == 87


def test_gaussian_integer_and_two_square_exhaustive():
    rng = random.Random(42)
    for _ in range(1000):
        first = GaussianInteger(rng.randrange(-100, 101), rng.randrange(-100, 101))
        second = GaussianInteger(rng.randrange(-20, 21), rng.randrange(-20, 21))
        if second == GaussianInteger():
            continue
        quotient, remainder = divmod(first, second)
        assert quotient * second + remainder == first
        assert remainder.norm() <= second.norm()
    assert gaussian_gcd(GaussianInteger(5), GaussianInteger(2, 1)).norm() in (1, 5)
    for number in range(1000):
        expected = []
        limit = int(number ** 0.5)
        for x in range(limit + 1):
            for y in range(limit + 1):
                if x * x + y * y == number:
                    expected.append((x, y))
        assert two_square_representations(number) == expected


def test_rational_number_search_finds_threshold_neighbors():
    for maximum in range(1, 30):
        for numerator, denominator in ((1, 3), (2, 5), (7, 11), (13, 8)):
            search = RationalNumberSearch(maximum)
            seen = []
            while search.has_next():
                value = search.get_next()
                seen.append(value)
                search.give(value[0] * denominator < numerator * value[1])
            assert seen
            assert len(seen) == len(set(seen))
            assert all(0 <= a <= maximum and 0 <= b <= maximum
                       and gcd(a, b) == 1 for a, b in seen)
