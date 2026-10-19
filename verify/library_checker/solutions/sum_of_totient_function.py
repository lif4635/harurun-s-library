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
    """number以下の素数の個数を返す。時間 O(N^(3/4)/log N)、メモリ O(√N)。"""
    if number < 2:
        return 0
    root = isqrt(number)
    size = (root + 1) // 2
    small = list(range(size))
    large = [(number // (2 * i + 1) - 1) // 2 for i in range(size)]
    for position in range(1, size):
        previous = small[position - 1]
        if small[position] == previous:
            continue
        prime = 2 * position + 1
        square = prime * prime
        stop = min(size, (number // square + 1) // 2)
        split = min(stop, ((2 * size - 1) // prime + 1) // 2)
        source = position
        for i in range(split):
            large[i] -= large[source] - previous
            source += prime
        divisor = prime * (2 * split + 1)
        for i in range(split, stop):
            large[i] -= small[(number // divisor - 1) // 2] - previous
            divisor += 2 * prime
        for i in range(size - 1, square // 2 - 1, -1):
            small[i] -= small[((2 * i + 1) // prime - 1) // 2] - previous
    return large[0] + 1

def count_square_free(number):
    """1以上number以下で、1以外の平方数を因子に持たない整数を数える。"""
    if number <= 0:
        return 0
    count = max(1, int(number ** 0.2))
    while (count + 1) ** 5 <= number:
        count += 1
    while count ** 5 > number:
        count -= 1
    limit = isqrt(number // count)
    prefix = [1] * (limit + 1)
    composite = bytearray(limit + 1)
    for prime in range(2, limit + 1):
        if not composite[prime]:
            prefix[prime] = -1
            for multiple in range(2 * prime, limit + 1, prime):
                composite[multiple] = 1
                prefix[multiple] = -prefix[multiple]
            square = prime * prime
            for multiple in range(square, limit + 1, square):
                prefix[multiple] = 0
    del composite
    prefix[0] = 0
    total = 0
    running = 0
    for value in range(1, limit + 1):
        mu = prefix[value]
        if mu:
            total += mu * (number // (value * value))
        running += mu
        prefix[value] = running
    large = [0] * count
    total -= (count - 1) * running
    for index in range(count - 1, 0, -1):
        value = isqrt(number // index)
        root = isqrt(value)
        boundary = min(root, value // (limit + 1))
        mertens = 1
        for divisor in range(2, boundary + 1):
            mertens -= large[index * divisor * divisor]
        for divisor in range(max(2, boundary + 1), root + 1):
            mertens -= prefix[value // divisor]
        previous = value
        for quotient in range(1, value // (root + 1) + 1):
            end = value // (quotient + 1)
            mertens -= (previous - end) * prefix[quotient]
            previous = end
        large[index] = mertens
        total += mertens
    return total

def sum_totient(limit, mod=None):
    """1からlimitまでのφの総和を返す。modを指定するとその余りを返す。"""
    if mod is not None and mod <= 0:
        raise ValueError('mod must be positive')
    if limit < 1:
        return 0
    if mod == 1:
        return 0
    cutoff = min(limit, max(64, int(limit ** (2.0 / 3.0))))
    prefix = list(range(cutoff + 1))
    for prime in range(2, cutoff + 1):
        if prefix[prime] == prime:
            for multiple in range(prime, cutoff + 1, prime):
                prefix[multiple] -= prefix[multiple] // prime
    total = 0
    if mod is None:
        for value in range(1, cutoff + 1):
            total += prefix[value]
            prefix[value] = total
    else:
        for value in range(1, cutoff + 1):
            total = (total + prefix[value]) % mod
            prefix[value] = total
    size = limit // (cutoff + 1)
    large = [0] * (size + 1)
    for index in range(size, 0, -1):
        value = limit // index
        root = isqrt(value)
        result = value * (value + 1) // 2
        boundary = min(root, value // (cutoff + 1))
        for divisor in range(2, boundary + 1):
            result -= large[index * divisor]
        for divisor in range(max(2, boundary + 1), root + 1):
            result -= prefix[value // divisor]
        previous = root
        for quotient in range(value // (root + 1), 0, -1):
            end = value // quotient
            result -= (end - previous) * prefix[quotient]
            previous = end
        large[index] = result if mod is None else result % mod
    return large[1] if size else prefix[limit]
import sys
print(sum_totient(int(sys.stdin.buffer.read()), 998244353))
