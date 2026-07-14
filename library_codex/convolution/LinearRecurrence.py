from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_divmod,
    fps_multiply,
    fps_shrink,
)


def berlekamp_massey(sequence, mod=DEFAULT_MOD):
    connection = [1]
    previous = [1]
    length = 0
    shift = 1
    previous_discrepancy = 1
    for position, raw_value in enumerate(sequence):
        discrepancy = raw_value % mod
        for index in range(1, length + 1):
            discrepancy += connection[index] * sequence[position - index]
        discrepancy %= mod
        if discrepancy == 0:
            shift += 1
            continue
        try:
            scale = discrepancy * pow(previous_discrepancy, -1, mod) % mod
        except ValueError as error:
            raise ZeroDivisionError("Berlekamp-Massey requires a field") from error
        saved = connection[:]
        required = len(previous) + shift
        if len(connection) < required:
            connection.extend([0] * (required - len(connection)))
        for index, value in enumerate(previous):
            connection[index + shift] = (
                connection[index + shift] - scale * value
            ) % mod
        if length * 2 <= position:
            length = position + 1 - length
            previous = saved
            previous_discrepancy = discrepancy
            shift = 1
        else:
            shift += 1
    return [-connection[index] % mod for index in range(1, length + 1)]


def berlekamp_massey_polynomial(sequence, mod=DEFAULT_MOD):
    coefficients = berlekamp_massey(sequence, mod)
    return [1] + [-value % mod for value in coefficients]


def bostan_mori(index, numerator, denominator, mod=DEFAULT_MOD):
    if index < 0:
        raise ValueError("index must be nonnegative")
    denominator = fps_shrink(denominator, mod)
    if not denominator:
        raise ZeroDivisionError("zero denominator")
    try:
        pow(denominator[0], -1, mod)
    except ValueError as error:
        raise ZeroDivisionError("constant denominator is not invertible") from error
    numerator = fps_shrink(numerator, mod)
    polynomial_part = 0
    if len(numerator) >= len(denominator):
        quotient, numerator = fps_divmod(numerator, denominator, mod)
        if index < len(quotient):
            polynomial_part = quotient[index]
    if not numerator:
        return polynomial_part
    while index:
        opposite = denominator[:]
        for position in range(1, len(opposite), 2):
            opposite[position] = -opposite[position] % mod
        multiplied_numerator = fps_multiply(numerator, opposite, mod)
        multiplied_denominator = fps_multiply(denominator, opposite, mod)
        numerator = multiplied_numerator[index & 1::2]
        denominator = multiplied_denominator[::2]
        index >>= 1
        if not numerator:
            return polynomial_part
    return (
        polynomial_part
        + numerator[0] * pow(denominator[0], -1, mod)
    ) % mod


def linear_recurrence_nth(initial, coefficients, index, mod=DEFAULT_MOD):
    if index < 0:
        raise ValueError("index must be nonnegative")
    order = len(coefficients)
    if index < len(initial):
        return initial[index] % mod
    if order == 0:
        return 0
    if len(initial) < order:
        raise ValueError("at least order initial values are required")
    denominator = [1] + [-value % mod for value in coefficients]
    numerator = fps_multiply(initial[:order], denominator, mod)[:order]
    return bostan_mori(index, numerator, denominator, mod)


def nth_term(index, sequence, mod=DEFAULT_MOD):
    if index < 0:
        raise ValueError("index must be nonnegative")
    if index < len(sequence):
        return sequence[index] % mod
    coefficients = berlekamp_massey(sequence, mod)
    if not coefficients:
        return 0
    return linear_recurrence_nth(sequence, coefficients, index, mod)


def kitamasa(index, characteristic, initial, mod=DEFAULT_MOD):
    characteristic = fps_shrink(characteristic, mod)
    if not characteristic or characteristic[0] == 0:
        raise ValueError("characteristic[0] must be nonzero")
    inverse = pow(characteristic[0], -1, mod)
    coefficients = [
        -value * inverse % mod for value in characteristic[1:]
    ]
    return linear_recurrence_nth(initial, coefficients, index, mod)


find_linear_recurrence = berlekamp_massey
BerlekampMassey = berlekamp_massey_polynomial
LinearRecurrence = bostan_mori
