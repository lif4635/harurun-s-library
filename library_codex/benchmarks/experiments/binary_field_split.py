from library_codex.benchmarks.experiments.binary_field_fused import (
    _expand, _compress, _constants, _mul, _transform, _original,
)


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


def multiply(first, second):
    if not first or not second or min(len(first), len(second)) <= 8:
        return _original(first, second)
    count = len(first) + len(second) - 1
    size = 1 << (count - 1).bit_length()
    a = [_expand(x) for x in first]
    b = [_expand(x) for x in second]
    a.extend([0] * ((1 << (len(a) - 1).bit_length()) - len(a)))
    b.extend([0] * ((1 << (len(b) - 1).bit_length()) - len(b)))
    constants = _constants(size)
    _convert(a)
    _convert(b)
    a.extend([0] * (size - len(a)))
    b.extend([0] * (size - len(b)))
    _transform(a, constants)
    _transform(b, constants)
    for i in range(size):
        a[i] = _mul(a[i], b[i])
    del b
    _transform(a, constants, True)
    _convert(a, True)
    return [_compress(x) for x in a[:count]]
