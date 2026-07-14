from math import isqrt

from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_derivative,
    fps_inverse,
    fps_multiply,
)
from library_codex.convolution.NTT import get_ntt


def _add_constant(series, value, mod):
    if series:
        series[0] = (series[0] + value) % mod
    else:
        series.append(value % mod)


def _compose_naive(outer, inner, degree, mod):
    result = []
    inner = [value % mod for value in inner[:degree]]
    for coefficient in reversed(outer[:degree]):
        result = fps_multiply(result, inner, mod)[:degree]
        _add_constant(result, coefficient, mod)
    result.extend([0] * (degree - len(result)))
    return result


def _compose_brent_kung(outer, inner, degree, mod):
    block = isqrt(degree) + 1
    inner = [value % mod for value in inner[:degree]]
    baby = [[1]]
    for _ in range(1, block):
        baby.append(fps_multiply(baby[-1], inner, mod)[:degree])
    giant = fps_multiply(baby[-1], inner, mod)[:degree]
    group_count = (min(len(outer), degree) + block - 1) // block
    groups = []
    for group in range(group_count):
        current = [0] * degree
        start = group * block
        end = min(start + block, len(outer), degree)
        for index in range(start, end):
            coefficient = outer[index] % mod
            if coefficient == 0:
                continue
            power = baby[index - start]
            for position, value in enumerate(power):
                current[position] = (
                    current[position] + coefficient * value
                ) % mod
        while current and current[-1] == 0:
            current.pop()
        groups.append(current)
    result = []
    for group in range(len(groups) - 1, -1, -1):
        result = fps_multiply(result, giant, mod)[:degree]
        current = groups[group]
        if len(result) < len(current):
            result.extend([0] * (len(current) - len(result)))
        for index, value in enumerate(current):
            result[index] = (result[index] + value) % mod
    result.extend([0] * (degree - len(result)))
    return result


def _build_frequency_q(series, n, height, blocks, transform):
    total = 4 * height * blocks
    frequency = [0] * total
    for block in range(blocks):
        source = block * height
        target = block * height * 2
        frequency[target:target + n + 1] = series[source:source + n + 1]
    frequency[blocks * height * 2] = (
        frequency[blocks * height * 2] + 1
    ) % transform.mod
    transform.butterfly(frequency)
    for index in range(0, total, 2):
        frequency[index], frequency[index + 1] = (
            frequency[index + 1], frequency[index]
        )
    return frequency


def _descend_q(series, n, height, blocks, transform):
    frequency = _build_frequency_q(
        series, n, height, blocks, transform
    )
    half_total = 2 * height * blocks
    reduced = [0] * half_total
    for index in range(half_total):
        reduced[index] = (
            frequency[index << 1] * frequency[index << 1 | 1]
            % transform.mod
        )
    transform.butterfly_inv(reduced)
    reduced[0] = (reduced[0] - 1) % transform.mod
    child_height = height >> 1
    child = [0] * (height * blocks)
    child_degree = n >> 1
    for block in range(blocks << 1):
        source = block * height
        target = block * child_height
        child[target:target + child_degree + 1] = reduced[
            source:source + child_degree + 1
        ]
    return child


def _reverse_frequency_blocks(values):
    start = 1
    while start < len(values):
        left = start
        right = (start << 1) - 1
        while left < right:
            values[left], values[right] = values[right], values[left]
            left += 1
            right -= 1
        start <<= 1


def _ascend_p(child, series, n, height, blocks, transform):
    frequency_q = _build_frequency_q(
        series, n, height, blocks, transform
    )
    total = len(frequency_q)
    frequency_p = [0] * total
    child_height = height >> 1
    child_degree = n >> 1
    parity = n & 1
    for block in range(blocks << 1):
        source = block * child_height
        target = block * height * 2 + parity
        for index in range(child_degree + 1):
            frequency_p[target + (index << 1)] = child[source + index]
    transform.butterfly(frequency_p)
    _reverse_frequency_blocks(frequency_q)
    mod = transform.mod
    for index in range(total):
        frequency_p[index] = frequency_p[index] * frequency_q[index] % mod
    transform.butterfly_inv(frequency_p)
    result = [0] * (height * blocks)
    for block in range(blocks):
        source = block * height * 2
        target = block * height
        result[target:target + n + 1] = frequency_p[source:source + n + 1]
    return result


def _compose_ntt(outer, inner, degree, mod, transform):
    original_degree = degree - 1
    height = 1
    while height < degree:
        height <<= 1
    transform._check_length(height << 2)
    fixed_size = height
    outer_values = [value % mod for value in outer[:degree]]
    outer_values.extend([0] * (degree - len(outer_values)))
    current = [0] * fixed_size
    for index, value in enumerate(inner[:degree]):
        current[index] = -value % mod
    frames = []
    n = original_degree
    block_height = height
    blocks = 1
    while n:
        frames.append((current, n, block_height, blocks))
        current = _descend_q(
            current, n, block_height, blocks, transform
        )
        n >>= 1
        block_height >>= 1
        blocks <<= 1

    denominator = current[:blocks]
    denominator.append(1)
    denominator.reverse()
    inverse = fps_inverse(denominator, len(denominator), mod)
    inverse.reverse()
    product = fps_multiply(outer_values, inverse, mod)
    result = [0] * fixed_size
    for index in range(degree):
        result[blocks - 1 - index] = product[index + blocks]

    while frames:
        series, n, block_height, blocks = frames.pop()
        result = _ascend_p(
            result, series, n, block_height, blocks, transform
        )
    result = result[:degree]
    result.reverse()
    return result


def fps_compose(outer, inner, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = max(len(outer), len(inner))
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return []
    if not outer:
        return [0] * degree
    if len(outer) == 1:
        return [outer[0] % mod] + [0] * (degree - 1)
    if len(inner) <= 1:
        point = inner[0] % mod if inner else 0
        value = 0
        for coefficient in reversed(outer[:degree]):
            value = (value * point + coefficient) % mod
        return [value] + [0] * (degree - 1)
    if (
        inner[0] % mod == 0
        and inner[1] % mod == 1
        and len(inner) == 2
    ):
        result = [value % mod for value in outer[:degree]]
        result.extend([0] * (degree - len(result)))
        return result
    if degree <= 64:
        return _compose_naive(outer, inner, degree, mod)
    height = 1 << (degree - 1).bit_length()
    try:
        transform = get_ntt(mod)
        transform._check_length(height << 2)
    except ValueError:
        return _compose_brent_kung(outer, inner, degree, mod)
    return _compose_ntt(outer, inner, degree, mod, transform)


def fps_compositional_inverse(series, degree=None, mod=DEFAULT_MOD):
    if degree is None:
        degree = len(series)
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return []
    if not series or series[0] % mod:
        raise ValueError("compositional inverse requires series[0] = 0")
    if len(series) < 2:
        raise ValueError("a nonzero linear coefficient is required")
    try:
        inverse_linear = pow(series[1] % mod, -1, mod)
    except ValueError as error:
        raise ZeroDivisionError("series[1] must be invertible") from error
    if degree == 1:
        return [0]
    last = min(len(series), degree) - 1
    while last > 1 and series[last] % mod == 0:
        last -= 1
    if last == 1:
        return [0, inverse_linear] + [0] * (degree - 2)
    result = [0, inverse_linear]
    current = 2
    derivative = fps_derivative(series, mod)
    while current < degree:
        target = min(current << 1, degree)
        composed = fps_compose(series, result, target, mod)
        composed.extend([0] * (target - len(composed)))
        composed[1] = (composed[1] - 1) % mod
        derivative_composed = fps_compose(
            derivative, result, target, mod
        )
        correction = fps_multiply(
            composed,
            fps_inverse(derivative_composed, target, mod),
            mod,
        )[:target]
        result.extend([0] * (target - len(result)))
        for index, value in enumerate(correction):
            result[index] = (result[index] - value) % mod
        current = target
    return result[:degree]


def composition(inner, outer, degree=None, mod=DEFAULT_MOD):
    return fps_compose(outer, inner, degree, mod)


Composition = composition
compositional_inverse = fps_compositional_inverse
CompositionInv = fps_compositional_inverse
