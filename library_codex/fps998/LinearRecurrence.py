"""998244353上で線形漸化式の推定と巨大添字の項を計算する。

Berlekamp--Masseyで最短漸化式を求め、Bostan--Moriで有理FPS
`P(x)/Q(x)`の指定係数を計算する。
"""

from library_codex.convolution.NTT998 import MOD, multiply
from library_codex.fps998.FPS import fps_divmod, shrink


def berlekamp_massey(sequence):
    """先頭から与えた列を生成する最短線形漸化式の係数を返す。O(N^2)。"""

    connection = [1]
    previous = [1]
    length = 0
    shift = 1
    previous_discrepancy = 1
    for position, raw_value in enumerate(sequence):
        discrepancy = raw_value % MOD
        for index in range(1, length + 1):
            discrepancy += connection[index] * sequence[position - index]
        discrepancy %= MOD
        if discrepancy == 0:
            shift += 1
            continue
        scale = discrepancy * pow(previous_discrepancy, MOD - 2, MOD) % MOD
        saved = connection[:]
        required = len(previous) + shift
        if len(connection) < required:
            connection.extend([0] * (required - len(connection)))
        for index, value in enumerate(previous):
            connection[index + shift] = (
                connection[index + shift] - scale * value
            ) % MOD
        if length * 2 <= position:
            length = position + 1 - length
            previous = saved
            previous_discrepancy = discrepancy
            shift = 1
        else:
            shift += 1
    return [-connection[index] % MOD for index in range(1, length + 1)]


def bostan_mori(index, numerator, denominator):
    """有理FPS`numerator/denominator`の`x^index`係数を返す。O(K log K log N)。"""

    if index < 0:
        raise ValueError("index must be nonnegative")
    denominator = shrink(denominator)
    if not denominator or denominator[0] == 0:
        raise ZeroDivisionError("denominator requires nonzero constant coefficient")
    numerator = shrink(numerator)
    polynomial_part = 0
    if len(numerator) >= len(denominator):
        quotient, numerator = fps_divmod(numerator, denominator)
        if index < len(quotient):
            polynomial_part = quotient[index]
    if not numerator:
        return polynomial_part
    while index:
        opposite = denominator[:]
        for position in range(1, len(opposite), 2):
            opposite[position] = -opposite[position] % MOD
        multiplied_numerator = multiply(numerator, opposite)
        multiplied_denominator = multiply(denominator, opposite)
        numerator = multiplied_numerator[index & 1::2]
        denominator = multiplied_denominator[::2]
        index >>= 1
        if not numerator:
            return polynomial_part
    return (
        polynomial_part
        + numerator[0] * pow(denominator[0], MOD - 2, MOD)
    ) % MOD


def linear_recurrence_nth(initial, coefficients, index):
    """`a[n]=sum(coefficients[i]*a[n-1-i])`で定まる`a[index]`を返す。O(K log K log N)。"""

    if index < 0:
        raise ValueError("index must be nonnegative")
    order = len(coefficients)
    if index < len(initial):
        return initial[index] % MOD
    if order == 0:
        return 0
    if len(initial) < order:
        raise ValueError("at least order initial values are required")
    denominator = [1] + [-value % MOD for value in coefficients]
    numerator = multiply(initial[:order], denominator)[:order]
    return bostan_mori(index, numerator, denominator)


def nth_term(index, sequence):
    """与えた列から漸化式を推定し、`index`番目の値を返す。O(N^2+K log K log index)。"""

    if index < 0:
        raise ValueError("index must be nonnegative")
    if index < len(sequence):
        return sequence[index] % MOD
    coefficients = berlekamp_massey(sequence)
    if not coefficients:
        return 0
    return linear_recurrence_nth(sequence, coefficients, index)
