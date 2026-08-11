"""合成数modulusにも対応する離散対数を求める。"""

from math import gcd, isqrt


def discrete_log(base, value, modulus):
    """最小の非負整数xでbase**x == value (mod modulus)となるものを返す。"""
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    if modulus == 1:
        return 0
    base %= modulus
    value %= modulus
    if value == 1:
        return 0

    offset = 0
    coefficient = 1
    common = gcd(base, modulus)
    while common > 1:
        if value == coefficient:
            return offset
        if value % common:
            return -1
        value //= common
        modulus //= common
        coefficient = coefficient * (base // common) % modulus
        offset += 1
        if modulus == 1:
            return offset
        common = gcd(base, modulus)

    target = value * pow(coefficient, -1, modulus) % modulus
    width = isqrt(modulus) + 1
    baby = {}
    power = 1
    for exponent in range(width):
        baby.setdefault(power, exponent)
        power = power * base % modulus
    giant_step = pow(power, -1, modulus)
    current = target
    best = None
    for giant in range(width + 1):
        small = baby.get(current)
        if small is not None:
            exponent = giant * width + small
            if best is None or exponent < best:
                best = exponent
        current = current * giant_step % modulus
    return -1 if best is None else offset + best
