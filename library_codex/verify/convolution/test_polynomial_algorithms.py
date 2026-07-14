import random

from library_codex.convolution.FormalPowerSeries import (
    fps_add,
    fps_evaluate,
    fps_multiply,
    fps_remainder,
)
from library_codex.convolution.PolynomialAlgorithms import (
    partial_fraction_distinct,
    polynomial_extended_gcd,
    polynomial_gcd,
    polynomial_inverse_mod,
    polynomial_pow_mod,
    polynomial_prefix_sum,
    polynomial_resultant,
    polynomial_roots,
    power_sums,
    prefix_sum_powers,
)


MOD = 998244353


def _shrink(values):
    while values and values[-1] % MOD == 0:
        values.pop()
    return [value % MOD for value in values]


def _sylvester_resultant(first, second, mod):
    m = len(first) - 1
    n = len(second) - 1
    size = m + n
    matrix = [[0] * size for _ in range(size)]
    first = list(reversed(first))
    second = list(reversed(second))
    for row in range(n):
        matrix[row][row:row + m + 1] = first
    for row in range(m):
        matrix[n + row][row:row + n + 1] = second
    determinant = 1
    for column in range(size):
        pivot = column
        while pivot < size and matrix[pivot][column] % mod == 0:
            pivot += 1
        if pivot == size:
            return 0
        if pivot != column:
            matrix[pivot], matrix[column] = matrix[column], matrix[pivot]
            determinant = -determinant
        pivot_value = matrix[column][column] % mod
        determinant = determinant * pivot_value % mod
        inverse = pow(pivot_value, -1, mod)
        for row in range(column + 1, size):
            scale = matrix[row][column] * inverse % mod
            for offset in range(column, size):
                matrix[row][offset] = (
                    matrix[row][offset] - scale * matrix[column][offset]
                ) % mod
    return determinant % mod


def test_polynomial_gcd_extended_inverse_and_power():
    rng = random.Random(11)
    for _ in range(80):
        common = [rng.randrange(MOD) for _ in range(rng.randrange(1, 5))]
        common[-1] = rng.randrange(1, MOD)
        first = fps_multiply(common, [rng.randrange(MOD), 1])
        second = fps_multiply(common, [rng.randrange(MOD), 1])
        gcd = polynomial_gcd(first, second)
        expected = [value * pow(common[-1], -1, MOD) % MOD for value in common]
        assert gcd == _shrink(expected)
        gcd2, left, right = polynomial_extended_gcd(first, second)
        assert gcd2 == gcd
        assert _shrink(fps_add(fps_multiply(left, first), fps_multiply(right, second))) == gcd

    modulus = [1, 2, 0, 1]
    value = [3, 1]
    inverse = polynomial_inverse_mod(value, modulus)
    assert fps_remainder(fps_multiply(value, inverse), modulus) == [1]
    direct = [1]
    for _ in range(37):
        direct = fps_remainder(fps_multiply(direct, value), modulus)
    assert polynomial_pow_mod(value, 37, modulus) == direct
    assert polynomial_pow_mod(value, -1, modulus) == inverse


def test_resultant_against_sylvester_determinant():
    rng = random.Random(12)
    for _ in range(150):
        first = [rng.randrange(MOD) for _ in range(rng.randrange(1, 6))]
        second = [rng.randrange(MOD) for _ in range(rng.randrange(1, 6))]
        first[-1] = rng.randrange(1, MOD)
        second[-1] = rng.randrange(1, MOD)
        assert polynomial_resultant(first, second) == _sylvester_resultant(
            first, second, MOD
        )


def test_root_finding_distinct_and_multiplicity():
    for mod in (2, 3, 5, 17, 101):
        rng = random.Random(mod)
        for _ in range(30):
            roots = [rng.randrange(mod) for _ in range(8)]
            polynomial = [1]
            for root in roots:
                polynomial = fps_multiply(polynomial, [-root % mod, 1], mod)
            polynomial = fps_multiply(polynomial, [1, 0, 1], mod)
            brute = [x for x in range(mod) if fps_evaluate(polynomial, x, mod) == 0]
            assert polynomial_roots(polynomial, mod) == brute
            expected = roots + polynomial_roots([1, 0, 1], mod, True)
            assert polynomial_roots(polynomial, mod, True) == sorted(expected)

    roots = [2, 5, 7, 11, 13, 17]
    polynomial = [1]
    for root in roots:
        polynomial = fps_multiply(polynomial, [-root % MOD, 1])
    assert polynomial_roots(polynomial) == roots


def test_partial_fraction_and_power_sums():
    rng = random.Random(13)
    roots = rng.sample(range(1, 100), 25)
    numerator = [rng.randrange(MOD) for _ in range(25)]
    coefficients = partial_fraction_distinct(numerator, roots)
    for point in range(101, 140):
        denominator = 1
        right = 0
        for root, coefficient in zip(roots, coefficients):
            denominator = denominator * (point - root) % MOD
            right = (right + coefficient * pow(point - root, -1, MOD)) % MOD
        assert right * denominator % MOD == fps_evaluate(numerator, point)

    values = [rng.randrange(MOD) for _ in range(50)]
    actual = power_sums(values, 30)
    expected = [sum(pow(value, exponent, MOD) for value in values) % MOD
                for exponent in range(31)]
    assert actual == expected


def test_prefix_sum_powers_and_faulhaber_polynomial():
    for count in (0, 1, 2, 10, 123456789):
        actual = prefix_sum_powers(count, 20)
        if count < 100:
            expected = [
                sum(pow(value, exponent, MOD) for value in range(count)) % MOD
                for exponent in range(21)
            ]
            assert actual == expected
    assert prefix_sum_powers(123456789, 2) == [
        123456789,
        123456789 * (123456789 - 1) // 2 % MOD,
        123456789 * (123456789 - 1) * (2 * 123456789 - 1) // 6 % MOD,
    ]

    polynomial = [7, 3, 5, 11]
    exclusive = polynomial_prefix_sum(polynomial)
    inclusive = polynomial_prefix_sum(polynomial, inclusive=True)
    for count in range(30):
        direct = sum(fps_evaluate(polynomial, value) for value in range(count)) % MOD
        assert fps_evaluate(exclusive, count) == direct
        direct = (direct + fps_evaluate(polynomial, count)) % MOD
        assert fps_evaluate(inclusive, count) == direct
