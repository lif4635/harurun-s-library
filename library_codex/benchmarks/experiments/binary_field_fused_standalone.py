"""GF(2^64)を係数とする多項式の積を、昇べき順の整数列で返す。

整数のbit iを体の生成元tのi乗の係数とし、t^64+t^4+t^3+t+1で割る。
係数の加算はXOR。整数mod 2^64やnim積の畳み込みではない。
"""
_convolution_binary_field_convolution_SPREAD = tuple(((6 * width, sum(((1 << width) - 1 << 7 * start for start in range(0, 64, width)))) for width in (32, 16, 8, 4, 2, 1)))
_convolution_binary_field_convolution_PARITY = sum((1 << 7 * i for i in range(128)))
_convolution_binary_field_convolution_COMPRESS = tuple(((6 * width, sum(((1 << 2 * width) - 1 << 7 * start for start in range(0, 64, 2 * width)))) for width in (1, 2, 4, 8, 16, 32)))
_convolution_binary_field_convolution_LOW = (1 << 448) - 1
_convolution_binary_field_convolution_REDUCER = 1 | 1 << 7 | 1 << 21 | 1 << 28
_convolution_binary_field_convolution_BASIS = []

def _convolution_binary_field_convolution_expand(value):
    if not 0 <= value < 1 << 64:
        raise ValueError('coefficients must be unsigned 64-bit integers')
    for (shift, mask) in _convolution_binary_field_convolution_SPREAD:
        value = (value | value << shift) & mask
    return value

def _convolution_binary_field_convolution_compress(value):
    for (shift, mask) in _convolution_binary_field_convolution_COMPRESS:
        value = (value | value >> shift) & mask
    return value

def _convolution_binary_field_convolution_mul(a, b):
    value = a * b & _convolution_binary_field_convolution_PARITY
    high = value >> 448
    value = value & _convolution_binary_field_convolution_LOW ^ high * _convolution_binary_field_convolution_REDUCER & _convolution_binary_field_convolution_PARITY
    high = value >> 448
    return value & _convolution_binary_field_convolution_LOW ^ high ^ high << 7 ^ high << 21 ^ high << 28

def _convolution_binary_field_convolution_basis():
    if not _convolution_binary_field_convolution_BASIS:
        value = _convolution_binary_field_convolution_expand(1 << 61)
        values = [value]
        for _ in range(63):
            value = _convolution_binary_field_convolution_mul(value, value) ^ value
            values.append(value)
        _convolution_binary_field_convolution_BASIS.extend(reversed(values))
    return _convolution_binary_field_convolution_BASIS

def _convolution_binary_field_convolution_convert(values, inverse=False):
    height = (len(values) - 1).bit_length()
    levels = range(1, height) if inverse else range(height - 1, 0, -1)
    for level in levels:
        half = 1 << level
        offsets = []
        subset = level - 1 & level
        while True:
            offsets.append(half - (1 << subset))
            if subset == 0:
                break
            subset = subset - 1 & level
        for start in range(0, len(values), half << 1):
            middle = start + half + (half >> 1)
            ranges = ((start + half, middle), (middle, start + 2 * half)) if inverse else ((middle, start + 2 * half), (start + half, middle))
            for (begin, end) in ranges:
                for offset in offsets:
                    for pos in range(begin, end):
                        values[pos - offset] ^= values[pos]

def _convolution_binary_field_convolution_transform(values, constants, inverse=False):
    height = (len(values) - 1).bit_length()
    levels = range(height & 1, height, 2) if inverse else range(height - 2, -1, -2)
    if inverse and height & 1:
        for start in range(0, len(values), 2):
            right = values[start + 1] ^ values[start]
            values[start + 1] = right
            values[start] ^= _convolution_binary_field_convolution_mul(constants[start >> 1], right)
    for level in levels:
        half = 1 << level
        hi = constants[1]
        for pos in range(half):
            (x0, x1) = (values[pos], values[pos + half])
            (x2, x3) = (values[pos + 2 * half], values[pos + 3 * half])
            if inverse:
                x1 ^= x0
                x3 ^= x2
                x2 ^= _convolution_binary_field_convolution_mul(hi, x3)
                x2 ^= x0
                x3 ^= x1
            else:
                x2 ^= x0
                x3 ^= x1
                x1 ^= x0
                x2 ^= _convolution_binary_field_convolution_mul(hi, x3)
                x3 ^= x2
            (values[pos], values[pos + half]) = (x0, x1)
            (values[pos + 2 * half], values[pos + 3 * half]) = (x2, x3)
        for start in range(half << 2, len(values), half << 2):
            outer = constants[start >> level + 2]
            lo = constants[start >> level + 1]
            hi = constants[(start >> level + 1) + 1]
            for pos in range(start, start + half):
                (x0, x1) = (values[pos], values[pos + half])
                (x2, x3) = (values[pos + 2 * half], values[pos + 3 * half])
                if inverse:
                    x1 ^= x0
                    x3 ^= x2
                    x0 ^= _convolution_binary_field_convolution_mul(lo, x1)
                    x2 ^= _convolution_binary_field_convolution_mul(hi, x3)
                    x2 ^= x0
                    x3 ^= x1
                    x0 ^= _convolution_binary_field_convolution_mul(outer, x2)
                    x1 ^= _convolution_binary_field_convolution_mul(outer, x3)
                else:
                    x0 ^= _convolution_binary_field_convolution_mul(outer, x2)
                    x1 ^= _convolution_binary_field_convolution_mul(outer, x3)
                    x2 ^= x0
                    x3 ^= x1
                    x0 ^= _convolution_binary_field_convolution_mul(lo, x1)
                    x2 ^= _convolution_binary_field_convolution_mul(hi, x3)
                    x1 ^= x0
                    x3 ^= x2
                (values[pos], values[pos + half]) = (x0, x1)
                (values[pos + 2 * half], values[pos + 3 * half]) = (x2, x3)
    if not inverse and height & 1:
        for start in range(0, len(values), 2):
            left = values[start] ^ _convolution_binary_field_convolution_mul(constants[start >> 1], values[start + 1])
            values[start + 1] ^= left
            values[start] = left

def _convolution_binary_field_convolution_constants(size):
    basis = _convolution_binary_field_convolution_basis()
    constants = [0] * (size >> 1)
    for i in range(1, len(constants)):
        bit = i & -i
        constants[i] = constants[i ^ bit] ^ basis[bit.bit_length()]
    return constants

def _convolution_binary_field_convolution_short_blocks(a, b):
    if len(a) > len(b):
        (a, b) = (b, a)
    n = len(a)
    block = 1 << (n - 1).bit_length()
    size = block << 1
    constants = _convolution_binary_field_convolution_constants(size)
    a.extend([0] * (size - n))
    _convolution_binary_field_convolution_convert(a)
    _convolution_binary_field_convolution_transform(a, constants)
    result = [0] * (n + len(b) - 1)
    for start in range(0, len(b), block):
        count = min(block, len(b) - start)
        work = b[start:start + count] + [0] * (size - count)
        _convolution_binary_field_convolution_convert(work)
        _convolution_binary_field_convolution_transform(work, constants)
        for i in range(size):
            work[i] = _convolution_binary_field_convolution_mul(work[i], a[i])
        _convolution_binary_field_convolution_transform(work, constants, True)
        _convolution_binary_field_convolution_convert(work, True)
        for i in range(n + count - 1):
            result[start + i] ^= work[i]
    return [_convolution_binary_field_convolution_compress(value) for value in result]

def multiply(first, second):
    """GF(2^64)係数列の積を返す。入力は変更せず、末尾の0も保持する。"""
    if not first or not second:
        return []
    a = [_convolution_binary_field_convolution_expand(value) for value in first]
    b = a if first is second else [_convolution_binary_field_convolution_expand(value) for value in second]
    output_size = len(a) + len(b) - 1
    if a is b or a == b:
        result = [0] * output_size
        for (i, value) in enumerate(a):
            result[2 * i] = _convolution_binary_field_convolution_compress(_convolution_binary_field_convolution_mul(value, value))
        return result
    if min(len(a), len(b)) <= 8:
        if len(a) > len(b):
            (a, b) = (b, a)
        result = [0] * output_size
        for (i, value) in enumerate(a):
            if value:
                for (j, other) in enumerate(b):
                    result[i + j] ^= _convolution_binary_field_convolution_mul(value, other)
        return [_convolution_binary_field_convolution_compress(value) for value in result]
    if min(len(a), len(b)) * 4 <= max(len(a), len(b)):
        return _convolution_binary_field_convolution_short_blocks(a, b)
    size = 1 << (output_size - 1).bit_length()
    if size > 1 << 64:
        raise ValueError('transform length exceeds the field size')
    constants = _convolution_binary_field_convolution_constants(size)
    a.extend([0] * ((1 << (len(a) - 1).bit_length()) - len(a)))
    b.extend([0] * ((1 << (len(b) - 1).bit_length()) - len(b)))
    _convolution_binary_field_convolution_convert(a)
    _convolution_binary_field_convolution_convert(b)
    a.extend([0] * (size - len(a)))
    b.extend([0] * (size - len(b)))
    _convolution_binary_field_convolution_transform(a, constants)
    _convolution_binary_field_convolution_transform(b, constants)
    for i in range(size):
        a[i] = _convolution_binary_field_convolution_mul(a[i], b[i])
    del b
    _convolution_binary_field_convolution_transform(a, constants, True)
    _convolution_binary_field_convolution_convert(a, True)
    del a[output_size:]
    return [_convolution_binary_field_convolution_compress(value) for value in a]
import sys

def main():
    stream = sys.stdin.buffer
    (n, m) = map(int, stream.readline().split())
    a = list(map(int, stream.readline().split()))
    b = list(map(int, stream.readline().split()))
    if len(a) != n or len(b) != m:
        raise ValueError('unexpected number of coefficients')
    result = multiply(a, b)
    for start in range(0, len(result), 8192):
        if start:
            sys.stdout.write(' ')
        sys.stdout.write(' '.join(map(str, result[start:start + 8192])))
    sys.stdout.write('\n')
if __name__ == '__main__':
    main()
