"""Small, independent integer operations."""

from math import isqrt


def nearest_congruent_at_least(value, lower_bound, modulus):
    """Return the smallest x >= lower_bound congruent to value mod modulus."""
    modulus = abs(modulus)
    if modulus == 0:
        raise ValueError("modulus must be nonzero")
    if value < lower_bound:
        return value + ((lower_bound - value + modulus - 1) // modulus) * modulus
    return value - (value - lower_bound) // modulus * modulus


def modular_power(base, exponent, modulus):
    """Return base**exponent modulo modulus."""
    if exponent < 0 or modulus == 0:
        raise ValueError("exponent must be nonnegative and modulus nonzero")
    return pow(base, exponent, modulus)


def exact_square_root(number):
    """Return the nonnegative square root, or -1 when number is not square."""
    if number < 0:
        return -1
    root = isqrt(number)
    return root if root * root == number else -1


def decimal_digit_count(number, zero=1):
    """Return the number of base-10 digits, ignoring the sign."""
    if number == 0:
        return zero
    return len(str(abs(number)))
