from array import array

from library_codex.convolution.NTT998 import MOD, _butterfly, _butterfly_inv
from library_codex.benchmarks.baselines.large_convolution_before_interleaving import (
    _convolution_large_convolution_multiply as _original,
)


def _multiply_interleaved(first, second, limit):
    count = len(first) + len(second) - 1
    size = 1 << (count - 1).bit_length()
    lanes = size // limit
    if lanes != 4:
        return _original(first, second)
    left, right = [], []
    for values, target in ((first, left), (second, right)):
        for lane in range(4):
            work = [x % MOD for x in values[lane::4]]
            work.extend([0] * (limit - len(work)))
            _butterfly(work)
            target.append(array("I", work))
    a0, a1, a2, a3 = left
    b0, b1, b2, b3 = right
    out = [array("I", [0]) * limit for _ in range(4)]
    c0, c1, c2, c3 = out
    root = pow(3, (MOD - 1) // limit, MOD)
    rates = [pow(root, (limit >> (j + 1)) - (limit - (limit >> j)), MOD)
             for j in range(limit.bit_length())]
    weight = 1
    for i in range(limit):
        x0, x1, x2, x3 = a0[i], a1[i], a2[i], a3[i]
        y0, y1, y2, y3 = b0[i], b1[i], b2[i], b3[i]
        c0[i] = (x0 * y0 + weight * ((x1 * y3 + x2 * y2 + x3 * y1) % MOD)) % MOD
        c1[i] = (x0 * y1 + x1 * y0 + weight * ((x2 * y3 + x3 * y2) % MOD)) % MOD
        c2[i] = (x0 * y2 + x1 * y1 + x2 * y0 + weight * (x3 * y3 % MOD)) % MOD
        c3[i] = (x0 * y3 + x1 * y2 + x2 * y1 + x3 * y0) % MOD
        weight = weight * rates[((i + 1) & -(i + 1)).bit_length() - 1] % MOD
    del left, right, a0, a1, a2, a3, b0, b1, b2, b3, work, target, c0, c1, c2, c3
    inverse = pow(limit, MOD - 2, MOD)
    result = [0] * count
    for lane in range(4):
        work = list(out[lane])
        out[lane] = None
        _butterfly_inv(work)
        for j in range((count - lane + 3) // 4):
            result[j * 4 + lane] = work[j] * inverse % MOD
    return result


def multiply(first, second):
    if not first or not second:
        return []
    if (len(first) + len(second) - 2).bit_length() != 25:
        return _original(first, second)
    return _multiply_interleaved(first, second, 1 << 23)
