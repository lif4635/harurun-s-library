"""Chirp-Z and multivariate convolution algorithms."""

from library_codex.convolution.NTT import convolution, get_ntt, primitive_root


DEFAULT_MOD = 998244353


def chirp_z(polynomial, ratio, count=None, start=1, mod=DEFAULT_MOD):
    """Return f(start*ratio^i) for i=0..count-1 by Bluestein."""
    polynomial = [value % mod for value in polynomial]
    if count is None:
        count = len(polynomial)
    if count < 0:
        raise ValueError("count must be nonnegative")
    if not polynomial or count == 0:
        return [0] * count
    if start % mod != 1:
        power = 1
        for i in range(len(polynomial)):
            polynomial[i] = polynomial[i] * power % mod
            power = power * start % mod
    ratio %= mod
    if ratio == 0:
        result = [polynomial[0]] * count
        result[0] = sum(polynomial) % mod
        return result
    length = len(polynomial)
    triangular = [1] * (count + length)
    inverse_triangular = [1] * max(count, length)
    step = 1
    for i in range(1, len(triangular)):
        triangular[i] = triangular[i - 1] * step % mod
        step = step * ratio % mod
    inverse_ratio = pow(ratio, -1, mod)
    step = 1
    for i in range(1, len(inverse_triangular)):
        inverse_triangular[i] = inverse_triangular[i - 1] * step % mod
        step = step * inverse_ratio % mod
    for i in range(length):
        polynomial[i] = polynomial[i] * inverse_triangular[i] % mod
    polynomial.reverse()
    product = convolution(polynomial, triangular, mod)
    return [product[length - 1 + i] * inverse_triangular[i] % mod
            for i in range(count)]


def middle_product(first, second, start, count, mod=DEFAULT_MOD):
    """A requested coefficient window of the ordinary convolution."""
    if count <= 0:
        return []
    product = convolution(first, second, mod)
    return [product[i] if 0 <= i < len(product) else 0
            for i in range(start, start + count)]


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


def multiplicative_convolution_mod_prime(first, second, prime,
                                         mod=DEFAULT_MOD):
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
