from fractions import Fraction

from library_codex.math.RationalFormalPowerSeries import (
    RationalFormalPowerSeries as FPS,
)


def test_rational_fps_core_operations():
    series = FPS([1, 1, Fraction(1, 2), Fraction(1, 6), Fraction(1, 24)])
    logarithm = series.log(5)
    assert logarithm.coefficients == [0, 1, 0, 0, 0]
    assert FPS([0, 1]).exp(7).coefficients == [
        Fraction(1), Fraction(1), Fraction(1, 2), Fraction(1, 6),
        Fraction(1, 24), Fraction(1, 120), Fraction(1, 720),
    ]
    polynomial = FPS([1, 2, 3])
    inverse = polynomial.inv(10)
    product = (polynomial * inverse).pre(10).coefficients
    assert product == [1] + [0] * 9
    assert polynomial.pow(5, 20).coefficients == (
        polynomial * polynomial * polynomial * polynomial * polynomial
    ).pre(20).coefficients

