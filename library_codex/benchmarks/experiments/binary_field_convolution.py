from time import perf_counter


_MASK64 = (1 << 64) - 1
_SPREAD = tuple(
    (7 * width, sum(((1 << width) - 1) << (8 * start)
                    for start in range(0, 64, width)))
    for width in (32, 16, 8, 4, 2, 1)
)
_PARITY = sum(1 << (8 * i) for i in range(128))
_COMPRESS = tuple(
    (7 * width, sum(((1 << (2 * width)) - 1) << (8 * start)
                    for start in range(0, 128, 2 * width)))
    for width in (1, 2, 4, 8, 16, 32, 64)
)
_LOW = (1 << 512) - 1
_REDUCER = 1 | 1 << 8 | 1 << 24 | 1 << 32


def mul(a, b):
    for shift, mask in _SPREAD:
        a = (a | a << shift) & mask
        b = (b | b << shift) & mask
    value = a * b & _PARITY
    for shift, mask in _COMPRESS:
        value = (value | value >> shift) & mask
    high = value >> 64
    value = (value & _MASK64) ^ high ^ high << 1 ^ high << 3 ^ high << 4
    high = value >> 64
    return (value & _MASK64) ^ high ^ high << 1 ^ high << 3 ^ high << 4


def expand(value):
    for shift, mask in _SPREAD:
        value = (value | value << shift) & mask
    return value


def compress(value):
    for shift, mask in _COMPRESS:
        value = (value | value >> shift) & mask
    return value


def wide_mul(a, b):
    value = a * b & _PARITY
    high = value >> 512
    value = (value & _LOW) ^ (high * _REDUCER & _PARITY)
    high = value >> 512
    return (value & _LOW) ^ high ^ high << 8 ^ high << 24 ^ high << 32


def cantor_basis():
    for bit in range(64):
        values = [1 << bit]
        for _ in range(63):
            value = values[-1]
            values.append(mul(value, value) ^ value)
        if values[-1] == 1:
            return values[::-1]
    raise AssertionError("missing trace-one element")


def convert(values, inverse=False):
    height = (len(values) - 1).bit_length()
    levels = range(height) if inverse else range(height - 1, -1, -1)
    for level in levels:
        half = 1 << level
        offsets = []
        subset = (level - 1) & level
        while True:
            offsets.append(half - (1 << subset))
            if subset == 0:
                break
            subset = (subset - 1) & level
        if level == 0:
            continue
        for start in range(0, len(values), half << 1):
            positions = (range(start + half, start + 2 * half) if inverse
                         else range(start + 2 * half - 1, start + half - 1, -1))
            for pos in positions:
                value = values[pos]
                for offset in offsets:
                    values[pos - offset] ^= value


def transform(values, constants, inverse=False, product=mul):
    height = (len(values) - 1).bit_length()
    levels = range(height) if inverse else range(height - 1, -1, -1)
    for level in levels:
        half = 1 << level
        for start in range(0, len(values), half << 1):
            scalar = constants[start >> (level + 1)]
            if inverse:
                for pos in range(start, start + half):
                    right = values[pos + half] ^ values[pos]
                    values[pos + half] = right
                    if scalar:
                        values[pos] ^= product(scalar, right)
            else:
                for pos in range(start, start + half):
                    left = values[pos]
                    right = values[pos + half]
                    if scalar:
                        left ^= product(scalar, right)
                    values[pos] = left
                    values[pos + half] = left ^ right


def multiply(first, second, wide=False):
    if not first or not second:
        return []
    size = 1 << (len(first) + len(second) - 2).bit_length()
    basis = cantor_basis()
    constants = [0] * max(1, size // 2)
    for i in range(1, len(constants)):
        bit = i & -i
        constants[i] = constants[i ^ bit] ^ basis[bit.bit_length()]
    if wide:
        constants = [expand(x) for x in constants]
    a = ([expand(x) for x in first] if wide else list(first)) + [0] * (size - len(first))
    b = ([expand(x) for x in second] if wide else list(second)) + [0] * (size - len(second))
    product = wide_mul if wide else mul
    convert(a)
    convert(b)
    transform(a, constants, product=product)
    transform(b, constants, product=product)
    for i in range(size):
        a[i] = product(a[i], b[i])
    transform(a, constants, True, product=product)
    convert(a, True)
    result = a[:len(first) + len(second) - 1]
    return [compress(x) for x in result] if wide else result


def naive_mul(a, b):
    result = 0
    for i in range(64):
        if b >> i & 1:
            result ^= a << i
    for i in range(126, 63, -1):
        if result >> i & 1:
            result ^= ((1 << 64) | 27) << (i - 64)
    return result


if __name__ == "__main__":
    import random
    import sys

    rng = random.Random(92471)
    for _ in range(2000):
        a, b = rng.getrandbits(64), rng.getrandbits(64)
        assert mul(a, b) == naive_mul(a, b)
        assert compress(wide_mul(expand(a), expand(b))) == naive_mul(a, b)
    for n in range(1, 45):
        a = [rng.getrandbits(64) for _ in range(n)]
        b = [rng.getrandbits(64) for _ in range(n + 3)]
        expected = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                expected[i + j] ^= naive_mul(x, y)
        assert multiply(a, b) == expected, n
        assert multiply(a, b, True) == expected, n
    for log in map(int, sys.argv[1:]):
        a = [rng.getrandbits(64) for _ in range(1 << log)]
        b = [rng.getrandbits(64) for _ in range(1 << log)]
        started = perf_counter()
        result = multiply(a, b, True)
        print(log, perf_counter() - started, result[0], flush=True)
