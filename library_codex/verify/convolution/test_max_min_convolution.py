import itertools
import random

from library_codex.convolution.MaxMinConvolution import max_min_conv, min_max_conv


def brute(a, b, maximize=True):
    if not a or not b:
        return []
    result = [None] * (len(a) + len(b) - 1)
    inside, outside = (min, max) if maximize else (max, min)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            value = inside(x, y)
            result[i + j] = value if result[i + j] is None else outside(result[i + j], value)
    return result


def test_exhaustive_small():
    arrays = [list(values) for size in range(4) for values in itertools.product((-1, 0, 1), repeat=size)]
    for a in arrays:
        for b in arrays:
            assert max_min_conv(a, b) == brute(a, b)
            assert min_max_conv(a, b) == brute(a, b, False)


def test_random_boundaries_and_non_numeric_values():
    rng = random.Random(6129)
    for n, m in ((1, 1024), (1024, 1), (31, 65), (64, 127), (128, 129), (500, 511)):
        a = [rng.randrange(-100, 100) for _ in range(n)]
        b = [rng.randrange(-100, 100) for _ in range(m)]
        original = a.copy(), b.copy()
        assert max_min_conv(a, b) == brute(a, b)
        assert min_max_conv(a, b) == brute(a, b, False)
        assert (a, b) == original
    assert max_min_conv("abc", "cba") == brute("abc", "cba")
    assert min_max_conv([float("inf"), 0], [0, -float("inf")]) == brute([float("inf"), 0], [0, -float("inf")], False)


def test_large_monotone_and_equal():
    n = 10000
    values = list(range(n))
    assert max_min_conv(values, values) == [i // 2 for i in range(2 * n - 1)]
    assert min_max_conv(values, values) == [(i + 1) // 2 for i in range(2 * n - 1)]
    assert max_min_conv([7] * n, [5] * n) == [5] * (2 * n - 1)


def test_benchmark_ntt_oracle():
    from library_codex.benchmarks.reference_algorithms import maxmin_ntt
    rng = random.Random(731)
    for n, m in ((0, 2), (1, 1), (2, 67), (65, 64), (129, 132)):
        a = [rng.randrange(-50, 50) for _ in range(n)]
        b = [rng.randrange(-50, 50) for _ in range(m)]
        assert maxmin_ntt(a, b) == brute(a, b)
