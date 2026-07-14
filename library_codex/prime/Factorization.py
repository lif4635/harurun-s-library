from math import gcd


_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
_MILLER_RABIN_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def is_prime(number):
    if number < 2:
        return False
    if number >= 1 << 64:
        raise ValueError("deterministic primality is supported below 2^64")
    for prime in _SMALL_PRIMES:
        if number % prime == 0:
            return number == prime
    odd = number - 1
    exponent = 0
    while odd & 1 == 0:
        odd >>= 1
        exponent += 1
    for base in _MILLER_RABIN_BASES:
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
        raise ValueError("number must be at least 2")
    for prime in _SMALL_PRIMES:
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
        raise ValueError("number must be positive")
    if number == 1:
        return []
    result = []
    remaining = number
    for prime in _SMALL_PRIMES:
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
        raise ValueError("number must be positive")
    result = [1]
    for prime, exponent in factor_count(number).items():
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
        raise ValueError("number must be positive")
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
