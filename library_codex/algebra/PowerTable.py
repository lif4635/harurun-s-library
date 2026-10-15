"""0からlimitまでの整数を、同じ指数で累乗した値をまとめて求める。"""

from math import isqrt

def power_table(limit, exponent, mod=None):
    """result[i] = i**exponentとなる長さlimit+1の列を返す。mod指定時は剰余。"""
    if limit < 0 or exponent < 0:
        raise ValueError("limit and exponent must be nonnegative")
    if mod is None:
        return [value ** exponent for value in range(limit + 1)]
    if limit < 128 or exponent < 4 or mod <= 0:
        return [pow(value, exponent, mod) for value in range(limit + 1)]
    values = [0] * (limit + 1)
    for prime in range(2, isqrt(limit) + 1):
        if values[prime] == 0:
            for multiple in range(prime * prime, limit + 1, prime):
                values[multiple] = prime
    values[0] = pow(0, exponent, mod)
    values[1] = 1 % mod
    for value in range(2, limit + 1):
        divisor = values[value]
        if divisor:
            values[value] = values[divisor] * values[value // divisor] % mod
        else:
            values[value] = pow(value, exponent, mod)
    return values

