"""添字の積を2の冪で割った余りごとに、係数の積を998244353で集計する。"""

from library_codex.convolution.NTT998 import ntt, intt


def _transform(values, powers, exponent):
    size = len(values)
    mask = size - 1
    mod = 998244353
    layers = []
    for shift in range(exponent - 1):
        width = size >> (shift + 2)
        positive = [values[(powers[i] << shift) & mask] % mod for i in range(width)]
        negative = [values[(-powers[i] << shift) & mask] % mod for i in range(width)]
        ntt(positive)
        ntt(negative)
        for i in range(width):
            a = positive[i]
            b = negative[i]
            positive[i] = (a + b) % mod
            negative[i] = (a - b) % mod
        layers.append((positive, negative))
    if exponent:
        layers.append(([values[size >> 1] % mod], [0]))
    layers.append(([values[0] % mod], [0]))
    return layers


def multiplicative_convolution_pow2(first, second):
    """同じ長さL=2^Nの列から、c[k]=Σ_{ij≡k (mod L)}a[i]b[j]を返す。"""
    size = len(first)
    if size == 0 or size & (size - 1) or len(second) != size:
        raise ValueError("both lengths must be the same positive power of two")
    if size > 1 << 25:
        raise ValueError("length exceeds 2^25")
    exponent = size.bit_length() - 1
    mask = size - 1
    mod = 998244353
    powers = [1] * max(1, size >> 2)
    for i in range(1, len(powers)):
        powers[i] = powers[i - 1] * 5 & mask
    left = _transform(first, powers, exponent)
    right = left if first is second else _transform(second, powers, exponent)
    result = [([0] * len(a), [0] * len(b)) for a, b in left]
    for i, (a, negative_a) in enumerate(left):
        for j, (b, negative_b) in enumerate(right):
            c, negative_c = result[min(exponent, i + j)]
            for k in range(len(c)):
                c[k] = (c[k] + a[k] * b[k]) % mod
                negative_c[k] = (negative_c[k] + negative_a[k] * negative_b[k]) % mod
    answer = [0] * size
    for shift in range(exponent - 1):
        positive, negative = result[shift]
        intt(positive)
        intt(negative)
        for i in range(len(positive)):
            a = positive[i]
            b = negative[i]
            answer[(powers[i] << shift) & mask] = (a + b) * 499122177 % mod
            answer[(-powers[i] << shift) & mask] = (a - b) * 499122177 % mod
    if exponent:
        answer[size >> 1] = result[exponent - 1][0][0]
    answer[0] = result[exponent][0][0]
    return answer
