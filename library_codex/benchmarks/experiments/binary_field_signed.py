from library_codex.benchmarks.experiments.binary_field_split import (
    _expand, _compress, _constants, _mul, _convert, _transform, _original,
)


def _signed(values):
    result = []
    for value in values:
        if not 0 <= value < 1 << 64:
            raise ValueError("coefficients must be unsigned 64-bit integers")
        result.append(value if value < 1 << 63 else value - (1 << 64))
    return result


def multiply(first, second):
    if not first or not second or min(len(first), len(second)) <= 8:
        return _original(first, second)
    count = len(first) + len(second) - 1
    size = 1 << (count - 1).bit_length()
    a, b = _signed(first), _signed(second)
    a.extend([0] * ((1 << (len(a) - 1).bit_length()) - len(a)))
    b.extend([0] * ((1 << (len(b) - 1).bit_length()) - len(b)))
    _convert(a)
    _convert(b)
    a = [_expand(x & ((1 << 64) - 1)) for x in a]
    b = [_expand(x & ((1 << 64) - 1)) for x in b]
    constants = _constants(size)
    a.extend([0] * (size - len(a)))
    b.extend([0] * (size - len(b)))
    _transform(a, constants)
    _transform(b, constants)
    for i in range(size):
        a[i] = _mul(a[i], b[i])
    del b
    _transform(a, constants, True)
    a = _signed([_compress(x) for x in a])
    _convert(a, True)
    return [x & ((1 << 64) - 1) for x in a[:count]]
