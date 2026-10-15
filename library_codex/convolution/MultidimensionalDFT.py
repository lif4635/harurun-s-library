"""多次元DFTと多変数循環畳み込みを計算する。"""

from library_codex.convolution.ChirpZ import chirp_z

from library_codex.convolution.NTT import primitive_root

DEFAULT_MOD = 998244353

def multidimensional_dft(values, base, inverse=False, mod=DEFAULT_MOD):
    """各軸にDFTを適用する。base[0]の添字が最も速く変化する並び。"""
    if mod < 2:
        raise ValueError("mod must be prime")
    size = 1
    for radix in base:
        if radix <= 0:
            raise ValueError("radices must be positive")
        size *= radix
        if (mod - 1) % radix:
            raise ValueError("each radix must divide mod-1")
    if len(values) != size:
        raise ValueError("value length must equal product(base)")
    result = [value % mod for value in values]
    root = primitive_root(mod)
    axes = range(len(base) - 1, -1, -1) if inverse else range(len(base))
    stride = [1] * len(base)
    for axis in range(1, len(base)):
        stride[axis] = stride[axis - 1] * base[axis - 1]
    for axis in axes:
        length = base[axis]
        step = stride[axis]
        block = step * length
        ratio = pow(root, (mod - 1) // length, mod)
        if inverse:
            ratio = pow(ratio, -1, mod)
        if length == 1:
            continue
        if length == 2:
            for block_start in range(0, size, block):
                for position in range(block_start, block_start + step):
                    a = result[position]
                    b = result[position + step]
                    result[position] = (a + b) % mod
                    result[position + step] = (a - b) % mod
            continue
        if length == 3:
            square = ratio * ratio % mod
            for block_start in range(0, size, block):
                for position in range(block_start, block_start + step):
                    a = result[position]
                    b = result[position + step]
                    c = result[position + 2 * step]
                    result[position] = (a + b + c) % mod
                    result[position + step] = (a + b * ratio + c * square) % mod
                    result[position + 2 * step] = (a + b * square + c * ratio) % mod
            continue
        for block_start in range(0, size, block):
            for offset in range(step):
                positions = [block_start + offset + step * i
                             for i in range(length)]
                transformed = chirp_z(
                    [result[position] for position in positions],
                    ratio, length, 1, mod
                )
                for position, value in zip(positions, transformed):
                    result[position] = value
    if inverse and size:
        inverse_size = pow(size, -1, mod)
        for i in range(size):
            result[i] = result[i] * inverse_size % mod
    return result

def multivariate_circular_convolution(first, second, base,
                                      mod=DEFAULT_MOD):
    """各軸の指数をbase[i]で折り返して乗算した係数列を返す。"""
    if len(first) != len(second):
        raise ValueError("input lengths differ")
    left = multidimensional_dft(first, base, False, mod)
    right = multidimensional_dft(second, base, False, mod)
    for i in range(len(left)):
        left[i] = left[i] * right[i] % mod
    return multidimensional_dft(left, base, True, mod)

