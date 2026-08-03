from math import gcd, isqrt


def modular_square_root(value, prime):
    if prime < 2:
        raise ValueError("prime must be at least 2")
    value %= prime
    if value < 2 or prime == 2:
        return value
    if pow(value, (prime - 1) >> 1, prime) != 1:
        return -1
    if prime & 3 == 3:
        root = pow(value, (prime + 1) >> 2, prime)
        return min(root, prime - root)
    odd = prime - 1
    exponent = 0
    while odd & 1 == 0:
        odd >>= 1
        exponent += 1
    nonresidue = 2
    while pow(nonresidue, (prime - 1) >> 1, prime) != prime - 1:
        nonresidue += 1
    root = pow(value, (odd + 1) >> 1, prime)
    remainder = pow(value, odd, prime)
    generator = pow(nonresidue, odd, prime)
    level = exponent
    while remainder != 1:
        position = 1
        squared = remainder * remainder % prime
        while position < level and squared != 1:
            squared = squared * squared % prime
            position += 1
        if position == level:
            return -1
        adjustment = pow(generator, 1 << (level - position - 1), prime)
        root = root * adjustment % prime
        adjustment = adjustment * adjustment % prime
        remainder = remainder * adjustment % prime
        generator = adjustment
        level = position
    return min(root, prime - root)


def discrete_logarithm(base, target, modulus):
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    base %= modulus
    target %= modulus
    identity = 1 % modulus
    if target == identity:
        return 0
    offset = 0
    accumulated = identity
    while True:
        common = gcd(base, modulus)
        if common == 1:
            break
        if target == accumulated:
            return offset
        if target % common:
            return -1
        target //= common
        modulus //= common
        offset += 1
        if modulus == 1:
            return offset
        accumulated = accumulated * (base // common) % modulus
    target = target * pow(accumulated, -1, modulus) % modulus
    width = isqrt(modulus) + 1
    baby = {}
    value = 1
    for exponent in range(width):
        if value not in baby:
            baby[value] = exponent
        value = value * base % modulus
    inverse_step = pow(value, -1, modulus)
    giant = target
    for block in range(width + 1):
        exponent = baby.get(giant)
        if exponent is not None:
            return offset + block * width + exponent
        giant = giant * inverse_step % modulus
    return -1


mod_sqrt = modular_square_root
tonelli_shanks = modular_square_root
mod_log = discrete_logarithm
ModLog = discrete_logarithm
