"""Polynomial quotient and remainder in ascending coefficient order."""

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_inverse,
    fps_multiply,
    fps_shrink,
)


def poly_div(dividend, divisor, mod=DEFAULT_MOD):
    """Return the polynomial quotient. O(N log N)."""

    first = fps_shrink(dividend, mod)
    second = fps_shrink(divisor, mod)
    if not second:
        raise ZeroDivisionError("polynomial division by zero")
    if len(first) < len(second):
        return []
    quotient_size = len(first) - len(second) + 1
    if len(second) <= 64:
        result = [0] * quotient_size
        remainder = first[:]
        try:
            inverse_leading = pow(second[-1], -1, mod)
        except ValueError as error:
            raise ZeroDivisionError(
                "the leading coefficient is not invertible"
            ) from error
        width = len(second)
        for index in range(quotient_size - 1, -1, -1):
            value = remainder[index + width - 1] * inverse_leading % mod
            result[index] = value
            for offset in range(width):
                remainder[index + offset] = (
                    remainder[index + offset] - value * second[offset]
                ) % mod
        return result
    reversed_dividend = list(reversed(first[-quotient_size:]))
    reversed_divisor = list(reversed(second))
    result = fps_multiply(
        reversed_dividend,
        fps_inverse(reversed_divisor, quotient_size, mod),
        mod,
    )[:quotient_size]
    result.reverse()
    return result


def poly_divmod(dividend, divisor, mod=DEFAULT_MOD):
    """Return ``(quotient, remainder)`` for polynomial division. O(N log N)."""

    second = fps_shrink(divisor, mod)
    if not second:
        raise ZeroDivisionError("polynomial division by zero")
    first = fps_shrink(dividend, mod)
    quotient = poly_div(first, second, mod)
    if not quotient:
        return [], first
    product = fps_multiply(quotient, second, mod)
    remainder = [0] * min(len(second) - 1, max(len(first), len(product)))
    for index in range(len(remainder)):
        left = first[index] if index < len(first) else 0
        right = product[index] if index < len(product) else 0
        remainder[index] = (left - right) % mod
    while remainder and remainder[-1] == 0:
        remainder.pop()
    return quotient, remainder


def poly_mod(dividend, divisor, mod=DEFAULT_MOD):
    """Return the remainder of polynomial division. O(N log N)."""

    return poly_divmod(dividend, divisor, mod)[1]
