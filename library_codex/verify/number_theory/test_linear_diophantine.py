import random

import pytest

from library_codex.number_theory.LinearDiophantine import LinearDiophantine


def test_exhaustive_coefficients():
    for a in range(-4, 5):
        for b in range(-4, 5):
            for c in range(-10, 11):
                result = LinearDiophantine(a, b, c, -4, 5, -4, 5)
                expected = [(x, y) for x in range(-4, 5) for y in range(-4, 5) if a * x + b * y == c]
                assert result.count == len(expected)
                assert [result.kth(i) for i in range(result.count)] == expected


def test_random_rectangles_and_huge_counts():
    rng = random.Random(90)
    for _ in range(1000):
        a, b, c = [rng.randrange(-12, 13) for _ in range(3)]
        xl, xr = sorted(rng.choices(range(-8, 9), k=2))
        yl, yr = sorted(rng.choices(range(-8, 9), k=2))
        result = LinearDiophantine(a, b, c, xl, xr, yl, yr)
        expected = [(x, y) for x in range(xl, xr) for y in range(yl, yr) if a * x + b * y == c]
        assert [result.kth(i) for i in range(result.count)] == expected
    result = LinearDiophantine(0, 0, 0, 0, 10**30, 0, 10**30)
    assert result.count == 10**60
    assert result.kth(result.count - 1) == (10**30 - 1, 10**30 - 1)
    assert "count=" in repr(result)
    with pytest.raises(IndexError):
        result.kth(-1)
    with pytest.raises(IndexError):
        result.kth(result.count)
    with pytest.raises(ValueError):
        LinearDiophantine(1, 2, 3, 1, 0, 0, 1)
