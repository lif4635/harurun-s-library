"""998244353上でFPS合成と合成逆関数を計算する。

`fps_compose(outer, inner, degree)`は`outer(inner(x)) mod x^degree`、
`fps_compositional_inv(series, degree)`は`series(g(x))=x mod x^degree`
となる`g`の係数列を返す。
"""

from array import array

from library_codex.convolution.NTT998 import (
    MOD,
    _butterfly,
    _butterfly_inv,
    _check_length,
    _ntt_plan,
)
from library_codex.fps998.FPS import fps_exp, fps_log, taylor_shift
from library_codex.fps998.PowerProjection import power_coefficient
from library_codex.convolution.NTT998 import multiply


def _add_constant(series, value):
    if series:
        series[0] = (series[0] + value) % MOD
    else:
        series.append(value % MOD)


def _compose_naive(outer, inner, degree):
    result = []
    inner = [value % MOD for value in inner[:degree]]
    for coefficient in reversed(outer[:degree]):
        result = multiply(result, inner)[:degree]
        _add_constant(result, coefficient)
    result.extend([0] * (degree - len(result)))
    return result


def _build_frequency_q(series, height, blocks, tables):
    total = 4 * height * blocks
    frequency = [0] * total
    for block in range(blocks):
        source = block * height
        target = block * height * 2
        frequency[target:target + height] = series[source:source + height]
    frequency[blocks * height * 2] = (
        frequency[blocks * height * 2] + 1
    ) % MOD
    _butterfly(frequency, tables)
    return frequency


def _descend_q(series, height, blocks, tables, inverse_tables):
    frequency = _build_frequency_q(series, height, blocks, tables)
    half_total = 2 * height * blocks
    reduced = [0] * half_total
    for index in range(half_total):
        reduced[index] = (
            frequency[index << 1] * frequency[index << 1 | 1] % MOD
        )
    _butterfly_inv(reduced, inverse_tables, height >> 1)
    scale = pow(half_total, MOD - 2, MOD)
    child_height = height >> 1
    child = [0] * (height * blocks)
    for block in range(blocks << 1):
        source = block * height
        target = block * child_height
        for index in range(child_height):
            child[target + index] = reduced[source + index] * scale % MOD
    child[0] = (child[0] - 1) % MOD
    return child, array("I", frequency)


def _ascend_p(child, frequency_q, height, blocks, tables, inverse_tables):
    total = len(frequency_q)
    half = total >> 1
    reduced = [0] * half
    child_height = height >> 1
    for block in range(blocks << 1):
        source = block * child_height
        target = block * height
        reduced[target:target + child_height] = child[source:source + child_height]
    _butterfly(reduced, tables)
    frequency_p = [0] * total
    for index in range(half):
        value = reduced[index]
        frequency_p[index << 1] = value * frequency_q[index << 1 | 1] % MOD
        frequency_p[index << 1 | 1] = value * frequency_q[index << 1] % MOD
    _butterfly_inv(frequency_p, inverse_tables, height)
    scale = pow(total, MOD - 2, MOD)
    result = [0] * (height * blocks)
    for block in range(blocks):
        source = half + block * height * 2
        target = block * height
        for index in range(height):
            result[target + index] = frequency_p[source + index] * scale % MOD
    return result


def _compose_ntt(outer, inner, degree):
    height = 1 << (degree - 1).bit_length()
    _check_length(height << 2)
    outer_values = [value % MOD for value in outer[:degree]]
    if inner[0] % MOD:
        outer_values = taylor_shift(outer_values, inner[0] % MOD)
    outer_values.extend([0] * (height - len(outer_values)))
    current = [0] * height
    for index, value in enumerate(inner[:degree]):
        current[index] = -value % MOD
    current[0] = 0
    tables = _ntt_plan(height << 2)
    inverse_tables = _ntt_plan(height << 2, True)
    frames = []
    block_height = height
    blocks = 1
    while block_height > 1:
        current, frequency_q = _descend_q(
            current, block_height, blocks, tables, inverse_tables
        )
        frames.append((frequency_q, block_height, blocks))
        block_height >>= 1
        blocks <<= 1

    result = outer_values
    while frames:
        frequency_q, block_height, blocks = frames.pop()
        result = _ascend_p(
            result, frequency_q, block_height, blocks, tables, inverse_tables
        )
    return result[:degree]


def fps_compose(outer, inner, degree=None):
    """`outer(inner(x)) mod x^degree`の係数を`degree`個返す。O(N log^2 N)。"""

    if degree is None:
        degree = max(len(outer), len(inner))
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return []
    outer_end = min(len(outer), degree)
    inner_end = min(len(inner), degree)
    while outer_end and outer[outer_end - 1] % MOD == 0:
        outer_end -= 1
    while inner_end and inner[inner_end - 1] % MOD == 0:
        inner_end -= 1
    outer = outer[:outer_end]
    inner = inner[:inner_end]
    if not outer:
        return [0] * degree
    if len(outer) == 1:
        return [outer[0] % MOD] + [0] * (degree - 1)
    if len(inner) <= 1:
        point = inner[0] % MOD if inner else 0
        value = 0
        for coefficient in reversed(outer[:degree]):
            value = (value * point + coefficient) % MOD
        return [value] + [0] * (degree - 1)
    if inner[0] % MOD == 0:
        first = 1
        while first < len(inner) and inner[first] % MOD == 0:
            first += 1
        if first == len(inner) - 1:
            value = inner[first] % MOD
            if first == 1 and value == 1:
                result = [coefficient % MOD for coefficient in outer]
                result.extend([0] * (degree - len(result)))
                return result
            result = [0] * degree
            power = 1
            for index in range(min(len(outer), (degree - 1) // first + 1)):
                result[index * first] = outer[index] * power % MOD
                power = power * value % MOD
            return result
    if degree <= 64:
        return _compose_naive(outer, inner, degree)
    return _compose_ntt(outer, inner, degree)


def fps_compositional_inv(series, degree=None):
    """`series(g(x))=x mod x^degree`となる`g`の係数を返す。O(N log^2 N)。"""

    if degree is None:
        degree = len(series)
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return []
    if not series or series[0] % MOD:
        raise ValueError("compositional inverse requires series[0] = 0")
    if len(series) < 2 or series[1] % MOD == 0:
        raise ValueError("a nonzero linear coefficient is required")
    inverse_linear = pow(series[1] % MOD, MOD - 2, MOD)
    if degree == 1:
        return [0]
    last = min(len(series), degree) - 1
    while last > 1 and series[last] % MOD == 0:
        last -= 1
    if last == 1:
        return [0, inverse_linear] + [0] * (degree - 2)

    order = degree - 1
    source = [value % MOD for value in series[:degree]]
    source.extend([0] * (degree - len(source)))
    coefficients = power_coefficient(source, count=degree)

    inverses = [0] * degree
    inverses[1] = 1
    for index in range(2, degree):
        inverses[index] = (
            -(MOD // index) * inverses[MOD % index]
        ) % MOD
    for index in range(1, degree):
        coefficients[index] = (
            coefficients[index] * order * inverses[index]
        ) % MOD

    coefficients.reverse()
    scale = pow(coefficients[0], MOD - 2, MOD)
    for index in range(degree):
        coefficients[index] = coefficients[index] * scale % MOD

    exponent = -pow(order, MOD - 2, MOD) % MOD
    logarithm = fps_log(coefficients, degree - 1)
    for index in range(degree - 1):
        logarithm[index] = logarithm[index] * exponent % MOD
    result = fps_exp(logarithm, degree - 1)
    for index in range(degree - 1):
        result[index] = result[index] * inverse_linear % MOD
    return [0] + result
