"""998244353上で多項式の冪に関する係数をまとめて列挙する。"""

from library_codex.convolution.NTT998 import (
    MOD,
    _butterfly,
    _butterfly_inv,
    _ntt_plan,
    multiply,
)


def _power_projection_zero_constant(polynomial, weights, count):
    if not polynomial or not weights:
        return [0] * count
    size = 1 << (len(weights) - 1).bit_length()
    width = size * 2
    forward_plan = _ntt_plan(width * 2)
    inverse_plan = _ntt_plan(width, inverse=True)
    inverse_width = pow(width, MOD - 2, MOD)
    inverse_two = (MOD + 1) >> 1
    inverse_root = pow(3, MOD - 1 - (MOD - 1) // (width * 2), MOD)
    reverse = [0] * width
    half = width >> 1
    for index in range(1, width):
        reverse[index] = (reverse[index >> 1] >> 1) | ((index & 1) * half)
    odd_scale = [0] * width
    value = inverse_two
    for index in reverse:
        odd_scale[index] = value
        value = value * inverse_root % MOD

    numerator = [0] * width
    denominator = [0] * width
    for index, value in enumerate(weights):
        numerator[size - 1 - index] = value % MOD
    for index in range(1, min(len(polynomial), len(weights))):
        denominator[index] = -polynomial[index] % MOD
    height = size
    blocks = 1
    while height > 1:
        numerator.extend([0] * width)
        denominator.extend([0] * width)
        denominator[width] = 1
        _butterfly(numerator, forward_plan)
        _butterfly(denominator, forward_plan)
        for index in range(width):
            left = index << 1
            right = left | 1
            numerator[index] = (
                numerator[left] * denominator[right]
                - numerator[right] * denominator[left]
            ) % MOD * odd_scale[index] % MOD
            denominator[index] = denominator[left] * denominator[right] % MOD
        del numerator[width:]
        del denominator[width:]
        _butterfly_inv(numerator, inverse_plan, height >> 1)
        _butterfly_inv(denominator, inverse_plan, height >> 1)
        for block in range(blocks << 1):
            start = block * height + (height >> 1)
            stop = (block + 1) * height
            for index in range(block * height, start):
                numerator[index] = numerator[index] * inverse_width % MOD
                denominator[index] = denominator[index] * inverse_width % MOD
            numerator[start:stop] = [0] * (height >> 1)
            denominator[start:stop] = [0] * (height >> 1)
        denominator[0] = 0
        height >>= 1
        blocks <<= 1
    result = numerator[:width:2][::-1][:count]
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
