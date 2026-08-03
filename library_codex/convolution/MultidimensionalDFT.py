"""多次元DFTと多変数循環畳み込みを計算する。"""

from library_codex.convolution.ChirpZ import chirp_z

from library_codex.convolution.NTT import convolution, get_ntt, primitive_root

DEFAULT_MOD = 998244353

def multidimensional_dft(values, base, inverse=False, mod=DEFAULT_MOD):
    """Mixed-radix multidimensional DFT; base[0] is the fastest axis."""
    size = 1
    for radix in base:
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
    if len(first) != len(second):
        raise ValueError("input lengths differ")
    left = multidimensional_dft(first, base, False, mod)
    right = multidimensional_dft(second, base, False, mod)
    for i in range(len(left)):
        left[i] = left[i] * right[i] % mod
    return multidimensional_dft(left, base, True, mod)

