"""GF(2^64)を係数とする多項式の積を、昇べき順の整数列で返す。

整数のbit iを体の生成元tのi乗の係数とし、t^64+t^4+t^3+t+1で割る。
係数の加算はXOR。整数mod 2^64やnim積の畳み込みではない。
"""

_SPREAD = tuple(
    (6 * width, sum(((1 << width) - 1) << (7 * start)
                    for start in range(0, 64, width)))
    for width in (32, 16, 8, 4, 2, 1)
)
_PARITY = sum(1 << (7 * i) for i in range(128))
_COMPRESS = tuple(
    (6 * width, sum(((1 << (2 * width)) - 1) << (7 * start)
                    for start in range(0, 64, 2 * width)))
    for width in (1, 2, 4, 8, 16, 32)
)
_LOW = (1 << 448) - 1
_REDUCER = 1 | 1 << 7 | 1 << 21 | 1 << 28
_BASIS = []


def _expand(value):
    if not 0 <= value < 1 << 64:
        raise ValueError("coefficients must be unsigned 64-bit integers")
    for shift, mask in _SPREAD:
        value = (value | value << shift) & mask
    return value


def _compress(value):
    for shift, mask in _COMPRESS:
        value = (value | value >> shift) & mask
    return value


def _mul(a, b):
    value = a * b & _PARITY
    high = value >> 448
    value = (value & _LOW) ^ (high * _REDUCER & _PARITY)
    high = value >> 448
    return (value & _LOW) ^ high ^ high << 7 ^ high << 21 ^ high << 28


def _basis():
    if not _BASIS:
        value = _expand(1 << 61)
        values = [value]
        for _ in range(63):
            value = _mul(value, value) ^ value
            values.append(value)
        _BASIS.extend(reversed(values))
    return _BASIS


def _convert(values, inverse=False):
    height = (len(values) - 1).bit_length()
    levels = range(1, height) if inverse else range(height - 1, 0, -1)
    for level in levels:
        half = 1 << level
        offsets = []
        subset = (level - 1) & level
        while True:
            offsets.append(half - (1 << subset))
            if subset == 0:
                break
            subset = (subset - 1) & level
        for start in range(0, len(values), half << 1):
            positions = (range(start + half, start + 2 * half) if inverse
                         else range(start + 2 * half - 1, start + half - 1, -1))
            for pos in positions:
                value = values[pos]
                for offset in offsets:
                    values[pos - offset] ^= value


def _transform(values, constants, inverse=False):
    height = (len(values) - 1).bit_length()
    levels = range(height) if inverse else range(height - 1, -1, -1)
    for level in levels:
        half = 1 << level
        for pos in range(half):
            values[pos + half] ^= values[pos]
        for start in range(half << 1, len(values), half << 1):
            scalar = constants[start >> (level + 1)]
            if inverse:
                for pos in range(start, start + half):
                    right = values[pos + half] ^ values[pos]
                    values[pos + half] = right
                    values[pos] ^= _mul(scalar, right)
            else:
                for pos in range(start, start + half):
                    left = values[pos] ^ _mul(scalar, values[pos + half])
                    values[pos + half] ^= left
                    values[pos] = left


def _constants(size):
    basis = _basis()
    constants = [0] * (size >> 1)
    for i in range(1, len(constants)):
        bit = i & -i
        constants[i] = constants[i ^ bit] ^ basis[bit.bit_length()]
    return constants


def _short_blocks(a, b):
    if len(a) > len(b):
        a, b = b, a
    n = len(a)
    block = 1 << (n - 1).bit_length()
    size = block << 1
    constants = _constants(size)
    a.extend([0] * (size - n))
    _convert(a)
    _transform(a, constants)
    result = [0] * (n + len(b) - 1)
    for start in range(0, len(b), block):
        count = min(block, len(b) - start)
        work = b[start:start + count] + [0] * (size - count)
        _convert(work)
        _transform(work, constants)
        for i in range(size):
            work[i] = _mul(work[i], a[i])
        _transform(work, constants, True)
        _convert(work, True)
        for i in range(n + count - 1):
            result[start + i] ^= work[i]
    return [_compress(value) for value in result]


def multiply(first, second):
    """GF(2^64)係数列の積を返す。入力は変更せず、末尾の0も保持する。"""

    if not first or not second:
        return []
    a = [_expand(value) for value in first]
    b = a if first is second else [_expand(value) for value in second]
    output_size = len(a) + len(b) - 1
    if a is b:
        result = [0] * output_size
        for i, value in enumerate(a):
            result[2 * i] = _compress(_mul(value, value))
        return result
    if min(len(a), len(b)) <= 8:
        if len(a) > len(b):
            a, b = b, a
        result = [0] * output_size
        for i, value in enumerate(a):
            if value:
                for j, other in enumerate(b):
                    result[i + j] ^= _mul(value, other)
        return [_compress(value) for value in result]
    if min(len(a), len(b)) * 4 <= max(len(a), len(b)):
        return _short_blocks(a, b)
    size = 1 << (output_size - 1).bit_length()
    if size > 1 << 64:
        raise ValueError("transform length exceeds the field size")
    constants = _constants(size)
    a.extend([0] * (size - len(a)))
    b.extend([0] * (size - len(b)))
    _convert(a)
    _convert(b)
    _transform(a, constants)
    _transform(b, constants)
    for i in range(size):
        a[i] = _mul(a[i], b[i])
    del b
    _transform(a, constants, True)
    _convert(a, True)
    del a[output_size:]
    return [_compress(value) for value in a]
