"""合成数の法や、大きい素数の法で二項係数を求める。"""

from math import isqrt

from library_codex.polynomial.MultipointEvaluation import ProductTree
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

    def C(self, n, k):
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

class PrimePowerBinomial:
    """素数冪を法とする二項係数を、素因子を除いた階乗表で求める。"""

    __slots__ = ("prime", "exponent", "mod", "delta", "prefix", "inverse_prefix", "powers")

    def __init__(self, prime, exponent):
        """prime**exponentを法とする表を用意する。階乗表は初回のCで拡張する。"""
        if prime < 2 or exponent < 1:
            raise ValueError("requires prime >= 2 and exponent >= 1")
        self.prime = prime
        self.exponent = exponent
        self.mod = prime ** exponent
        self.delta = 1 if prime == 2 and exponent >= 3 else self.mod - 1
        self.prefix = [1]
        self.inverse_prefix = [1]
        self.powers = [prime ** i for i in range(exponent)]

    def _ensure(self, size):
        prefix = self.prefix
        old = len(prefix)
        if size < old:
            return
        mod = self.mod
        size = min(mod - 1, max(size * 2, old * 2 - 1))
        prime = self.prime
        value = prefix[-1]
        for index in range(old, size + 1):
            if index % prime:
                value = value * index % mod
            prefix.append(value)
        inverse = self.inverse_prefix
        inverse.extend([1] * (size + 1 - old))
        value = pow(value, -1, mod)
        for index in range(size, old - 1, -1):
            inverse[index] = value
            if index % prime:
                value = value * index % mod

    def C(self, n, k):
        """C(n,k)を法で割った余り。表の拡張を除きO(log_prime(n+1))時間。"""
        if n < 0 or k < 0 or n < k:
            return 0
        if k == 0 or k == n:
            return 1
        mod = self.mod
        prime = self.prime
        limit = self.exponent
        if len(self.prefix) <= min(n, mod - 1):
            a, b, c = n, k, n - k
            required = valuation = 0
            while a:
                required = max(required, a % mod, b % mod, c % mod)
                a //= prime
                b //= prime
                c //= prime
                valuation += a - b - c
                if valuation >= limit:
                    return 0
            self._ensure(required)
        prefix, inverse = self.prefix, self.inverse_prefix
        exponent = high = depth = 0
        result = 1
        remaining = n - k
        while n:
            result = result * prefix[n % mod] % mod
            result = result * inverse[k % mod] % mod
            result = result * inverse[remaining % mod] % mod
            n //= prime
            k //= prime
            remaining //= prime
            carry = n - k - remaining
            exponent += carry
            if exponent >= limit:
                return 0
            depth += 1
            if depth >= limit:
                high += carry
        if high & 1:
            result = result * self.delta % mod
        return result * self.powers[exponent] % mod

class ArbitraryModBinomial:
    """法を素数冪へ分解し、各二項係数を前計算したCRT係数で合成する。"""

    __slots__ = ("mod", "components", "moduli", "coefficients")

    def __init__(self, mod):
        """固定した正の法で、繰り返しC(n,k)を計算できる状態を作る。"""
        if mod < 1:
            raise ValueError("mod must be positive")
        self.mod = mod
        self.components = []
        self.moduli = []
        self.coefficients = []
        for prime, exponent in factor_count(mod).items():
            modulus = prime ** exponent
            if exponent == 1 and prime > 2_000_000:
                component = LargePrimeFactorial(prime)
            else:
                component = PrimePowerBinomial(prime, exponent)
            self.components.append(component)
            self.moduli.append(modulus)
            quotient = mod // modulus
            self.coefficients.append(quotient * pow(quotient, -1, modulus) % mod)

    def C(self, n, k):
        """C(n,k)をmodで割った余り。n<0またはkが範囲外なら0。"""
        if self.mod == 1 or n < 0 or k < 0 or k > n:
            return 0
        answer = 0
        for component, coefficient in zip(self.components, self.coefficients):
            answer += component.C(n, k) * coefficient
        return answer % self.mod
