from library_codex.benchmarks.baselines.binary_field_scalar import (
    _expand, _compress, _constants, _mul, _convert,
    multiply as _original,
)


def _transform(values, constants, inverse=False):
    height = (len(values) - 1).bit_length()
    levels = range(height & 1, height, 2) if inverse else range(height - 2, -1, -2)
    if inverse and height & 1:
        for start in range(0, len(values), 2):
            right = values[start + 1] ^ values[start]
            values[start + 1] = right
            values[start] ^= _mul(constants[start >> 1], right)
    for level in levels:
        half = 1 << level
        hi = constants[1]
        for pos in range(half):
            x0, x1 = values[pos], values[pos + half]
            x2, x3 = values[pos + 2 * half], values[pos + 3 * half]
            if inverse:
                x1 ^= x0
                x3 ^= x2
                x2 ^= _mul(hi, x3)
                x2 ^= x0
                x3 ^= x1
            else:
                x2 ^= x0
                x3 ^= x1
                x1 ^= x0
                x2 ^= _mul(hi, x3)
                x3 ^= x2
            values[pos], values[pos + half] = x0, x1
            values[pos + 2 * half], values[pos + 3 * half] = x2, x3
        for start in range(half << 2, len(values), half << 2):
            outer = constants[start >> (level + 2)]
            lo = constants[start >> (level + 1)]
            hi = constants[(start >> (level + 1)) + 1]
            for pos in range(start, start + half):
                x0, x1 = values[pos], values[pos + half]
                x2, x3 = values[pos + 2 * half], values[pos + 3 * half]
                if inverse:
                    x1 ^= x0
                    x3 ^= x2
                    x0 ^= _mul(lo, x1)
                    x2 ^= _mul(hi, x3)
                    x2 ^= x0
                    x3 ^= x1
                    x0 ^= _mul(outer, x2)
                    x1 ^= _mul(outer, x3)
                else:
                    x0 ^= _mul(outer, x2)
                    x1 ^= _mul(outer, x3)
                    x2 ^= x0
                    x3 ^= x1
                    x0 ^= _mul(lo, x1)
                    x2 ^= _mul(hi, x3)
                    x1 ^= x0
                    x3 ^= x2
                values[pos], values[pos + half] = x0, x1
                values[pos + 2 * half], values[pos + 3 * half] = x2, x3
    if not inverse and height & 1:
        for start in range(0, len(values), 2):
            left = values[start] ^ _mul(constants[start >> 1], values[start + 1])
            values[start + 1] ^= left
            values[start] = left


def multiply(first, second):
    if not first or not second or min(len(first), len(second)) <= 8:
        return _original(first, second)
    count = len(first) + len(second) - 1
    size = 1 << (count - 1).bit_length()
    a = [_expand(x) for x in first] + [0] * (size - len(first))
    b = [_expand(x) for x in second] + [0] * (size - len(second))
    constants = _constants(size)
    _convert(a)
    _convert(b)
    _transform(a, constants)
    _transform(b, constants)
    for i in range(size):
        a[i] = _mul(a[i], b[i])
    del b
    _transform(a, constants, True)
    _convert(a, True)
    return [_compress(x) for x in a[:count]]
