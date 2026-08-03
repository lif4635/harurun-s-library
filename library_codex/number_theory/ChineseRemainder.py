from math import gcd


def inv_gcd(value, modulus):
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    value %= modulus
    if value == 0:
        return modulus, 0
    first, second = modulus, value
    x0, x1 = 0, 1
    while second:
        quotient = first // second
        first, second = second, first - quotient * second
        x0, x1 = x1, x0 - quotient * x1
    return first, x0 % (modulus // first)


def _combine(first_remainder, first_modulus, second_remainder, second_modulus):
    second_remainder %= second_modulus
    if first_modulus < second_modulus:
        first_remainder, second_remainder = second_remainder, first_remainder
        first_modulus, second_modulus = second_modulus, first_modulus
    if first_modulus % second_modulus == 0:
        if first_remainder % second_modulus != second_remainder:
            return 0, 0
        return first_remainder, first_modulus
    common, inverse = inv_gcd(first_modulus, second_modulus)
    difference = second_remainder - first_remainder
    if difference % common:
        return 0, 0
    reduced_modulus = second_modulus // common
    multiplier = difference // common % reduced_modulus
    multiplier = multiplier * inverse % reduced_modulus
    modulus = first_modulus * reduced_modulus
    remainder = (first_remainder + multiplier * first_modulus) % modulus
    return remainder, modulus


def chinese_remainder(residues, moduli):
    residues = list(residues)
    moduli = list(moduli)
    if len(residues) != len(moduli):
        raise ValueError("residues and moduli must have the same length")
    remainder = 0
    modulus = 1
    for value, current_modulus in zip(residues, moduli):
        if current_modulus <= 0:
            raise ValueError("moduli must be positive")
        remainder, modulus = _combine(
            remainder, modulus, value, current_modulus
        )
        if modulus == 0:
            return 0, 0
    return remainder, modulus


def chinese_remainder_balanced(residues, moduli):
    residues = list(residues)
    moduli = list(moduli)
    if len(residues) != len(moduli):
        raise ValueError("residues and moduli must have the same length")
    current = []
    for value, modulus in zip(residues, moduli):
        if modulus <= 0:
            raise ValueError("moduli must be positive")
        current.append((value % modulus, modulus))
    if not current:
        return 0, 1
    while len(current) > 1:
        next_level = []
        limit = len(current) - 1
        index = 0
        while index < limit:
            combined = _combine(*current[index], *current[index + 1])
            if combined[1] == 0:
                return 0, 0
            next_level.append(combined)
            index += 2
        if index < len(current):
            next_level.append(current[index])
        current = next_level
    return current[0]


def garner_mod(residues, moduli, target_modulus):
    residues = list(residues)
    moduli = list(moduli)
    if len(residues) != len(moduli):
        raise ValueError("residues and moduli must have the same length")
    if target_modulus <= 0:
        raise ValueError("target_modulus must be positive")
    size = len(residues)
    constants = [0] * (size + 1)
    products = [1] * (size + 1)
    extended_moduli = moduli + [target_modulus]
    for index in range(size):
        modulus = extended_moduli[index]
        if modulus <= 0:
            raise ValueError("moduli must be positive")
        if gcd(products[index], modulus) != 1:
            raise ValueError("Garner requires pairwise coprime moduli")
        digit = (
            (residues[index] - constants[index])
            * pow(products[index], -1, modulus)
        ) % modulus
        for target in range(index + 1, size + 1):
            target_mod = extended_moduli[target]
            constants[target] = (
                constants[target] + products[target] * digit
            ) % target_mod
            products[target] = products[target] * modulus % target_mod
    return constants[-1]


crt = chinese_remainder
garner = chinese_remainder
garner_bigint = chinese_remainder_balanced
