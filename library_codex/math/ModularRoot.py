from math import gcd, isqrt

from library_codex.prime.Factorization import factor_count


def primitive_root(prime):
    if prime < 2:
        raise ValueError("prime must be at least 2")
    if prime == 2:
        return 1
    known = {
        167772161: 3,
        469762049: 3,
        754974721: 11,
        998244353: 3,
        1000000007: 5,
    }
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


class _PrimeOrderLog:
    __slots__ = ("baby", "step", "size", "period", "mod")

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
        raise ArithmeticError("discrete logarithm in prime-order subgroup failed")


def _prime_power_root(value, divisor, exponent, prime):
    coprime = prime - 1
    valuation = 0
    while coprime % divisor == 0:
        coprime //= divisor
        valuation += 1
    power = divisor ** exponent
    inverse = pow((-coprime) % power, -1, power)
    root = pow(value, (coprime * inverse + 1) // power, prime)
    error = pow(value, coprime * inverse, prime)
    if error == 1:
        return root
    if valuation <= exponent:
        raise ArithmeticError("invalid prime-power root state")
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
    logarithm = _PrimeOrderLog(
        generator, valuation - exponent, divisor, prime
    )
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
        raise ValueError("prime must be at least 2")
    if exponent < 0:
        raise ValueError("exponent must be nonnegative")
    value %= prime
    if exponent == 0:
        return 1 if value == 1 else -1
    if value <= 1 or exponent == 1:
        return value
    common = gcd(prime - 1, exponent)
    if pow(value, (prime - 1) // common, prime) != 1:
        return -1
    reduced_order = (prime - 1) // common
    value = pow(
        value,
        pow(exponent // common, -1, reduced_order),
        prime,
    )
    for divisor, multiplicity in factor_count(common).items():
        value = _prime_power_root(
            value, divisor, multiplicity, prime
        )
    return value


def _power_leq(base, exponent, limit):
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
        raise ValueError("value must be nonnegative")
    if exponent <= 0:
        raise ValueError("exponent must be positive")
    if value <= 1 or exponent == 1:
        return value
    if exponent == 2:
        return isqrt(value)
    if exponent >= value.bit_length():
        return 1
    upper = 1 << ((value.bit_length() + exponent - 1) // exponent)
    lower = upper >> 1
    while lower + 1 < upper:
        middle = (lower + upper) >> 1
        if _power_leq(middle, exponent, value):
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
