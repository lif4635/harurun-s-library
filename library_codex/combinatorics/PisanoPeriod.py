"""Fibonacci数列を法としたときの周期を求める。"""

import math

from library_codex.prime.Factorization import divisors, factor_count

def _fib_pair(index, modulus):
    first, second = 0, 1
    for bit in bin(index)[2:]:
        doubled = first * ((second << 1) - first) % modulus
        next_value = (first * first + second * second) % modulus
        if bit == "0":
            first, second = doubled, next_value
        else:
            first, second = next_value, (doubled + next_value) % modulus
    return first, second

def pisano_prime(prime):
    if prime == 2:
        return 3
    if prime == 5:
        return 20
    candidate = prime - 1 if prime % 5 in (1, 4) else 2 * (prime + 1)
    for period in divisors(candidate):
        if _fib_pair(period, prime) == (0, 1):
            return period
    raise ArithmeticError("Pisano period was not found")

def pisano_period(modulus):
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    if modulus == 1:
        return 1
    result = 1
    for prime, exponent in factor_count(modulus).items():
        period = pisano_prime(prime) * prime ** (exponent - 1)
        result = math.lcm(result, period)
    return result

