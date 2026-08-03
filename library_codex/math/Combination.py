"""階乗前計算または乗法式で二項係数・順列数を計算する。"""

DEFAULT_MOD = 998244353

class Combination:
    """Dynamically extended factorial table over a prime modulus."""

    __slots__ = ("mod", "factorial", "inverse_factorial")

    def __init__(self, size=0, mod=DEFAULT_MOD):
        self.mod = mod
        self.factorial = [1]
        self.inverse_factorial = [1]
        self.ensure(size)

    def ensure(self, size):
        old = len(self.factorial) - 1
        if size <= old:
            return
        mod = self.mod
        self.factorial.extend([1] * (size - old))
        for value in range(old + 1, size + 1):
            self.factorial[value] = self.factorial[value - 1] * value % mod
        self.inverse_factorial.extend([1] * (size - old))
        self.inverse_factorial[size] = pow(self.factorial[size], -1, mod)
        for value in range(size, old + 1, -1):
            self.inverse_factorial[value - 1] = (
                self.inverse_factorial[value] * value % mod
            )

    def factorial_value(self, n):
        self.ensure(n)
        return self.factorial[n]

    def binomial(self, n, k):
        if k < 0 or n < k or n < 0:
            return 0
        self.ensure(n)
        return (self.factorial[n] * self.inverse_factorial[k]
                % self.mod * self.inverse_factorial[n - k] % self.mod)

    C = binomial
    nCr = binomial

    def permutation(self, n, k):
        if k < 0 or n < k or n < 0:
            return 0
        self.ensure(n)
        return self.factorial[n] * self.inverse_factorial[n - k] % self.mod

    P = permutation
    nPr = permutation

    def multiset(self, n, k):
        if n == 0:
            return int(k == 0)
        return self.binomial(n + k - 1, k)

def binomial_multiplicative(n, k, mod=DEFAULT_MOD):
    """O(k) binomial for huge n and small k over a prime modulus."""
    if k < 0 or n < k:
        return 0
    k = min(k, n - k)
    numerator = denominator = 1
    for i in range(1, k + 1):
        numerator = numerator * (n - k + i) % mod
        denominator = denominator * i % mod
    return numerator * pow(denominator, -1, mod) % mod

