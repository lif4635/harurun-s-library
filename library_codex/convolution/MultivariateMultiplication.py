"""多変数多項式を指定shapeの係数配列として乗算する。"""

from library_codex.convolution.NTT import convolution, get_ntt, primitive_root

DEFAULT_MOD = 998244353

def multivariate_multiplication(first, second, base, mod=DEFAULT_MOD):
    """Multiply dense multivariate polynomials truncated by each degree base."""
    if len(first) != len(second):
        raise ValueError("input lengths differ")
    size = 1
    for radix in base:
        size *= radix
    if len(first) != size:
        raise ValueError("input length must equal product(base)")
    dimensions = len(base)
    if dimensions == 0:
        return [first[0] * second[0] % mod]
    transform_size = 1
    while transform_size < size * 2:
        transform_size <<= 1
    chi = [0] * size
    for index in range(size):
        value = index
        total = 0
        for axis in range(dimensions - 1):
            value //= base[axis]
            total += value
        chi[index] = total % dimensions
    left = [[0] * transform_size for _ in range(dimensions)]
    right = [[0] * transform_size for _ in range(dimensions)]
    for index in range(size):
        group = chi[index]
        left[group][index] = first[index] % mod
        right[group][index] = second[index] % mod
    ntt = get_ntt(mod)
    for row in left:
        ntt.butterfly(row)
    for row in right:
        ntt.butterfly(row)
    scratch = [0] * dimensions
    for frequency in range(transform_size):
        for group in range(dimensions):
            scratch[group] = 0
        for i in range(dimensions):
            a = left[i][frequency]
            if a:
                for j in range(dimensions):
                    scratch[(i + j) % dimensions] += a * right[j][frequency]
        for group in range(dimensions):
            left[group][frequency] = scratch[group] % mod
    for row in left:
        ntt.butterfly_inv(row)
    return [left[chi[index]][index] for index in range(size)]

