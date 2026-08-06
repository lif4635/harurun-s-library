"""素数法の乗法群上で畳み込みを計算する。"""

from library_codex.convolution.NTT import convolution, get_ntt, primitive_root

DEFAULT_MOD = 998244353

def multiplicative_convolution(first, second, prime, mod=DEFAULT_MOD):
    """h[k] = sum_{i*j=k (mod prime)} first[i]*second[j]."""
    if len(first) != prime or len(second) != prime:
        raise ValueError("arrays must have length prime")
    if prime == 2:
        return [
            (first[0] * second[0] + first[0] * second[1]
             + first[1] * second[0]) % mod,
            first[1] * second[1] % mod,
        ]
    generator = primitive_root(prime)
    length = prime - 1
    left = [0] * length
    right = [0] * length
    value = 1
    for exponent in range(length):
        left[exponent] = first[value] % mod
        right[exponent] = second[value] % mod
        value = value * generator % prime
    ordinary = convolution(left, right, mod)
    cyclic = ordinary[:length]
    for exponent in range(length, len(ordinary)):
        cyclic[exponent - length] = (
            cyclic[exponent - length] + ordinary[exponent]
        ) % mod
    answer = [0] * prime
    value = 1
    for exponent in range(length):
        answer[value] = cyclic[exponent]
        value = value * generator % prime
    sum_first = sum(first) % mod
    sum_second = sum(second) % mod
    answer[0] = (first[0] * sum_second + second[0] * sum_first
                 - first[0] * second[0]) % mod
    return answer
