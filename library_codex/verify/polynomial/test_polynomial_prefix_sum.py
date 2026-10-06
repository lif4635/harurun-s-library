import random

import pytest

from library_codex.fps.FormalPowerSeries import fps_evaluate
from library_codex.polynomial.PolynomialPrefixSum import polynomial_prefix_sum


MOD = 998244353


def test_faulhaber_polynomial():
    polynomial = [7, 3, 5, 11]
    exclusive = polynomial_prefix_sum(polynomial)
    inclusive = polynomial_prefix_sum(polynomial, inclusive=True)
    for count in range(30):
        direct = sum(fps_evaluate(polynomial, value) for value in range(count)) % MOD
        assert fps_evaluate(exclusive, count) == direct
        direct = (direct + fps_evaluate(polynomial, count)) % MOD
        assert fps_evaluate(inclusive, count) == direct


def test_random_prefixes_and_boundaries():
    rng = random.Random(1206)
    for mod in (17, 101, MOD):
        for size in range(1, min(mod, 80)):
            polynomial = [rng.randrange(-mod, mod) for _ in range(size)]
            saved = polynomial[:]
            exclusive = polynomial_prefix_sum(polynomial, mod)
            inclusive = polynomial_prefix_sum(polynomial, mod, True)
            total = 0
            for point in range(size + 20):
                assert fps_evaluate(exclusive, point, mod) == total
                total = (total + fps_evaluate(polynomial, point, mod)) % mod
                assert fps_evaluate(inclusive, point, mod) == total
            assert polynomial == saved
    assert polynomial_prefix_sum([]) == []
    assert polynomial_prefix_sum([0, 0]) == []
    assert polynomial_prefix_sum([7, 0, 0]) == [0, 7]
    with pytest.raises(ValueError):
        polynomial_prefix_sum([1] * 17, 17)
