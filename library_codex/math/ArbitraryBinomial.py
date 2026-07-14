from math import isqrt

from library_codex.convolution.MultipointEvaluation import ProductTree
from library_codex.math.ChineseRemainder import chinese_remainder
from library_codex.prime.Factorization import factor_count, is_prime


class LargePrimeFactorial:
    """Factorials modulo a large prime via sqrt decomposition and multipoint eval."""

    __slots__ = ("mod", "cache")

    def __init__(self, mod):
        if not is_prime(mod):
            raise ValueError("mod must be prime")
        self.mod = mod
        self.cache = {0: 1, 1: 1}

    def factorial(self, n):
        mod = self.mod
        if not 0 <= n < mod:
            return 0 if n >= mod else 0
        cached = self.cache.get(n)
        if cached is not None:
            return cached
        if mod - 1 - n < isqrt(n):
            product = 1
            for value in range(n + 1, mod):
                product = product * value % mod
            result = -pow(product, -1, mod) % mod
            self.cache[n] = result
            return result
        block = max(1, isqrt(n))
        quotient, remainder = divmod(n, block)
        roots = [(-value) % mod for value in range(1, block + 1)]
        polynomial = ProductTree(roots, mod).polynomial
        points = [index * block % mod for index in range(quotient)]
        values = ProductTree(points, mod).evaluate(polynomial)
        result = 1
        for value in values:
            result = result * value % mod
        for value in range(quotient * block + 1, n + 1):
            result = result * value % mod
        self.cache[n] = result
        return result

    fact = factorial

    def binomial(self, n, k):
        if k < 0 or n < k:
            return 0
        mod = self.mod
        result = 1
        while n:
            n, nd = divmod(n, mod)
            k, kd = divmod(k, mod)
            if nd < kd:
                return 0
            denominator = self.factorial(kd) * self.factorial(nd - kd) % mod
            result = (result * self.factorial(nd) % mod
                      * pow(denominator, -1, mod) % mod)
        return result

    C = binomial


class PrimePowerBinomial:
    __slots__ = ("prime", "exponent", "mod", "delta", "prefix")

    def __init__(self, prime, exponent):
        self.prime = prime
        self.exponent = exponent
        self.mod = prime ** exponent
        self.delta = 1 if prime == 2 and exponent >= 3 else self.mod - 1
        self.prefix = [1]

    def _ensure(self, size):
        prefix = self.prefix
        mod = self.mod
        prime = self.prime
        value = prefix[-1]
        for index in range(len(prefix), size + 1):
            if index % prime:
                value = value * index % mod
            prefix.append(value)

    def _unit_factorial(self, n):
        result = 1
        prime = self.prime
        mod = self.mod
        while n:
            quotient, remainder = divmod(n, mod)
            self._ensure(remainder)
            result = (result * pow(self.delta, quotient, mod) % mod
                      * self.prefix[remainder] % mod)
            n //= prime
        return result

    def binomial(self, n, k):
        if n < 0 or k < 0 or n < k:
            return 0
        prime = self.prime
        exponent = 0
        a, b, c = n, k, n - k
        while a:
            a //= prime
            b //= prime
            c //= prime
            exponent += a - b - c
        if exponent >= self.exponent:
            return 0
        mod = self.mod
        numerator = self._unit_factorial(n)
        denominator = (self._unit_factorial(k)
                       * self._unit_factorial(n - k) % mod)
        return (numerator * pow(denominator, -1, mod) % mod
                * pow(prime, exponent, mod) % mod)

    C = binomial


class ArbitraryModBinomial:
    __slots__ = ("mod", "components", "moduli")

    def __init__(self, mod):
        if mod < 1:
            raise ValueError("mod must be positive")
        self.mod = mod
        self.components = []
        self.moduli = []
        for prime, exponent in factor_count(mod).items():
            modulus = prime ** exponent
            if exponent == 1 and prime > 2_000_000:
                component = LargePrimeFactorial(prime)
            else:
                component = PrimePowerBinomial(prime, exponent)
            self.components.append(component)
            self.moduli.append(modulus)

    def binomial(self, n, k):
        if self.mod == 1:
            return 0
        residues = [component.binomial(n, k)
                    for component in self.components]
        return chinese_remainder(residues, self.moduli)[0]

    C = binomial
    nCr = binomial


prime_power_binomial = PrimePowerBinomial
arbitrary_mod_binomial = ArbitraryModBinomial
FactLarge = LargePrimeFactorial
