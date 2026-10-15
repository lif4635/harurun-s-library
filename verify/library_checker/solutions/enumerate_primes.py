"""素数列挙、最小素因数・Möbius・φの表、素数と平方因子を持たない数の個数。"""
from math import isqrt

class LinearSieve:
    __slots__ = ('limit', 'primes', 'least_prime', 'mobius', 'phi')

    def __init__(self, limit):
        if limit < 0:
            raise ValueError('limit must be nonnegative')
        least = [0] * (limit + 1)
        mobius = [0] * (limit + 1)
        phi = [0] * (limit + 1)
        if limit >= 1:
            mobius[1] = phi[1] = 1
        primes = []
        for value in range(2, limit + 1):
            if least[value] == 0:
                least[value] = value
                primes.append(value)
                mobius[value] = -1
                phi[value] = value - 1
            for prime in primes:
                product = value * prime
                if product > limit:
                    break
                least[product] = prime
                if value % prime == 0:
                    mobius[product] = 0
                    phi[product] = phi[value] * prime
                    break
                mobius[product] = -mobius[value]
                phi[product] = phi[value] * (prime - 1)
        self.limit = limit
        self.primes = primes
        self.least_prime = least
        self.mobius = mobius
        self.phi = phi

    def is_prime(self, value):
        return 2 <= value <= self.limit and self.least_prime[value] == value

    def factor_count(self, value):
        if not 1 <= value <= self.limit:
            raise ValueError('value outside sieve')
        result = []
        while value > 1:
            prime = self.least_prime[value]
            exponent = 0
            while value % prime == 0:
                value //= prime
                exponent += 1
            result.append((prime, exponent))
        return result

def prime_sieve(limit):
    """limit以下の素数を昇順listで返す。時間 O(N log log N)。"""
    return enumerate_primes(limit)[1]

def enumerate_primes(limit, step=1, offset=0):
    """素数の総数と、素数列のoffset番目からstep個おきの値を返す。"""
    if limit < 0 or step <= 0 or (not 0 <= offset < step):
        raise ValueError('require limit >= 0 and 0 <= offset < step')
    if limit < 2:
        return (0, [])
    root = isqrt(limit)
    small = bytearray(b'\x01') * ((root + 1) // 2)
    if small:
        small[0] = 0
    for i in range(1, (isqrt(root) + 1) // 2):
        if small[i]:
            prime = 2 * i + 1
            start = prime * prime // 2
            small[start::prime] = b'\x00' * ((len(small) - 1 - start) // prime + 1)
    primes = [2 * i + 1 for i in range(1, len(small)) if small[i]]
    block = max(1 << 18, root)
    total = 1
    result = [2] if offset == 0 else []
    wanted = offset + step if offset == 0 else offset
    for low in range(3, limit + 1, 2 * block):
        size = min(block, (limit - low) // 2 + 1)
        flags = bytearray(b'\x01') * size
        high = low + 2 * size
        for prime in primes:
            square = prime * prime
            if square >= high:
                break
            first = max(square, (low + prime - 1) // prime * prime)
            if first & 1 == 0:
                first += prime
            start = (first - low) // 2
            flags[start::prime] = b'\x00' * ((size - 1 - start) // prime + 1)
        count = flags.count(1)
        if wanted < total + count:
            rank = total
            for i in range(size):
                if flags[i]:
                    if rank == wanted:
                        result.append(low + 2 * i)
                        wanted += step
                    rank += 1
        total += count
    return (total, result)

def prime_count(number):
    """Lucy-DP prime counting in about O(n^(3/4)/log n)."""
    if number < 2:
        return 0
    quotients = []
    left = 1
    while left <= number:
        quotient = number // left
        quotients.append(quotient)
        left = number // quotient + 1
    index = {value: i for (i, value) in enumerate(quotients)}
    count = [value - 1 for value in quotients]
    limit = isqrt(number)
    composite = bytearray(limit + 1)
    for prime in range(2, limit + 1):
        if composite[prime]:
            continue
        previous = count[index[prime - 1]]
        square = prime * prime
        for (i, value) in enumerate(quotients):
            if value < square:
                break
            count[i] -= count[index[value // prime]] - previous
        start = square
        for multiple in range(start, limit + 1, prime):
            composite[multiple] = 1
    return count[0]

def count_square_free(number):
    """Count positive square-free integers <= number in O(sqrt(number))."""
    if number <= 0:
        return 0
    limit = isqrt(number)
    mobius = LinearSieve(limit).mobius
    return sum((mobius[value] * (number // (value * value)) for value in range(1, limit + 1)))

def sum_totient(limit):
    if limit < 1:
        return 0
    return sum(LinearSieve(limit).phi[1:])
import sys
(n, step, offset) = map(int, sys.stdin.buffer.read().split())
(count, values) = enumerate_primes(n, step, offset)
print(count, len(values))
print(*values)
