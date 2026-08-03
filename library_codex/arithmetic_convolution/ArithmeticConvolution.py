DEFAULT_MOD = 998244353
_PRIME_LIMIT = 1
_PRIMES = []


def _primes_up_to(limit):
    global _PRIME_LIMIT, _PRIMES
    if limit <= _PRIME_LIMIT:
        end = 0
        while end < len(_PRIMES) and _PRIMES[end] <= limit:
            end += 1
        return _PRIMES[:end]
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[:2] = b"\x00\x00"
    bound = int(limit ** 0.5)
    for value in range(2, bound + 1):
        if sieve[value]:
            start = value * value
            sieve[start:limit + 1:value] = b"\x00" * (
                (limit - start) // value + 1
            )
    _PRIMES = [value for value in range(2, limit + 1) if sieve[value]]
    _PRIME_LIMIT = limit
    return _PRIMES


def divisor_zeta_transform(values, mod=None):
    limit = len(values) - 1
    for prime in _primes_up_to(limit):
        if mod is None:
            for value in range(1, limit // prime + 1):
                values[value * prime] += values[value]
        else:
            for value in range(1, limit // prime + 1):
                index = value * prime
                values[index] = (values[index] + values[value]) % mod
    return values


def divisor_mobius_transform(values, mod=None):
    limit = len(values) - 1
    for prime in _primes_up_to(limit):
        if mod is None:
            for value in range(limit // prime, 0, -1):
                values[value * prime] -= values[value]
        else:
            for value in range(limit // prime, 0, -1):
                index = value * prime
                values[index] = (values[index] - values[value]) % mod
    return values


def multiple_zeta_transform(values, mod=None):
    limit = len(values) - 1
    for prime in _primes_up_to(limit):
        if mod is None:
            for value in range(limit // prime, 0, -1):
                values[value] += values[value * prime]
        else:
            for value in range(limit // prime, 0, -1):
                values[value] = (values[value] + values[value * prime]) % mod
    return values


def multiple_mobius_transform(values, mod=None):
    limit = len(values) - 1
    for prime in _primes_up_to(limit):
        if mod is None:
            for value in range(1, limit // prime + 1):
                values[value] -= values[value * prime]
        else:
            for value in range(1, limit // prime + 1):
                values[value] = (values[value] - values[value * prime]) % mod
    return values


def gcd_convolution(first, second, mod=DEFAULT_MOD):
    if len(first) != len(second):
        raise ValueError("input lengths must be equal")
    if not first:
        return []
    left = [value % mod for value in first]
    right = [value % mod for value in second]
    left[0] = 0
    right[0] = 0
    multiple_zeta_transform(left, mod)
    multiple_zeta_transform(right, mod)
    for index in range(1, len(left)):
        left[index] = left[index] * right[index] % mod
    multiple_mobius_transform(left, mod)
    left[0] = 0
    return left


def lcm_convolution(first, second, mod=DEFAULT_MOD):
    if len(first) != len(second):
        raise ValueError("input lengths must be equal")
    if not first:
        return []
    left = [value % mod for value in first]
    right = [value % mod for value in second]
    left[0] = 0
    right[0] = 0
    divisor_zeta_transform(left, mod)
    divisor_zeta_transform(right, mod)
    for index in range(1, len(left)):
        left[index] = left[index] * right[index] % mod
    divisor_mobius_transform(left, mod)
    left[0] = 0
    return left


DivisorZeta = divisor_zeta_transform
DivisorMobius = divisor_mobius_transform
DivisorReversedZeta = multiple_zeta_transform
DivisorReversedMobius = multiple_mobius_transform
GcdConvolution = gcd_convolution
LcmConvolution = lcm_convolution
