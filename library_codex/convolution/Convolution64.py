"""64bit整数の積和を、2**64を法として畳み込む。"""

from library_codex.convolution.NTT import convolution_ntt
from library_codex.convolution.NTT998 import multiply


def convolution_u64(first, second):
    """長さlen(first)+len(second)-1の積和を、各要素0以上2**64未満で返す。"""
    if not first or not second:
        return []
    length = len(first) + len(second) - 1
    if length > 1 << 21:
        raise ValueError("convolution length exceeds 2^21")
    mask = (1 << 64) - 1
    a = [value & mask for value in first]
    b = a if first is second else [value & mask for value in second]
    if min(len(a), len(b)) <= 32:
        if len(a) > len(b):
            a, b = b, a
        result = [0] * length
        for i, value in enumerate(a):
            for j, other in enumerate(b):
                result[i + j] = (result[i + j] + value * other) & mask
        return result
    result = multiply(a, b)
    product = 998244353
    for prime in (1012924417, 1224736769, 754974721, 469762049):
        residues = convolution_ntt(a, b, prime)
        inverse = pow(product, -1, prime)
        if prime == 469762049:
            for i in range(length):
                digit = (residues[i] - result[i]) * inverse % prime
                result[i] = (result[i] + product * digit) & mask
        else:
            for i in range(length):
                digit = (residues[i] - result[i]) * inverse % prime
                result[i] += product * digit
        product *= prime
    return result
