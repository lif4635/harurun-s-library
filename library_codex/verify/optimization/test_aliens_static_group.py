import itertools

import pytest

from library_codex.optimization.AliensTrick import aliens_trick
from library_codex.range_query.StaticRangeGroup import StaticRangeGroup


def test_aliens_trick_minimize_and_maximize():
    minimum = [(25, 0), (12, 1), (4, 2), (1, 3), (0, 4)]

    def solve_min(penalty):
        return min(
            ((base + penalty * count, -count, count) for base, count in minimum)
        )[::2]

    value, _ = aliens_trick(2, solve_min)
    assert value == 4

    maximum = [(0, 0), (7, 1), (12, 2), (15, 3), (16, 4)]

    def solve_max(penalty):
        value, count = max((base + penalty * count, count) for base, count in maximum)
        return value, count

    value, _ = aliens_trick(2, solve_max, minimize=False)
    assert value == 12

    with pytest.raises(ValueError):
        aliens_trick(10, solve_min, max_abs_penalty=8)


MOD = 101


def _op(first, second):
    return first[0] * second[0] % MOD, (first[0] * second[1] + first[1]) % MOD


def _inverse(value):
    inverse_a = pow(value[0], MOD - 2, MOD)
    return inverse_a, -inverse_a * value[1] % MOD


def test_static_range_group_noncommutative_affine_group():
    values = [(2, 3), (5, 7), (4, 9), (3, 8)]
    query = StaticRangeGroup(values, _op, _inverse, (1, 0))
    for left, right in itertools.combinations_with_replacement(range(len(values) + 1), 2):
        expected = (1, 0)
        for value in values[left:right]:
            expected = _op(expected, value)
        assert query.prod(left, right) == expected
    assert query.prefix(3) == _op(_op(values[0], values[1]), values[2])
    with pytest.raises(IndexError):
        query.prod(-1, 2)
