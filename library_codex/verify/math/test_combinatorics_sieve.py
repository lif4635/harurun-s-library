import math
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.combinatorics.Combination import Comb, comb_small_k  # noqa: E402
from library_codex.number_theory.EnumerateQuotient import enumerate_quotient  # noqa: E402
from library_codex.number_theory.FloorSum import floor_sum, mod_affine_range_count  # noqa: E402
from library_codex.combinatorics.GrayCode import gray_code, inverse_gray_code  # noqa: E402
from library_codex.number_theory.IntegerArithmetic import extended_gcd  # noqa: E402
from library_codex.prime.Sieve import (  # noqa: E402
    LinearSieve,
    count_square_free,
    prime_count,
    prime_sieve,
)


def test_extended_gcd_combination_and_gray():
    rng = random.Random(100)
    for _ in range(10_000):
        a = rng.randrange(-10**18, 10**18)
        b = rng.randrange(-10**18, 10**18)
        gcd, x, y = extended_gcd(a, b)
        assert gcd == math.gcd(a, b)
        assert a * x + b * y == gcd
    combination = Comb(mod=998244353)
    for n in range(500):
        for k in range(n + 1):
            assert combination.C(n, k) == math.comb(n, k) % 998244353
            assert combination(n, k) == combination.C(n, k)
    assert combination.F(10) == math.factorial(10) % 998244353
    assert combination.Fi(10) * combination.F(10) % 998244353 == 1
    for value in range(1, 500):
        assert combination.inv(value) * value % 998244353 == 1
    assert combination.P(10, 3) == 10 * 9 * 8
    assert combination.H(4, 3) == math.comb(6, 3)
    assert [combination.catalan(n, n) for n in range(8)] == [
        1, 1, 2, 5, 14, 42, 132, 429,
    ]
    assert combination.catalan(3, 2) == 5
    assert combination.catalan(2, 3) == 0
    assert combination.catalan(2, 3, 1) == 5
    assert combination.catalan(2, 4, 1) == 0
    assert combination.catalan(-1, 0) == 0
    assert combination.catalan(0, 0, -1) == 0
    for n in range(9):
        for m in range(9):
            for k in range(5):
                paths = [[0] * (m + 1) for _ in range(n + 1)]
                paths[0][0] = 1
                for x in range(n + 1):
                    for y in range(m + 1):
                        if y > x + k or (x == 0 and y == 0):
                            continue
                        paths[x][y] = (
                            (paths[x - 1][y] if x else 0)
                            + (paths[x][y - 1] if y else 0)
                        )
                assert combination.catalan(n, m, k) == paths[n][m]
    try:
        combination.inv(0)
    except ValueError:
        pass
    else:
        raise AssertionError("inv(0) must reject a non-invertible value")
    try:
        Comb(mod=7).inv(7)
    except ValueError:
        pass
    else:
        raise AssertionError("inv(mod) must reject a non-invertible value")
    for method in (combination.F, combination.Fi):
        try:
            method(-1)
        except ValueError:
            pass
        else:
            raise AssertionError("factorial methods must reject negative n")
    assert comb_small_k(10**18, 4) == math.comb(10**18, 4) % 998244353
    for old_name in (
        "fact", "factorial_value", "binomial", "nCr", "permutation", "nPr",
        "multiset",
    ):
        assert not hasattr(combination, old_name)
    for value in range(10_000):
        assert inverse_gray_code(gray_code(value)) == value


def test_floor_sum_and_mod_affine_against_direct_sum():
    rng = random.Random(101)
    for _ in range(5_000):
        n = rng.randrange(100)
        modulus = rng.randrange(1, 100)
        multiplier = rng.randrange(-200, 201)
        addend = rng.randrange(-200, 201)
        assert floor_sum(n, modulus, multiplier, addend) == sum(
            (multiplier * i + addend) // modulus for i in range(n)
        )
        y = rng.randrange(modulus + 1)
        assert mod_affine_range_count(
            multiplier, addend, modulus, n, y
        ) == sum((multiplier * i + addend) % modulus < y for i in range(n))


def test_enumerate_quotient_ranges():
    for number in range(1_000):
        ranges = list(enumerate_quotient(number))
        flattened = []
        for quotient, left, right in ranges:
            assert left < right
            assert all(number // value == quotient for value in range(left, right))
            flattened.extend(range(left, right))
        assert flattened == list(range(1, number + 1))


def _is_prime(value):
    return value >= 2 and all(value % divisor
                              for divisor in range(2, math.isqrt(value) + 1))


def test_linear_sieve_prime_count_and_square_free():
    sieve = LinearSieve(100_000)
    assert all(_is_prime(value) for value in sieve.primes)
    assert len(sieve.primes) == 9592
    for value in range(1, 100_001):
        factors = sieve.factor_count(value)
        product = 1
        for prime, exponent in factors:
            product *= prime ** exponent
        assert product == value
        expected_phi = value
        for prime, _ in factors:
            expected_phi -= expected_phi // prime
        assert sieve.phi[value] == expected_phi
        square_free = all(exponent == 1 for _, exponent in factors)
        assert sieve.mobius[value] == (
            (-1) ** len(factors) if square_free else 0
        )
    primes = prime_sieve(1_000_000)
    for number in list(range(10_000)) + [10**5, 10**6, 10**7, 10**8]:
        expected = sum(prime <= number for prime in primes)
        if number > 1_000_000:
            expected = {10**7: 664579, 10**8: 5761455}[number]
        assert prime_count(number) == expected
    square_free_prefix = [0] * 2_001
    for value in range(1, 2_001):
        square_free_prefix[value] = square_free_prefix[value - 1] + int(
            all(exponent == 1 for _, exponent in sieve.factor_count(value))
        )
    for number in range(2_001):
        assert count_square_free(number) == square_free_prefix[number]
