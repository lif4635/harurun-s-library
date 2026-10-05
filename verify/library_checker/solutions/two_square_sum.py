"""Gaussian整数の四則演算と最大公約数を扱う。"""

class GaussianInteger:
    __slots__ = ('real', 'imag')

    def __init__(self, real=0, imag=0):
        self.real = real
        self.imag = imag

    @property
    def x(self):
        return self.real

    @property
    def y(self):
        return self.imag

    def norm(self):
        return self.real * self.real + self.imag * self.imag

    def conjugate(self):
        return GaussianInteger(self.real, -self.imag)
    conj = conjugate

    def __add__(self, other):
        return GaussianInteger(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return GaussianInteger(self.real - other.real, self.imag - other.imag)

    def __neg__(self):
        return GaussianInteger(-self.real, -self.imag)

    def __mul__(self, other):
        if isinstance(other, int):
            return GaussianInteger(self.real * other, self.imag * other)
        return GaussianInteger(self.real * other.real - self.imag * other.imag, self.real * other.imag + self.imag * other.real)

    def __eq__(self, other):
        return isinstance(other, GaussianInteger) and self.real == other.real and (self.imag == other.imag)

    def __repr__(self):
        return f'GaussianInteger({self.real}, {self.imag})'

    def __pow__(self, exponent):
        if exponent < 0:
            raise ValueError('negative Gaussian powers are not integral')
        result = GaussianInteger(1)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            exponent >>= 1
            if exponent:
                base = base * base
        return result

    def __divmod__(self, other):
        norm = other.norm()
        if norm == 0:
            raise ZeroDivisionError('Gaussian integer division by zero')
        product = self * other.conjugate()

        def nearest(value):
            (quotient, remainder) = divmod(value, norm)
            if remainder * 2 >= norm:
                quotient += 1
            return quotient
        quotient = GaussianInteger(nearest(product.real), nearest(product.imag))
        return (quotient, self - quotient * other)

    def __floordiv__(self, other):
        return divmod(self, other)[0]

    def __mod__(self, other):
        return divmod(self, other)[1]

def gaussian_gcd(first, second):
    while second != GaussianInteger():
        (first, second) = (second, first % second)
    return first
from math import gcd, isqrt

def modular_square_root(value, prime):
    if prime < 2:
        raise ValueError('prime must be at least 2')
    value %= prime
    if value < 2 or prime == 2:
        return value
    if pow(value, prime - 1 >> 1, prime) != 1:
        return -1
    if prime & 3 == 3:
        root = pow(value, prime + 1 >> 2, prime)
        return min(root, prime - root)
    odd = prime - 1
    exponent = 0
    while odd & 1 == 0:
        odd >>= 1
        exponent += 1
    nonresidue = 2
    while pow(nonresidue, prime - 1 >> 1, prime) != prime - 1:
        nonresidue += 1
    root = pow(value, odd + 1 >> 1, prime)
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
        adjustment = pow(generator, 1 << level - position - 1, prime)
        root = root * adjustment % prime
        adjustment = adjustment * adjustment % prime
        remainder = remainder * adjustment % prime
        generator = adjustment
        level = position
    return min(root, prime - root)

def discrete_logarithm(base, target, modulus):
    if modulus <= 0:
        raise ValueError('modulus must be positive')
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
from math import gcd as _prime_factorization_gcd
_prime_factorization_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
_prime_factorization_MILLER_RABIN_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)

def is_prime(number):
    if number < 2:
        return False
    if number >= 1 << 64:
        raise ValueError('deterministic primality is supported below 2^64')
    for prime in _prime_factorization_SMALL_PRIMES:
        if number % prime == 0:
            return number == prime
    odd = number - 1
    exponent = 0
    while odd & 1 == 0:
        odd >>= 1
        exponent += 1
    for base in _prime_factorization_MILLER_RABIN_BASES:
        base %= number
        if base == 0:
            continue
        value = pow(base, odd, number)
        if value == 1 or value == number - 1:
            continue
        for _ in range(exponent - 1):
            value = value * value % number
            if value == number - 1:
                break
        else:
            return False
    return True

def pollard_rho(number):
    if number < 2:
        raise ValueError('number must be at least 2')
    for prime in _prime_factorization_SMALL_PRIMES:
        if number % prime == 0:
            return prime
    if is_prime(number):
        return number
    constant = 1
    seed = 2
    while True:
        y = seed
        power = 1
        factor = 1
        saved = y
        x = y
        while factor == 1:
            x = y
            for _ in range(power):
                y = (y * y + constant) % number
            offset = 0
            product = 1
            while offset < power and factor == 1:
                saved = y
                block = min(128, power - offset)
                for _ in range(block):
                    y = (y * y + constant) % number
                    product = product * abs(x - y) % number
                factor = _prime_factorization_gcd(product, number)
                offset += block
            power <<= 1
        if factor == number:
            factor = 1
            while factor == 1:
                saved = (saved * saved + constant) % number
                factor = _prime_factorization_gcd(abs(x - saved), number)
        if factor != number:
            return factor
        constant += 1
        seed += 1
        if constant == number:
            constant = 1

def prime_factors(number):
    if number < 1:
        raise ValueError('number must be positive')
    if number == 1:
        return []
    result = []
    remaining = number
    for prime in _prime_factorization_SMALL_PRIMES:
        while remaining % prime == 0:
            result.append(prime)
            remaining //= prime
    stack = [remaining] if remaining > 1 else []
    while stack:
        current = stack.pop()
        if current == 1:
            continue
        if is_prime(current):
            result.append(current)
            continue
        factor = pollard_rho(current)
        stack.append(factor)
        stack.append(current // factor)
    result.sort()
    return result

def factor_count(number):
    result = {}
    for prime in prime_factors(number):
        result[prime] = result.get(prime, 0) + 1
    return result

def divisors(number):
    if number < 1:
        raise ValueError('number must be positive')
    result = [1]
    for (prime, exponent) in factor_count(number).items():
        initial_size = len(result)
        power = 1
        for _ in range(exponent):
            power *= prime
            for index in range(initial_size):
                result.append(result[index] * power)
    result.sort()
    return result

def euler_phi(number):
    if number < 1:
        raise ValueError('number must be positive')
    result = number
    for prime in factor_count(number):
        result -= result // prime
    return result

def mobius(number):
    factors = factor_count(number)
    for exponent in factors.values():
        if exponent > 1:
            return 0
    return -1 if len(factors) & 1 else 1

def factor_count_pairs(number):
    return list(factor_count(number).items())
miller_rabin = is_prime
factorize = prime_factors
Pollard = prime_factors
Pollard2 = factor_count_pairs
EnumDivisors = divisors
'整数を2つの平方数の和で表す組を列挙する。'
from math import gcd as _number_theory_two_square_representations_gcd, isqrt as _number_theory_two_square_representations_isqrt

def _number_theory_two_square_representations_prime_two_squares(prime):
    if prime == 2:
        return GaussianInteger(1, 1)
    if prime & 3 == 3:
        return None
    root = modular_square_root(-1, prime)
    if root == -1:
        return None
    (previous, current) = (prime, root)
    while current * current > prime:
        (previous, current) = (current, previous % current)
    remaining = prime - current * current
    imaginary = _number_theory_two_square_representations_isqrt(remaining)
    if imaginary * imaginary != remaining:
        root = prime - root
        (previous, current) = (prime, root)
        while current * current > prime:
            (previous, current) = (current, previous % current)
        remaining = prime - current * current
        imaginary = _number_theory_two_square_representations_isqrt(remaining)
    if imaginary * imaginary != remaining:
        raise ArithmeticError('Cornacchia failed')
    return GaussianInteger(current, imaginary)

def two_square_representations(number):
    """All ordered nonnegative (x,y) with x*x+y*y == number."""
    if number < 0:
        return []
    if number == 0:
        return [(0, 0)]
    current = [GaussianInteger(1)]
    for (prime, exponent) in factor_count(number).items():
        if prime & 3 == 3:
            if exponent & 1:
                return []
            choices = [GaussianInteger(prime ** (exponent >> 1))]
        elif prime == 2:
            choices = [GaussianInteger(1, 1) ** exponent]
        else:
            base = _number_theory_two_square_representations_prime_two_squares(prime)
            powers = [GaussianInteger(1)] * (exponent + 1)
            conjugate_powers = [GaussianInteger(1)] * (exponent + 1)
            conjugate = base.conjugate()
            for index in range(exponent):
                powers[index + 1] = powers[index] * base
                conjugate_powers[index + 1] = conjugate_powers[index] * conjugate
            choices = [powers[index] * conjugate_powers[exponent - index] for index in range(exponent + 1)]
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
import sys

def main():
    read = sys.stdin.buffer.readline
    result = []
    for _ in range(int(read())):
        pairs = two_square_representations(int(read()))
        result.append(str(len(pairs)))
        result.extend((f'{a} {b}' for (a, b) in pairs))
    sys.stdout.write('\n'.join(result))
if __name__ == '__main__':
    main()
