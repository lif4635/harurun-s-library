"""998244353上で部分集合・多重集合の重さ別個数を母関数から求める。

`counts[w]`を重さ`w`の種類数とし、返り値`result[s]`は総重さ`s`に
なる選び方の個数を表す。返す長さは`len(counts)`。
"""

from library_codex.convolution.NTT998 import MOD
from library_codex.fps998.FPS import fps_exp


_INVERSES = [0, 1]


def _extend_inverses(size):
    values = _INVERSES
    for index in range(len(values), size):
        values.append(-values[MOD % index] * (MOD // index) % MOD)
    return values


def subset_sum(counts):
    r"""`prod_(w>=1)(1+x^w)^counts[w]`の先頭`len(counts)`係数を返す。O(N log N)。"""

    size = len(counts)
    if size == 0:
        return []
    inverse = _extend_inverses(size)
    logarithm = [0] * size
    for weight in range(1, size):
        count = counts[weight] % MOD
        if count == 0:
            continue
        scaled = count * weight
        quotient = 1
        for total in range(weight, size, weight):
            value = scaled * inverse[total] % MOD
            if quotient & 1:
                logarithm[total] += value
            else:
                logarithm[total] -= value
            quotient += 1
    return fps_exp([value % MOD for value in logarithm], size)


def multiset_sum(counts):
    r"""`prod_(w>=1)(1-x^w)^(-counts[w])`の先頭`len(counts)`係数を返す。O(N log N)。"""

    size = len(counts)
    if size == 0:
        return []
    inverse = _extend_inverses(size)
    logarithm = [0] * size
    for weight in range(1, size):
        count = counts[weight] % MOD
        if count == 0:
            continue
        scaled = count * weight
        for total in range(weight, size, weight):
            logarithm[total] += scaled * inverse[total] % MOD
    return fps_exp([value % MOD for value in logarithm], size)
