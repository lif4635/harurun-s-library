"""998244353上で多項式の冪に関する係数をまとめて列挙する。"""

from library_codex.convolution.NTT998 import (
    MOD,
    _butterfly,
    _intt,
    multiply,
)


def _power_projection_zero_constant(polynomial, weights, count):
    if not polynomial or not weights:
        return [0] * count
    original_size = len(weights)
    size = 1
    while size < original_size:
        size <<= 1
    degree = original_size - 1
    height = size
    blocks = 1
    numerator = [0] * height
    denominator = [0] * height
    padded_weights = [value % MOD for value in reversed(weights)]
    padded_weights.extend([0] * (size - original_size))
    numerator[:size] = padded_weights
    limit = min(len(polynomial), original_size)
    for index in range(1, limit):
        denominator[index] = -polynomial[index] % MOD
    while degree:
        total = 4 * height * blocks
        frequency_p = [0] * total
        frequency_q = [0] * total
        for block in range(blocks):
            source = block * height
            target = block * height * 2
            frequency_p[target:target + degree + 1] = numerator[
                source:source + degree + 1
            ]
            frequency_q[target:target + degree + 1] = denominator[
                source:source + degree + 1
            ]
        frequency_q[blocks * height * 2] = (
            frequency_q[blocks * height * 2] + 1
        ) % MOD
        _butterfly(frequency_p)
        _butterfly(frequency_q)
        reduced_q = [0] * (total >> 1)
        for index in range(0, total, 2):
            frequency_q[index], frequency_q[index + 1] = (
                frequency_q[index + 1], frequency_q[index]
            )
            frequency_p[index] = (
                frequency_p[index] * frequency_q[index]
            ) % MOD
            frequency_p[index + 1] = (
                frequency_p[index + 1] * frequency_q[index + 1]
            ) % MOD
            reduced_q[index >> 1] = (
                frequency_q[index] * frequency_q[index + 1]
            ) % MOD
        _intt(frequency_p)
        _intt(reduced_q)
        reduced_q[0] = (reduced_q[0] - 1) % MOD
        child_height = height >> 1
        child_degree = degree >> 1
        parity = degree & 1
        child_size = height * blocks
        child_p = [0] * child_size
        child_q = [0] * child_size
        for block in range(blocks << 1):
            source = block * height * 2
            target = block * child_height
            for index in range(child_degree + 1):
                child_p[target + index] = frequency_p[
                    source + (index << 1) + parity
                ]
                child_q[target + index] = reduced_q[
                    block * height + index
                ]
        numerator = child_p
        denominator = child_q
        degree >>= 1
        height >>= 1
        blocks <<= 1
    result = numerator[:blocks]
    result.reverse()
    result = result[:count]
    result.extend([0] * (count - len(result)))
    return result


def power_projection(polynomial, weights, count):
    r"""`result[i]=sum_j weights[j][x^j]polynomial(x)^i`を`0<=i<count`で返す。O(N log^2 N)。"""

    if count < 0:
        raise ValueError("count must be nonnegative")
    if count == 0:
        return []
    if not polynomial or not weights:
        return [0] * count
    constant = polynomial[0] % MOD
    shifted = list(polynomial)
    shifted[0] = 0
    result = _power_projection_zero_constant(shifted, weights, count)
    if constant == 0:
        return result
    factorial = [1] * count
    inverse_factorial = [1] * count
    for index in range(1, count):
        factorial[index] = factorial[index - 1] * index % MOD
    inverse_factorial[-1] = pow(factorial[-1], MOD - 2, MOD)
    for index in range(count - 1, 0, -1):
        inverse_factorial[index - 1] = inverse_factorial[index] * index % MOD
    coefficient = [0] * count
    power = 1
    for index in range(count):
        result[index] = result[index] * inverse_factorial[index] % MOD
        coefficient[index] = inverse_factorial[index] * power % MOD
        power = power * constant % MOD
    result = multiply(result, coefficient)[:count]
    result.extend([0] * (count - len(result)))
    return [result[index] * factorial[index] % MOD for index in range(count)]


def power_coefficient(polynomial, multiplier=None, count=None):
    r"""`[x^n]polynomial(x)^i multiplier(x)`を`0<=i<count`で返す。O(N log^2 N)。"""

    degree = len(polynomial) - 1
    if degree < 0:
        return [] if count is None else [0] * count
    if multiplier is None:
        multiplier = [1]
    if count is None:
        count = degree + 1
    weights = [0] * (degree + 1)
    for exponent in range(degree + 1):
        multiplier_index = degree - exponent
        if multiplier_index < len(multiplier):
            weights[exponent] = multiplier[multiplier_index]
    return power_projection(polynomial, weights, count)
