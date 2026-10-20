from library_codex.benchmarks.baselines.binary_field_scalar import (
    _expand, _compress, _convert, _constants, _mul,
    multiply as _original,
)


def _pack(values, width):
    return [int.from_bytes(b"".join(v.to_bytes(112, "little")
                                   for v in values[i:i + width]), "little")
            for i in range(0, len(values), width)]


def _unpack(values, width):
    result = []
    for value in values:
        raw = value.to_bytes(112 * width, "little")
        result.extend(int.from_bytes(raw[i:i + 56], "little")
                      for i in range(0, len(raw), 112))
    return result


def _wide_transform(values, constants, width, inverse=False):
    parity = sum(1 << (896 * j + 7 * i)
                 for j in range(width) for i in range(128))
    low = sum(((1 << 448) - 1) << (896 * j) for j in range(width))
    reducer = 1 | 1 << 7 | 1 << 21 | 1 << 28
    height = (len(values) - 1).bit_length()
    levels = range(height) if inverse else range(height - 1, -1, -1)
    for level in levels:
        half = 1 << level
        for pos in range(half):
            values[pos + half] ^= values[pos]
        for start in range(half << 1, len(values), half << 1):
            scalar = constants[start >> (level + 1)]
            for pos in range(start, start + half):
                right = values[pos + half]
                if inverse:
                    right ^= values[pos]
                product = scalar * right & parity
                high = product >> 448 & low
                product = (product & low) ^ (high * reducer & parity)
                high = product >> 448 & low
                product = (product & low) ^ high ^ high << 7 ^ high << 21 ^ high << 28
                left = values[pos] ^ product
                values[pos] = left
                values[pos + half] = right if inverse else right ^ left


def _low_transform(values, constants, width, inverse=False):
    height = width.bit_length() - 1
    levels = range(height) if inverse else range(height - 1, -1, -1)
    for level in levels:
        half = 1 << level
        for start in range(0, len(values), half << 1):
            scalar = constants[start >> (level + 1)]
            for pos in range(start, start + half):
                right = values[pos + half]
                if inverse:
                    right ^= values[pos]
                left = values[pos] ^ _mul(scalar, right)
                values[pos] = left
                values[pos + half] = right if inverse else right ^ left


def multiply(first, second, width=16):
    if not first or not second or min(len(first), len(second)) <= 8:
        return _original(first, second)
    count = len(first) + len(second) - 1
    size = 1 << (count - 1).bit_length()
    width = min(width, size)
    a = list(first) + [0] * (size - len(first))
    b = list(second) + [0] * (size - len(second))
    _convert(a)
    _convert(b)
    constants = _constants(size)
    a = _pack([_expand(x) for x in a], width)
    b = _pack([_expand(x) for x in b], width)
    _wide_transform(a, constants, width)
    _wide_transform(b, constants, width)
    a = _unpack(a, width)
    b = _unpack(b, width)
    _low_transform(a, constants, width)
    _low_transform(b, constants, width)
    for i in range(size):
        a[i] = _mul(a[i], b[i])
    del b
    _low_transform(a, constants, width, True)
    a = _pack(a, width)
    _wide_transform(a, constants, width, True)
    a = [_compress(x) for x in _unpack(a, width)]
    _convert(a, True)
    return a[:count]
