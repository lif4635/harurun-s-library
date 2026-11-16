import random

from library_codex.convolution.NTT998 import MOD, multiply
from library_codex.convolution.OrderedConvolution import ordered_conv


def brute(a, b):
    if not a or not b:
        return []
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j in range(i + 1, len(b)):
            result[i + j] += x * b[j]
    return [value % MOD for value in result]


def test_random_and_unequal_lengths():
    rng = random.Random(7281)
    for n in (0, 1, 2, 31, 32, 33, 63, 64, 65, 129, 300):
        for m in (0, 1, 2, 32, 33, 70, 129, 301):
            a = [rng.randrange(-2 * MOD, 2 * MOD) for _ in range(n)]
            b = [rng.randrange(-2 * MOD, 2 * MOD) for _ in range(m)]
            original = a.copy(), b.copy()
            assert ordered_conv(a, b) == brute(a, b)
            assert (a, b) == original


def test_partition_of_convolution():
    rng = random.Random(81)
    for n, m in ((1024, 2048), (4096, 97), (17, 4096), (8192, 8193)):
        a = [rng.randrange(MOD) for _ in range(n)]
        b = [rng.randrange(MOD) for _ in range(m)]
        forward, backward = ordered_conv(a, b), ordered_conv(b, a)
        for i in range(min(n, m)):
            forward[2 * i] += a[i] * b[i]
        assert [(x + y) % MOD for x, y in zip(forward, backward)] == multiply(a, b)
