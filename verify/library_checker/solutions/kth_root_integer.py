from math import gcd
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
                factor = gcd(product, number)
                offset += block
            power <<= 1
        if factor == number:
            factor = 1
            while factor == 1:
                saved = (saved * saved + constant) % number
                factor = gcd(abs(x - saved), number)
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
from math import gcd as _number_theory_modular_root_gcd, isqrt

def primitive_root(prime):
    if prime < 2:
        raise ValueError('prime must be at least 2')
    if prime == 2:
        return 1
    known = {167772161: 3, 469762049: 3, 754974721: 11, 998244353: 3, 1000000007: 5}
    root = known.get(prime)
    if root is not None:
        return root
    order = prime - 1
    tests = [order // divisor for divisor in factor_count(order)]
    candidate = 2
    while True:
        for exponent in tests:
            if pow(candidate, exponent, prime) == 1:
                break
        else:
            return candidate
        candidate += 1

class _number_theory_modular_root_PrimeOrderLog:
    __slots__ = ('baby', 'step', 'size', 'period', 'mod')

    def __init__(self, generator, queries, period, mod):
        size = min(period, isqrt(max(1, queries) * period) + 1)
        baby = {}
        value = 1
        for exponent in range(size):
            baby[value] = exponent
            value = value * generator % mod
        self.baby = baby
        self.step = value
        self.size = size
        self.period = period
        self.mod = mod

    def find(self, value):
        elapsed = 0
        baby = self.baby
        step = self.step
        mod = self.mod
        size = self.size
        period = self.period
        while elapsed < period:
            exponent = baby.get(value)
            if exponent is not None:
                return (exponent - elapsed) % period
            value = value * step % mod
            elapsed += size
        raise ArithmeticError('discrete logarithm in prime-order subgroup failed')

def _number_theory_modular_root_prime_power_root(value, divisor, exponent, prime):
    coprime = prime - 1
    valuation = 0
    while coprime % divisor == 0:
        coprime //= divisor
        valuation += 1
    power = divisor ** exponent
    inverse = pow(-coprime % power, -1, power)
    root = pow(value, (coprime * inverse + 1) // power, prime)
    error = pow(value, coprime * inverse, prime)
    if error == 1:
        return root
    if valuation <= exponent:
        raise ArithmeticError('invalid prime-power root state')
    candidate = 2
    test_exponent = divisor ** (valuation - 1)
    while True:
        adjuster = pow(candidate, coprime, prime)
        if pow(adjuster, test_exponent, prime) != 1:
            break
        candidate += 1
    adjuster_power = pow(adjuster, power, prime)
    adjuster_level = exponent
    generator = adjuster_power
    for _ in range(valuation - exponent - 1):
        generator = pow(generator, divisor, prime)
    logarithm = _number_theory_modular_root_PrimeOrderLog(generator, valuation - exponent, divisor, prime)
    while error != 1:
        reduced = error
        depth = 0
        while reduced != 1:
            reduced = pow(reduced, divisor, prime)
            depth += 1
        target_level = valuation - depth
        while adjuster_level != target_level:
            adjuster = pow(adjuster, divisor, prime)
            adjuster_power = pow(adjuster_power, divisor, prime)
            adjuster_level += 1
        reduced = pow(error, -1, prime)
        for _ in range(depth - 1):
            reduced = pow(reduced, divisor, prime)
        correction = logarithm.find(reduced)
        root = root * pow(adjuster, correction, prime) % prime
        error = error * pow(adjuster_power, correction, prime) % prime
    return root

def modular_kth_root(value, exponent, prime):
    if prime < 2:
        raise ValueError('prime must be at least 2')
    if exponent < 0:
        raise ValueError('exponent must be nonnegative')
    value %= prime
    if exponent == 0:
        return 1 if value == 1 else -1
    if value <= 1 or exponent == 1:
        return value
    common = _number_theory_modular_root_gcd(prime - 1, exponent)
    if pow(value, (prime - 1) // common, prime) != 1:
        return -1
    reduced_order = (prime - 1) // common
    value = pow(value, pow(exponent // common, -1, reduced_order), prime)
    for (divisor, multiplicity) in factor_count(common).items():
        value = _number_theory_modular_root_prime_power_root(value, divisor, multiplicity, prime)
    return value

def _number_theory_modular_root_power_leq(base, exponent, limit):
    result = 1
    while exponent:
        if exponent & 1:
            if result > limit // base:
                return False
            result *= base
        exponent >>= 1
        if exponent:
            if base > limit // base:
                base = limit + 1
            else:
                base *= base
    return result <= limit

def floor_kth_root(value, exponent):
    if value < 0:
        raise ValueError('value must be nonnegative')
    if exponent <= 0:
        raise ValueError('exponent must be positive')
    if value <= 1 or exponent == 1:
        return value
    if exponent == 2:
        return isqrt(value)
    if exponent >= value.bit_length():
        return 1
    upper = 1 << (value.bit_length() + exponent - 1) // exponent
    lower = upper >> 1
    while lower + 1 < upper:
        middle = lower + upper >> 1
        if _number_theory_modular_root_power_leq(middle, exponent, value):
            lower = middle
        else:
            upper = middle
    return lower

def ceil_kth_root(value, exponent):
    root = floor_kth_root(value, exponent)
    return root if pow(root, exponent) == value else root + 1
kth_root = modular_kth_root
kth_root_mod = modular_kth_root
primitive_root_ll = primitive_root
FloorOfKthRoot = floor_kth_root
CeilOfKthRoot = ceil_kth_root
kth_root_integral = floor_kth_root
import sys
read = sys.stdin.buffer.readline
answers = [str(floor_kth_root(*map(int, read().split()))) for _ in range(int(read()))]
sys.stdout.write('\n'.join(answers) + '\n')
