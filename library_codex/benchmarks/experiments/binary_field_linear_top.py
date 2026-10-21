"""GF(2^64)を係数とする多項式の積を、昇べき順の整数列で返す。

整数のbit iを体の生成元tのi乗の係数とし、t^64+t^4+t^3+t+1で割る。
係数の加算はXOR。整数mod 2^64やnim積の畳み込みではない。
"""

_SPREAD = tuple(
    (5 * width, sum(((1 << width) - 1) << (6 * start)
                    for start in range(0, 64, width)))
    for width in (32, 16, 8, 4, 2, 1)
)
_PARITY = sum(1 << (6 * i) for i in range(128))
_COMPRESS = tuple(
    (5 * width, sum(((1 << (2 * width)) - 1) << (6 * start)
                    for start in range(0, 64, 2 * width)))
    for width in (1, 2, 4, 8, 16, 32)
)
_LOW = (1 << 384) - 1
_REDUCER = 1 | 1 << 6 | 1 << 18 | 1 << 24
_BASIS = []
_ONES = sum(1 << (6 * i) for i in range(64))
_SQUARE = sum(1 << (12 * i) for i in range(64))
_FOLD = tuple(i ^ i << 6 ^ i << 18 ^ i << 24 for i in range(4162))


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
    value = _SQUARE if a == _ONES and b == _ONES else a * b & _PARITY
    high = value >> 384
    value = (value & _LOW) ^ (high * _REDUCER & _PARITY)
    high = value >> 384
    return (value & _LOW) ^ _FOLD[high]


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
            middle = start + half + (half >> 1)
            ranges = ((start + half, middle), (middle, start + 2 * half)) if inverse else (
                (middle, start + 2 * half), (start + half, middle))
            for begin, end in ranges:
                for offset in offsets:
                    for pos in range(begin, end):
                        values[pos - offset] ^= values[pos]


def _transform(values, constants, inverse=False, low=0, high=None, begin=0, end=None):
    if high is None:
        high = (len(values) - 1).bit_length()
    if end is None:
        end = len(values)
    odd = (high - low) & 1
    levels = range(low + odd, high, 2) if inverse else range(high - 2, low - 1, -2)
    if inverse and odd:
        half = 1 << low
        for start in range(begin, end, half << 1):
            constant = constants[start >> (low + 1)]
            for pos in range(start, start + half):
                right = values[pos + half] ^ values[pos]
                values[pos + half] = right
                values[pos] ^= _mul(constant, right)
    for level in levels:
        half = 1 << level
        hi = constants[1]
        for pos in range(half if begin == 0 else 0):
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
        for start in range(begin or half << 2, end, half << 2):
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
    if not inverse and odd:
        half = 1 << low
        for start in range(begin, end, half << 1):
            constant = constants[start >> (low + 1)]
            for pos in range(start, start + half):
                left = values[pos] ^ _mul(constant, values[pos + half])
                values[pos + half] ^= left
                values[pos] = left


def _linear(tables, value):
    if tables is None:
        return 0
    return (tables[0][value & 255] ^ tables[1][(value >> 8) & 255]
            ^ tables[2][(value >> 16) & 255] ^ tables[3][(value >> 24) & 255]
            ^ tables[4][(value >> 32) & 255] ^ tables[5][(value >> 40) & 255]
            ^ tables[6][(value >> 48) & 255] ^ tables[7][(value >> 56) & 255])


def _linear_tables(constants, count):
    result = [None]
    for constant in constants[1:count]:
        columns = []
        for shift in range(0, 64, 8):
            vectors = _signed([_compress(_mul(constant, _expand(1 << (shift + bit)))) for bit in range(8)])
            table = [0] * 256
            for i in range(1, 256):
                bit = i & -i
                table[i] = table[i ^ bit] ^ vectors[bit.bit_length() - 1]
            columns.append(table)
        result.append(columns)
    return result


def _linear_transform(values, constants, inverse=False, low=0, high=None, begin=0, end=None):
    if high is None:
        high = (len(values) - 1).bit_length()
    if end is None:
        end = len(values)
    odd = (high - low) & 1
    levels = range(low + odd, high, 2) if inverse else range(high - 2, low - 1, -2)
    if inverse and odd:
        half = 1 << low
        for start in range(begin, end, half << 1):
            constant = constants[start >> (low + 1)]
            for pos in range(start, start + half):
                right = values[pos + half] ^ values[pos]
                values[pos + half] = right
                values[pos] ^= _linear(constant, right)
    for level in levels:
        half = 1 << level
        hi = constants[1]
        for pos in range(half if begin == 0 else 0):
            x0, x1 = values[pos], values[pos + half]
            x2, x3 = values[pos + 2 * half], values[pos + 3 * half]
            if inverse:
                x1 ^= x0
                x3 ^= x2
                x2 ^= _linear(hi, x3)
                x2 ^= x0
                x3 ^= x1
            else:
                x2 ^= x0
                x3 ^= x1
                x1 ^= x0
                x2 ^= _linear(hi, x3)
                x3 ^= x2
            values[pos], values[pos + half] = x0, x1
            values[pos + 2 * half], values[pos + 3 * half] = x2, x3
        for start in range(begin or half << 2, end, half << 2):
            outer = constants[start >> (level + 2)]
            lo = constants[start >> (level + 1)]
            hi = constants[(start >> (level + 1)) + 1]
            for pos in range(start, start + half):
                x0, x1 = values[pos], values[pos + half]
                x2, x3 = values[pos + 2 * half], values[pos + 3 * half]
                if inverse:
                    x1 ^= x0
                    x3 ^= x2
                    x0 ^= _linear(lo, x1)
                    x2 ^= _linear(hi, x3)
                    x2 ^= x0
                    x3 ^= x1
                    x0 ^= _linear(outer, x2)
                    x1 ^= _linear(outer, x3)
                else:
                    x0 ^= _linear(outer, x2)
                    x1 ^= _linear(outer, x3)
                    x2 ^= x0
                    x3 ^= x1
                    x0 ^= _linear(lo, x1)
                    x2 ^= _linear(hi, x3)
                    x1 ^= x0
                    x3 ^= x2
                values[pos], values[pos + half] = x0, x1
                values[pos + 2 * half], values[pos + 3 * half] = x2, x3
    if not inverse and odd:
        half = 1 << low
        for start in range(begin, end, half << 1):
            constant = constants[start >> (low + 1)]
            for pos in range(start, start + half):
                left = values[pos] ^ _linear(constant, values[pos + half])
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


def _signed(values):
    result = []
    for value in values:
        if not 0 <= value < 1 << 64:
            raise ValueError("coefficients must be unsigned 64-bit integers")
        result.append(value if value < 1 << 63 else value - (1 << 64))
    return result


def multiply(first, second):
    """GF(2^64)係数列の積を返す。入力は変更せず、末尾の0も保持する。"""

    if not first or not second:
        return []
    a = _signed(first)
    b = a if first is second else _signed(second)
    output_size = len(a) + len(b) - 1
    if a is b or a == b:
        result = [0] * output_size
        for i, value in enumerate(a):
            value = _expand(value & ((1 << 64) - 1))
            result[2 * i] = _compress(_mul(value, value))
        return result
    short = min(len(a), len(b)) <= 8
    blocked = min(len(a), len(b)) * 4 <= max(len(a), len(b))
    if short or blocked:
        a = [_expand(value & ((1 << 64) - 1)) for value in a]
        b = [_expand(value & ((1 << 64) - 1)) for value in b]
    if short:
        if len(a) > len(b):
            a, b = b, a
        result = [0] * output_size
        for i, value in enumerate(a):
            if value:
                for j, other in enumerate(b):
                    result[i + j] ^= _mul(value, other)
        return [_compress(value) for value in result]
    if blocked:
        return _short_blocks(a, b)
    size = 1 << (output_size - 1).bit_length()
    if size > 1 << 64:
        raise ValueError("transform length exceeds the field size")
    constants = _constants(size)
    a.extend([0] * ((1 << (len(a) - 1).bit_length()) - len(a)))
    b.extend([0] * ((1 << (len(b) - 1).bit_length()) - len(b)))
    _convert(a)
    _convert(b)
    a.extend([0] * (size - len(a)))
    b.extend([0] * (size - len(b)))
    height = size.bit_length() - 1
    low = min(8, height)
    top = min(6, height - low)
    tables = _linear_tables(constants, 1 << max(0, top - 1))
    _linear_transform(a, tables, low=height-top, high=height)
    _linear_transform(b, tables, low=height-top, high=height)
    a = [_expand(value & ((1 << 64) - 1)) for value in a]
    b = [_expand(value & ((1 << 64) - 1)) for value in b]
    _transform(a, constants, low=low, high=height-top)
    _transform(b, constants, low=low, high=height-top)
    for begin in range(0, size, 1 << low):
        end = begin + (1 << low)
        _transform(a, constants, high=low, begin=begin, end=end)
        _transform(b, constants, high=low, begin=begin, end=end)
        for i in range(begin, end):
            a[i] = _mul(a[i], b[i])
        _transform(a, constants, True, high=low, begin=begin, end=end)
    del b
    _transform(a, constants, True, low=low, high=height-top)
    a = _signed([_compress(value) for value in a])
    _linear_transform(a, tables, True, low=height-top, high=height)
    _convert(a, True)
    del a[output_size:]
    return [value & ((1 << 64) - 1) for value in a]


import sys




def main():
    stream = sys.stdin.buffer
    n, m = map(int, stream.readline().split())
    a = list(map(int, stream.readline().split()))
    b = list(map(int, stream.readline().split()))
    if len(a) != n or len(b) != m:
        raise ValueError("unexpected number of coefficients")
    result = multiply(a, b)
    for start in range(0, len(result), 8192):
        if start:
            sys.stdout.write(" ")
        sys.stdout.write(" ".join(map(str, result[start:start + 8192])))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
