import itertools
import math
import random

import pytest

from library_codex.fps.IncreasingSequences import (
    _cross,
    _count_fast,
    _staircase,
    count_increasing_sequences,
)


def test_increasing_sequences_against_brute_force():
    rng = random.Random(449)
    for size in range(1, 9):
        for _ in range(100):
            lower = [rng.randrange(-3, 5) for _ in range(size)]
            upper = [rng.randrange(-2, 7) for _ in range(size)]
            minimum = min(lower)
            maximum = max(upper)
            expected = 0
            for values in itertools.combinations_with_replacement(
                range(minimum, maximum), size
            ):
                if all(lower[i] <= values[i] < upper[i] for i in range(size)):
                    expected += 1
            assert count_increasing_sequences(
                lower, upper
            ) == expected


def _naive(lower, upper, mod=998244353):
    if not lower:
        return 1 % mod
    offset = min(lower)
    width = max(upper) - offset
    if width <= 0:
        return 0
    values = [int(lower[0] <= i + offset < upper[0]) for i in range(width)]
    for left, right in zip(lower[1:], upper[1:]):
        total = 0
        for i in range(width):
            total = (total + values[i]) % mod
            values[i] = total if left <= i + offset < right else 0
    return sum(values) % mod


def test_fast_small_staircases():
    rng = random.Random(786521)
    for n in range(1, 40):
        for _ in range(30):
            lower = sorted(rng.randrange(40) for _ in range(n))
            upper = sorted(rng.randrange(1, 60) for _ in range(n))
            if any(x >= y for x, y in zip(lower, upper)):
                continue
            offset = lower[0]
            assert _count_fast([x - offset for x in lower], [x - offset for x in upper]) == _naive(lower, upper)


def test_ntt_and_nonmonotone_bounds():
    rng = random.Random(61781)
    for n, width in [(63, 67), (65, 63), (127, 131), (256, 257), (513, 511)]:
        for _ in range(8):
            lower = sorted(rng.randrange(width // 2) for _ in range(n))
            upper = sorted(rng.randrange(width // 2 + 1, width) for _ in range(n))
            lower = [x + rng.randrange(-2, 3) for x in lower]
            upper = [x + rng.randrange(-2, 3) for x in upper]
            original = lower[:], upper[:]
            assert count_increasing_sequences(lower, upper) == _naive(lower, upper)
            assert (lower, upper) == original


def test_rectangles_narrow_corridors_and_translation():
    mod = 998244353
    for n, width in [(1, 5000), (5000, 1), (65, 67), (1000, 900)]:
        assert count_increasing_sequences([0] * n, [width] * n) == math.comb(n + width - 1, n) % mod
    for n in [1, 2, 100, 5000]:
        assert count_increasing_sequences(list(range(n)), list(range(1, n + 1))) == 1
    lower = [0] * 100 + list(range(100))
    upper = list(range(1, 101)) + [200] * 100
    answer = _naive(lower, upper)
    for shift in [-10 ** 20, 0, 10 ** 20]:
        assert count_increasing_sequences([x + shift for x in lower], [x + shift for x in upper]) == answer


def test_empty_invalid_and_other_moduli():
    assert count_increasing_sequences([], []) == 1
    assert count_increasing_sequences([], [], 1) == 0
    assert count_increasing_sequences([4, 0], [6, 2]) == 0
    assert count_increasing_sequences([2], [2]) == 0
    for mod in [1, 2, 7, 12, 1000000007]:
        lower, upper = [0] * 65, [70] * 65
        assert count_increasing_sequences(lower, upper, mod) == math.comb(134, 65) % mod
    with pytest.raises(ValueError):
        count_increasing_sequences([1], [])
    with pytest.raises(ValueError):
        count_increasing_sequences([], [], 0)
    with pytest.raises(ValueError, match=r"2\^22"):
        count_increasing_sequences([0, 0], [1 << 22, 1 << 22])
    assert count_increasing_sequences([-10 ** 30], [10 ** 30]) == 2 * 10 ** 30 % 998244353


def test_middle_transfer_has_no_cyclic_wraparound():
    mod = 998244353
    factorial = [1] * 600
    for i in range(1, len(factorial)):
        factorial[i] = factorial[i - 1] * i % mod
    inverse = [pow(x, -1, mod) for x in factorial]
    rng = random.Random(562731)
    for size, length in [(1, 500), (500, 1), (32, 65), (33, 33), (64, 65), (129, 128)]:
        values = [rng.randrange(mod) for _ in range(size)]
        expected = [sum(value * math.comb(size - 1 - j + i, i)
                        for j, value in enumerate(values)) % mod for i in range(length)]
        assert _cross(values, length, factorial, inverse) == expected


def test_weighted_staircase_against_grid_dp():
    mod = 998244353
    factorial = [1] * 4096
    for i in range(1, len(factorial)):
        factorial[i] = factorial[i - 1] * i % mod
    inverse = [1] * len(factorial)
    inverse[-1] = pow(factorial[-1], -1, mod)
    for i in range(len(factorial) - 1, 0, -1):
        inverse[i - 1] = inverse[i] * i % mod
    rng = random.Random(816297)
    for n, height in [(3, 2000), (15, 513), (33, 256), (128, 129), (513, 15)]:
        for _ in range(10):
            heights = sorted(rng.randrange(height + 1) for _ in range(n))
            start = [rng.randrange(mod) for _ in range(n)]
            expected = [0] * (heights[-1] + 1)
            for limit, value in zip(heights, start):
                for i in range(limit + 1):
                    value = (value + expected[i]) % mod
                    expected[i] = value
            assert _staircase(heights, start, factorial, inverse) == expected
