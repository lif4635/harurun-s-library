from array import array
import sys

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
    words = array("Q", values)
    if sys.byteorder != "little":
        words.byteswap()
    packed = int.from_bytes(words.tobytes(), "little")
    for period, target, source, count in plan:
        pattern = (b"\0" * (source * 8) + b"\xff" * (count * 8)
                   + b"\0" * ((period - source - count) * 8))
        mask = int.from_bytes(pattern * (len(values) // period), "little")
        packed ^= (packed & mask) >> ((source - target) * 64)
    words = array("Q")
    words.frombytes(packed.to_bytes(len(values) * 8, "little"))
    if sys.byteorder != "little":
        words.byteswap()
    values[:] = words


def multiply(first, second):
    if not first or not second or min(len(first), len(second)) <= 8:
        return _original(first, second)
    count = len(first) + len(second) - 1
    size = 1 << (count - 1).bit_length()
    a = list(first) + [0] * (size - len(first))
    b = list(second) + [0] * (size - len(second))
    constants = _constants(size)
    _convert(a)
    _convert(b)
    a = [_expand(x) for x in a]
    b = [_expand(x) for x in b]
    _transform(a, constants)
    _transform(b, constants)
    for i in range(size):
        a[i] = _mul(a[i], b[i])
    del b
    _transform(a, constants, True)
    a = [_compress(x) for x in a]
    _convert(a, True)
    return a[:count]
