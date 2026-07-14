from library_codex.algorithm.MiscAlgorithms import (
    decimal_digit_count,
    exact_square_root,
    modular_power,
)
from library_codex.math.Combinatorics import extended_gcd
from library_codex.math.ModularRoot import primitive_root
from library_codex.prime.Factorization import divisors, euler_phi, factor_count
from library_codex.prime.Sieve import LinearSieve


def totient_table(limit):
    return LinearSieve(limit).phi


def is_primitive_root(value, prime):
    value %= prime
    if value == 0:
        return False
    return all(pow(value, (prime - 1) // factor, prime) != 1
               for factor in factor_count(prime - 1))


EulersTotientFunction = totient_table
Divisor = divisors
PrimeFactors = lambda number: list(factor_count(number).items())
modpow = modular_power
PrimitiveRoot = primitive_root
isPrimitiveRoot = is_primitive_root
phi = euler_phi
extgcd = lambda first, second: extended_gcd(first, second)[1:]
SqrtInt = exact_square_root
isDigit = decimal_digit_count
