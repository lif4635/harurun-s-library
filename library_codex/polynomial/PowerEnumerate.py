"""多項式の冪に関する内積または係数をまとめて列挙する。"""

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
)

def _power_inner_zero_constant(polynomial, weights, count, mod):
    if count < 0:
        raise ValueError("count must be nonnegative")
    if not polynomial or not weights:
        return [0] * (count + 1)
    original_size = len(weights)
    size = 1
    while size < original_size:
        size <<= 1
    product_numerator = [0] * (size << 1)
    denominator = [0] * (size << 1)
    padded_weights = list(weights) + [0] * (size - original_size)
    padded_weights.reverse()
    product_numerator[:size] = [value % mod for value in padded_weights]
    limit = min(len(polynomial), original_size)
    for index in range(1, limit):
        denominator[index] = -polynomial[index] % mod
    block_count = 1
    while size > 1:
        reflected = denominator[:]
        for index in range(1, len(reflected), 2):
            reflected[index] = -reflected[index] % mod
        next_numerator = fps_multiply(product_numerator, reflected, mod)
        next_denominator = fps_multiply(denominator, reflected, mod)
        expanded = size * block_count << 2
        next_numerator.extend([0] * (expanded - len(next_numerator)))
        next_denominator.extend([0] * (expanded - len(next_denominator)))
        offset = size * block_count << 1
        source_length = size * block_count << 1
        for index in range(source_length):
            next_numerator[offset + index] = (
                next_numerator[offset + index] + product_numerator[index]
            ) % mod
            next_denominator[offset + index] = (
                next_denominator[offset + index]
                + denominator[index] + reflected[index]
            ) % mod
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
    result = [product_numerator[index << 1]
              for index in range(block_count)]
    result.reverse()
    result = result[:count + 1]
    result.extend([0] * (count + 1 - len(result)))
    return result

def power_inner_product_enumerate(polynomial, weights, count,
                                  mod=DEFAULT_MOD):
    """Enumerate sum_j weights[j]*[x^j] polynomial(x)^i."""
    if count < 0:
        raise ValueError("count must be nonnegative")
    if not polynomial or not weights:
        return [0] * (count + 1)
    constant = polynomial[0] % mod
    shifted = list(polynomial)
    shifted[0] = 0
    result = _power_inner_zero_constant(shifted, weights, count, mod)
    if constant:
        factorial = [1] * (count + 1)
        inverse_factorial = [1] * (count + 1)
        for index in range(1, count + 1):
            factorial[index] = factorial[index - 1] * index % mod
        inverse_factorial[count] = pow(factorial[count], -1, mod)
        for index in range(count, 0, -1):
            inverse_factorial[index - 1] = (
                inverse_factorial[index] * index % mod
            )
        coefficient = [0] * (count + 1)
        power = 1
        for index in range(count + 1):
            result[index] = result[index] * inverse_factorial[index] % mod
            coefficient[index] = inverse_factorial[index] * power % mod
            power = power * constant % mod
        result = fps_multiply(result, coefficient, mod)[:count + 1]
        result.extend([0] * (count + 1 - len(result)))
        return [result[index] * factorial[index] % mod
                for index in range(count + 1)]
    return result

def power_coefficient_enumerate(polynomial, multiplier=None, count=None,
                                mod=DEFAULT_MOD):
    """Enumerate [x^n] polynomial(x)^i*multiplier(x), n=len(f)-1."""
    degree = len(polynomial) - 1
    if degree < 0:
        if count is None:
            count = 0
        return [0] * (count + 1)
    if multiplier is None:
        multiplier = [1]
    if count is None:
        count = degree
    weights = [0] * (degree + 1)
    for exponent in range(degree + 1):
        multiplier_index = degree - exponent
        if multiplier_index < len(multiplier):
            weights[exponent] = multiplier[multiplier_index]
    return power_inner_product_enumerate(polynomial, weights, count, mod)

