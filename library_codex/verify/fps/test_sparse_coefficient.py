import random
import pytest
from library_codex.fps.SparseCoefficient import inv_coeff, log_coeff, exp_coeff, pow_coeff
from library_codex.fps.SparseFormalPowerSeries import sparse_inverse, sparse_logarithm, sparse_exponential, sparse_power


def test_coefficients_against_prefix_algorithms():
    rng = random.Random(356754)
    mod = 998244353
    for dimension in (1, 2, 3, 9):
        for index in (0, 1, 5, 64, 65, 200, 1000):
            f = [1] + [rng.randrange(mod) for _ in range(dimension)]
            assert inv_coeff(f, index) == sparse_inverse(f, index + 1)[index]
            assert log_coeff(f, index) == sparse_logarithm(f, index + 1)[index]
            exponent = 10000
            assert pow_coeff(f, exponent, index) == sparse_power(f, exponent, index + 1)[index]
            f[0] = 0
            assert exp_coeff(f, index) == sparse_exponential(f, index + 1)[index]


def test_shifted_powers_constants_and_modulus():
    assert inv_coeff([1, -1], 10**18) == 1
    assert pow_coeff([0, 0, 2, 3], 5, 10) == 32
    assert pow_coeff([0, 0, 2, 3], 5, 11) == 240
    assert pow_coeff([0, 0, 2, 3], 5, 9) == 0
    assert pow_coeff([], 0, 0) == 1
    assert pow_coeff([], 0, 1) == 0
    assert exp_coeff([], 0) == 1 and exp_coeff([], 100) == 0
    assert exp_coeff([0, 1], 100, 101) == 100
    assert log_coeff([1], 12, 101) == 0
    assert pow_coeff([2], 10**10, 1) == 0
    for call in (lambda: inv_coeff([0], 1), lambda: log_coeff([2], 1), lambda: exp_coeff([1], 1), lambda: pow_coeff([1], -1, 1), lambda: exp_coeff([0, 1], 101, 101)):
        with pytest.raises((ValueError, ZeroDivisionError)):
            call()


def test_matrix_branch_and_degree_compression():
    index = 2000101
    assert exp_coeff([0, 3, 5], index) == sparse_exponential([0, 3, 5], index + 1)[index]
    assert pow_coeff([1, 3, 5], 10**9, index) == sparse_power([1, 3, 5], 10**9, index + 1)[index]
    for fn, constant in ((inv_coeff, 1), (log_coeff, 1), (exp_coeff, 0)):
        assert fn([constant, 0, 3], 123) == 0
        assert fn([constant, 0, 3], 124) == fn([constant, 3], 62)
    assert pow_coeff([1, 0, 3], 100, 123) == 0
    assert pow_coeff([1, 0, 3], 100, 124) == pow_coeff([1, 3], 100, 62)
