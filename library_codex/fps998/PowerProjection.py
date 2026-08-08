"""998244353上で多項式の冪に関する係数をまとめて列挙する。"""

from library_codex.convolution.NTT998 import MOD, multiply


def _power_projection_zero_constant(polynomial, weights, count):
    if not polynomial or not weights:
        return [0] * count
    original_size = len(weights)
    size = 1
    while size < original_size:
        size <<= 1
    product_numerator = [0] * (size << 1)
    denominator = [0] * (size << 1)
    padded_weights = list(weights) + [0] * (size - original_size)
    padded_weights.reverse()
    product_numerator[:size] = [value % MOD for value in padded_weights]
    limit = min(len(polynomial), original_size)
    for index in range(1, limit):
        denominator[index] = -polynomial[index] % MOD
    block_count = 1
    while size > 1:
        reflected = denominator[:]
        for index in range(1, len(reflected), 2):
            reflected[index] = -reflected[index] % MOD
        next_numerator = multiply(product_numerator, reflected)
        next_denominator = multiply(denominator, reflected)
        expanded = size * block_count << 2
        next_numerator.extend([0] * (expanded - len(next_numerator)))
        next_denominator.extend([0] * (expanded - len(next_denominator)))
        offset = size * block_count << 1
        source_length = size * block_count << 1
        for index in range(source_length):
            next_numerator[offset + index] = (
                next_numerator[offset + index] + product_numerator[index]
            ) % MOD
            next_denominator[offset + index] = (
                next_denominator[offset + index]
                + denominator[index] + reflected[index]
            ) % MOD
        new_length = size * block_count << 1
        new_numerator = [0] * new_length
        new_denominator = [0] * new_length
        half = size >> 1
        for block in range(block_count << 1):
            source = block * size * 2
            destination = block * size
            for index in range(half):
                new_numerator[destination + index] = next_numerator[
                    source + (index << 1) + 1
                ]
                new_denominator[destination + index] = next_denominator[
                    source + (index << 1)
                ]
        product_numerator = new_numerator
        denominator = new_denominator
        size >>= 1
        block_count <<= 1
    result = [product_numerator[index << 1] for index in range(block_count)]
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
