DEFAULT_MOD = 998244353
_arithmetic_convolution_arithmetic_convolution_PRIME_LIMIT = 1
_arithmetic_convolution_arithmetic_convolution_PRIMES = []

def _arithmetic_convolution_arithmetic_convolution_primes_up_to(limit):
    global _arithmetic_convolution_arithmetic_convolution_PRIME_LIMIT, _arithmetic_convolution_arithmetic_convolution_PRIMES
    if limit <= _arithmetic_convolution_arithmetic_convolution_PRIME_LIMIT:
        end = 0
        while end < len(_arithmetic_convolution_arithmetic_convolution_PRIMES) and _arithmetic_convolution_arithmetic_convolution_PRIMES[end] <= limit:
            end += 1
        return _arithmetic_convolution_arithmetic_convolution_PRIMES[:end]
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[:2] = b'\x00\x00'
    bound = int(limit ** 0.5)
    for value in range(2, bound + 1):
        if sieve[value]:
            start = value * value
            sieve[start:limit + 1:value] = b'\x00' * ((limit - start) // value + 1)
    _arithmetic_convolution_arithmetic_convolution_PRIMES = [value for value in range(2, limit + 1) if sieve[value]]
    _arithmetic_convolution_arithmetic_convolution_PRIME_LIMIT = limit
    return _arithmetic_convolution_arithmetic_convolution_PRIMES

def divisor_zeta_transform(values, mod=None):
    limit = len(values) - 1
    for prime in _arithmetic_convolution_arithmetic_convolution_primes_up_to(limit):
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
    for prime in _arithmetic_convolution_arithmetic_convolution_primes_up_to(limit):
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
    for prime in _arithmetic_convolution_arithmetic_convolution_primes_up_to(limit):
        if mod is None:
            for value in range(limit // prime, 0, -1):
                values[value] += values[value * prime]
        else:
            for value in range(limit // prime, 0, -1):
                values[value] = (values[value] + values[value * prime]) % mod
    return values

def multiple_mobius_transform(values, mod=None):
    limit = len(values) - 1
    for prime in _arithmetic_convolution_arithmetic_convolution_primes_up_to(limit):
        if mod is None:
            for value in range(1, limit // prime + 1):
                values[value] -= values[value * prime]
        else:
            for value in range(1, limit // prime + 1):
                values[value] = (values[value] - values[value * prime]) % mod
    return values

def gcd_convolution(first, second, mod=DEFAULT_MOD):
    if len(first) != len(second):
        raise ValueError('input lengths must be equal')
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
        raise ValueError('input lengths must be equal')
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
import sys

def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    a = [0] + list(map(int, read().split()))
    b = [0] + list(map(int, read().split()))
    sys.stdout.write(' '.join(map(str, lcm_convolution(a, b)[1:])) + '\n')
if __name__ == '__main__':
    main()
