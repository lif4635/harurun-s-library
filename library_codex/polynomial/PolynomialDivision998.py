"""Fast polynomial quotient and remainder modulo 998244353."""

from library_codex.convolution.NTT998 import MOD, multiply
from library_codex.fps998.FPS import fps_inv, shrink


def poly_div(dividend, divisor):
    """Return the polynomial quotient modulo 998244353. O(N log N)."""

    first = shrink(dividend)
    second = shrink(divisor)
    if not second:
        raise ZeroDivisionError("polynomial division by zero")
    if len(first) < len(second):
        return []
    quotient_size = len(first) - len(second) + 1
    if len(second) <= 64:
        result = [0] * quotient_size
        remainder = first[:]
        inverse_leading = pow(second[-1], MOD - 2, MOD)
        width = len(second)
        for index in range(quotient_size - 1, -1, -1):
            value = remainder[index + width - 1] * inverse_leading % MOD
            result[index] = value
            for offset in range(width):
                remainder[index + offset] = (
                    remainder[index + offset] - value * second[offset]
                ) % MOD
        return result
    reversed_dividend = list(reversed(first[-quotient_size:]))
    reversed_divisor = list(reversed(second))
    result = multiply(
        reversed_dividend,
        fps_inv(reversed_divisor, quotient_size),
    )[:quotient_size]
    result.reverse()
    return result


def poly_divmod(dividend, divisor):
    """Return polynomial ``(quotient, remainder)`` modulo 998244353. O(N log N)."""

    second = shrink(divisor)
    if not second:
        raise ZeroDivisionError("polynomial division by zero")
    first = shrink(dividend)
    quotient = poly_div(first, second)
    if not quotient:
        return [], first
    product = multiply(quotient, second)
    remainder = [0] * min(len(second) - 1, max(len(first), len(product)))
    for index in range(len(remainder)):
        left = first[index] if index < len(first) else 0
        right = product[index] if index < len(product) else 0
        remainder[index] = (left - right) % MOD
    while remainder and remainder[-1] == 0:
        remainder.pop()
    return quotient, remainder


def poly_mod(dividend, divisor):
    """Return the polynomial remainder modulo 998244353. O(N log N)."""

    return poly_divmod(dividend, divisor)[1]
