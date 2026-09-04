import random

from library_codex.convolution.MinPlusConvolution import (
    minplus_conv,
    minplus_conv_convex,
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
