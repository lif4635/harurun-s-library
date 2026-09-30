"""多変数多項式を指定shapeの係数配列として乗算する。"""

from library_codex.convolution.NTT import convolution, get_ntt
from library_codex.convolution.NTT998 import multiply as _multiply998

DEFAULT_MOD = 998244353

def multivariate_multiplication(first, second, base, mod=DEFAULT_MOD):
    """Multiply dense multivariate polynomials truncated by each degree base."""
    if len(first) != len(second):
        raise ValueError("input lengths differ")
    size = 1
    for radix in base:
        if radix <= 0:
            raise ValueError("radices must be positive")
        size *= radix
    if len(first) != size:
        raise ValueError("input length must equal product(base)")
    return _multiply_prefix(first, second, base, mod, size)


def _multiply_prefix(first, second, base, mod, size):
    base = tuple(radix for radix in base if radix > 1)
    first = first[:size]
    second = second[:size]
    if not first or not second:
        return [0] * size
    dimensions = len(base)
    if dimensions == 0:
        return [first[0] * second[0] % mod]
    width = min(base[0], size)
    packed_size = len(first) + len(second) - 1 + ((len(first) - 1) // width + (len(second) - 1) // width) * (width - 1)
    if dimensions <= 2 and (mod != DEFAULT_MOD or packed_size <= 1 << 23):
        stride = 2 * width - 1
        left = [0] * (len(first) + (len(first) - 1) // width * (width - 1))
        right = [0] * (len(second) + (len(second) - 1) // width * (width - 1))
        for start in range(0, len(first), width):
            position = start // width * stride
            left[position:position + min(width, len(first) - start)] = first[start:start + width]
        for start in range(0, len(second), width):
            position = start // width * stride
            right[position:position + min(width, len(second) - start)] = second[start:start + width]
        product = _multiply998(left, right) if mod == DEFAULT_MOD else convolution(left, right, mod)
        result = [0] * size
        for start in range(0, size, width):
            position = start // width * stride
            count = min(width, size - start, max(0, len(product) - position))
            result[start:start + count] = product[position:position + count]
        return result
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
    for index, value in enumerate(first):
        left[chi[index]][index] = value % mod
    for index, value in enumerate(second):
        right[chi[index]][index] = value % mod
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

