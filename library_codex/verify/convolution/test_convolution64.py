import random

import pytest

from library_codex.convolution.Convolution64 import convolution_u64


def _naive(a, b):
    if not a or not b:
        return []
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return [x % (1 << 64) for x in result]


def test_empty_and_single():
    assert convolution_u64([], []) == []
    assert convolution_u64([1], []) == []
    assert convolution_u64([], [1]) == []
    assert convolution_u64([-1], [-1]) == [1]
    assert convolution_u64([1 << 64], [10]) == [0]
    assert convolution_u64([1, 2, 3], [4, 5]) == [4, 13, 22, 15]


def test_randomized_and_ntt_boundaries():
    rng = random.Random(456891)
    for n, m in [(1, 100), (32, 45), (33, 33), (63, 66), (128, 129), (256, 257)]:
        for _ in range(8):
            a = [rng.getrandbits(80) - (1 << 79) for _ in range(n)]
            b = [rng.getrandbits(80) - (1 << 79) for _ in range(m)]
            before = a[:], b[:]
            assert convolution_u64(a, b) == _naive(a, b)
            assert (a, b) == before


def test_full_width_coefficients_and_square():
    mask = (1 << 64) - 1
    for n in [33, 65, 513]:
        a = [mask] * n
        assert convolution_u64(a, a) == list(range(1, n + 1)) + list(range(n - 1, 0, -1))
        a = [mask if i & 1 else 1 << 63 for i in range(n)]
        assert convolution_u64(a, a) == _naive(a, a)
        assert convolution_u64([0] * n, a) == [0] * (2 * n - 1)


def test_capacity_and_crt_bound():
    product = 998244353 * 1012924417 * 1224736769 * 754974721 * 469762049
    assert product > (1 << 20) * ((1 << 64) - 1) ** 2
    for prime in [998244353, 1012924417, 1224736769, 754974721, 469762049]:
        assert (prime - 1) % (1 << 21) == 0
    with pytest.raises(ValueError, match=r'2\^21'):
        convolution_u64(range(1 << 21), [1, 2])


def test_largest_supported_transform():
    n = 1 << 20
    result = convolution_u64([(1 << 64) - 1] * n, [(1 << 64) - 1] * n)
    assert len(result) == 2 * n - 1
    assert all(value == min(i + 1, 2 * n - 1 - i) for i, value in enumerate(result))
