"""整数を2つの平方数の和で表す組を列挙する。"""

from library_codex.number_theory.GaussianInteger import GaussianInteger

from math import gcd, isqrt

from library_codex.number_theory.ModularArithmetic import modular_square_root

from library_codex.prime.Factorization import factor_count, euler_phi

def _prime_two_squares(prime):
    if prime == 2:
        return GaussianInteger(1, 1)
    if prime & 3 == 3:
        return None
    root = modular_square_root(-1, prime)
    if root == -1:
        return None
    previous, current = prime, root
    while current * current > prime:
        previous, current = current, previous % current
    remaining = prime - current * current
    imaginary = isqrt(remaining)
    if imaginary * imaginary != remaining:
        root = prime - root
        previous, current = prime, root
        while current * current > prime:
            previous, current = current, previous % current
        remaining = prime - current * current
        imaginary = isqrt(remaining)
    if imaginary * imaginary != remaining:
        raise ArithmeticError("Cornacchia failed")
    return GaussianInteger(current, imaginary)

def two_square_representations(number):
    """All ordered nonnegative (x,y) with x*x+y*y == number."""
    if number < 0:
        return []
    if number == 0:
        return [(0, 0)]
    current = [GaussianInteger(1)]
    for prime, exponent in factor_count(number).items():
        if prime & 3 == 3:
            if exponent & 1:
                return []
            choices = [GaussianInteger(prime ** (exponent >> 1))]
        elif prime == 2:
            choices = [GaussianInteger(1, 1) ** exponent]
        else:
            base = _prime_two_squares(prime)
            powers = [GaussianInteger(1)] * (exponent + 1)
            conjugate_powers = [GaussianInteger(1)] * (exponent + 1)
            conjugate = base.conjugate()
            for index in range(exponent):
                powers[index + 1] = powers[index] * base
                conjugate_powers[index + 1] = conjugate_powers[index] * conjugate
            choices = [powers[index] * conjugate_powers[exponent - index]
                       for index in range(exponent + 1)]
        next_values = []
        for first in current:
            for second in choices:
                next_values.append(first * second)
        current = next_values
    result = set()
    for value in current:
        real = abs(value.real)
        imaginary = abs(value.imag)
        result.add((real, imaginary))
        result.add((imaginary, real))
    return sorted(result)

