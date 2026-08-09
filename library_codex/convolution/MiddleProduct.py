"""2列の相関に当たるmiddle productを高速に計算する。"""

from library_codex.convolution.NTT import convolution, get_ntt

DEFAULT_MOD = 998244353

def middle_product(first, second, mod=DEFAULT_MOD):
    """Return c[i] = sum(second[j] * first[i+j]) modulo mod.

    The result has ``len(first) - len(second) + 1`` elements.  For
    998244353, the NTT length is only the next power of two at least
    ``len(first)``; coefficients outside the requested middle cannot wrap
    into the returned range.
    """
    first = list(first)
    second = list(second)
    first_size = len(first)
    second_size = len(second)
    if second_size == 0:
        raise ValueError("second must be nonempty")
    if first_size < second_size:
        raise ValueError("len(first) must be at least len(second)")

    output_size = first_size - second_size + 1
    if min(second_size, output_size) <= 60:
        return [
            sum(second[j] * first[i + j] for j in range(second_size)) % mod
            for i in range(output_size)
        ]

    if mod != DEFAULT_MOD:
        product = convolution(first, list(reversed(second)), mod)
        return product[second_size - 1:first_size]

    size = 1 << (first_size - 1).bit_length()
    left = [value % mod for value in first]
    left.extend([0] * (size - first_size))
    right = [value % mod for value in reversed(second)]
    right.extend([0] * (size - second_size))
    ntt = get_ntt(mod)
    ntt.butterfly(left)
    ntt.butterfly(right)
    for index in range(size):
        left[index] = left[index] * right[index] % mod
    ntt.butterfly_inv(left)
    return left[second_size - 1:first_size]
