from library_codex.benchmarks.experiments.binary_field_fused import (
    _expand, _compress, _constants, _mul, _transform, _original,
)


def _convert(values, inverse=False):
    height = (len(values) - 1).bit_length()
    tasks = [(height, 1)]
    plan = []
    while tasks:
        level, width = tasks.pop()
        if level < 2:
            continue
        split = 1 << ((level - 1).bit_length() - 1)
        for step in range(level - 1, split - 1, -1):
            half = (1 << step) * width
            delta = (1 << (step - split)) * width
            plan.append((half * 2, delta, half, half - delta))
            plan.append((half * 2, delta, half * 2 - delta, delta))
            plan.append((half * 2, half, half * 2 - delta, delta))
        tasks.append((level - split, width << split))
        tasks.append((split, width))
    if inverse:
        plan.reverse()
    for period, target, source, count in plan:
        for start in range(0, len(values), period):
            offset = source - target
            for i in range(start + target, start + target + count):
                values[i] ^= values[i + offset]


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
