import random

from library_codex.convolution.MinPlusConvolution import (
    minplus_conv,
    minplus_conv_convex,
    minplus_conv_concave,
)


def test_min_plus_convolution_against_brute():
    assert minplus_conv([], [1, 2]) == []
    assert minplus_conv([3], [4]) == [7]
    assert minplus_conv_convex([], [1, 2]) == []
    rng = random.Random(718934)
    for _ in range(5000):
        first = [rng.randrange(-100, 101) for _ in range(rng.randrange(1, 30))]
        differences = sorted(rng.randrange(-30, 31) for _ in range(rng.randrange(29)))
        second = [rng.randrange(-100, 101)]
        for difference in differences:
            second.append(second[-1] + difference)
        expected = [
            min(
                first[index] + second[total - index]
                for index in range(len(first))
                if 0 <= total - index < len(second)
            )
            for total in range(len(first) + len(second) - 1)
        ]
        assert minplus_conv(first, second) == expected
        values, indices = minplus_conv(first, second, return_argmin=True)
        assert values == expected
        assert all(
            values[total] == first[total - index] + second[index]
            for total, index in enumerate(indices)
        )
        first_convex = [rng.randrange(-100, 101)]
        differences = sorted(rng.randrange(-30, 31) for _ in range(rng.randrange(29)))
        for difference in differences:
            first_convex.append(first_convex[-1] + difference)
        expected = [
            min(
                first_convex[index] + second[total - index]
                for index in range(len(first_convex))
                if 0 <= total - index < len(second)
            )
            for total in range(len(first_convex) + len(second) - 1)
        ]
        assert minplus_conv_convex(first_convex, second) == expected


def test_concave_against_brute():
    rng = random.Random(904621)
    for _ in range(3000):
        a = [rng.randrange(-100, 101) for _ in range(rng.randrange(1, 55))]
        b = [rng.randrange(-100, 101)]
        for difference in sorted((rng.randrange(-25, 26) for _ in range(rng.randrange(54))), reverse=True):
            b.append(b[-1] + difference)
        expected = [min(a[k - j] + b[j] for j in range(max(0, k - len(a) + 1), min(k + 1, len(b))))
                    for k in range(len(a) + len(b) - 1)]
        original = a[:], b[:]
        assert minplus_conv_concave(a, b) == expected
        values, indices = minplus_conv_concave(a, b, True)
        assert values == expected
        assert all(0 <= j < len(b) and 0 <= k - j < len(a) and a[k - j] + b[j] == values[k]
                   for k, j in enumerate(indices))
        assert (a, b) == original


def test_concave_boundaries():
    assert minplus_conv_concave([], [1]) == []
    assert minplus_conv_concave([1], [], True) == ([], [])
    for n, m in ((1, 200), (200, 1), (100, 100), (201, 7), (7, 201)):
        a = [10**40] * n
        b = [-10**41] * m
        values, indices = minplus_conv_concave(a, b, True)
        assert values == [-9 * 10**40] * (n + m - 1)
        assert all(0 <= j < m and 0 <= k - j < n for k, j in enumerate(indices))
    assert minplus_conv_concave([4, -2, 9], [5, 7, 7, 4]) == [9, 3, 5, 5, 2, 13]
