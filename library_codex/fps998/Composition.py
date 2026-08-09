"""998244353上でFPS合成と合成逆関数を計算する。

`fps_compose(outer, inner, degree)`は`outer(inner(x)) mod x^degree`、
`fps_compositional_inv(series, degree)`は`series(g(x))=x mod x^degree`
となる`g`の係数列を返す。
"""

from array import array

from library_codex.convolution.NTT998 import (
    MOD,
    _butterfly,
    _check_length,
    _intt,
)
from library_codex.fps998.FPS import fps_exp, fps_inv, fps_log
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


def _build_frequency_q(series, n, height, blocks):
    total = 4 * height * blocks
    frequency = [0] * total
    for block in range(blocks):
        source = block * height
        target = block * height * 2
        frequency[target:target + n + 1] = series[source:source + n + 1]
    frequency[blocks * height * 2] = (
        frequency[blocks * height * 2] + 1
    ) % MOD
    _butterfly(frequency)
    for index in range(0, total, 2):
        frequency[index], frequency[index + 1] = (
            frequency[index + 1], frequency[index]
        )
    return frequency


def _descend_q(series, n, height, blocks):
    frequency = _build_frequency_q(series, n, height, blocks)
    half_total = 2 * height * blocks
    reduced = [0] * half_total
    for index in range(half_total):
        reduced[index] = (
            frequency[index << 1] * frequency[index << 1 | 1] % MOD
        )
    _intt(reduced)
    reduced[0] = (reduced[0] - 1) % MOD
    child_height = height >> 1
    child = [0] * (height * blocks)
    child_degree = n >> 1
    for block in range(blocks << 1):
        source = block * height
        target = block * child_height
        child[target:target + child_degree + 1] = reduced[
            source:source + child_degree + 1
        ]
    return child, array("I", frequency)


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


def _ascend_p(child, frequency_q, n, height, blocks):
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
    _butterfly(frequency_p)
    _reverse_frequency_blocks(frequency_q)
    for index in range(total):
        frequency_p[index] = frequency_p[index] * frequency_q[index] % MOD
    _intt(frequency_p)
    result = [0] * (height * blocks)
    for block in range(blocks):
        source = block * height * 2
        target = block * height
        result[target:target + n + 1] = frequency_p[source:source + n + 1]
    return result


def _compose_ntt(outer, inner, degree):
    original_degree = degree - 1
    height = 1 << (degree - 1).bit_length()
    _check_length(height << 2)
    fixed_size = height
    outer_values = [value % MOD for value in outer[:degree]]
    outer_values.extend([0] * (degree - len(outer_values)))
    current = [0] * fixed_size
    for index, value in enumerate(inner[:degree]):
        current[index] = -value % MOD
    frames = []
    n = original_degree
    block_height = height
    blocks = 1
    while n:
        current, frequency_q = _descend_q(
            current, n, block_height, blocks
        )
        frames.append((frequency_q, n, block_height, blocks))
        n >>= 1
        block_height >>= 1
        blocks <<= 1

    denominator = current[:blocks]
    denominator.append(1)
    denominator.reverse()
    inverse = fps_inv(denominator, len(denominator))
    inverse.reverse()
    product = multiply(outer_values, inverse)
    result = [0] * fixed_size
    for index in range(degree):
        result[blocks - 1 - index] = product[index + blocks]

    while frames:
        frequency_q, n, block_height, blocks = frames.pop()
        result = _ascend_p(
            result, frequency_q, n, block_height, blocks
        )
    result = result[:degree]
    result.reverse()
    return result


def fps_compose(outer, inner, degree=None):
    """`outer(inner(x)) mod x^degree`の係数を`degree`個返す。O(N log^2 N)。"""

    if degree is None:
        degree = max(len(outer), len(inner))
    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if degree == 0:
        return []
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
    if inner[0] % MOD == 0 and inner[1] % MOD == 1 and len(inner) == 2:
        result = [value % MOD for value in outer[:degree]]
        result.extend([0] * (degree - len(result)))
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
