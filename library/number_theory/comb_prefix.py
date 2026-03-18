class CombPrefix:
    __slots__ = ("n", "k", "s", "comb", "inv2")

    def __init__(self, comb):
        self.n = self.k = 0
        self.s = 1
        self.comb = comb
        self.inv2 = (comb.mod + 1) // 2

    def move(self, n, k):
        C = self.comb.C
        mod = self.comb.mod
        
        while self.n < n:
            self.s = (2 * self.s - C(self.n, self.k)) % mod
            self.n += 1
        while self.k > k:
            self.s = (self.s - C(self.n, self.k)) % mod
            self.k -= 1
        while self.n > n:
            self.n -= 1
            self.s = (self.s + C(self.n, self.k)) * self.inv2 % mod
        while self.k < k:
            self.k += 1
            self.s = (self.s + C(self.n, self.k)) % mod
            
        return self.s

    def get(self):
        return self.s

class Comb:
    __slots__ = ("mod", "fac", "finv", "inv")

    def __init__(self, lim: int, mod: int):
        self.mod = mod
        self.fac = [1] * (lim + 1)
        self.finv = [1] * (lim + 1)
        self.inv = [1] * (lim + 2)
        
        for i in range(2, lim + 2):
            self.inv[i] = mod - self.inv[mod % i] * (mod // i) % mod
            
        for i in range(1, lim + 1):
            self.fac[i] = self.fac[i - 1] * i % mod
            
        self.finv[lim] = pow(self.fac[lim], -1, mod)
        for i in range(lim, 2, -1):
            self.finv[i - 1] = self.finv[i] * i % mod

    def C(self, a, b):
        if b < 0 or a < b or a < 0: return 0
        return self.fac[a] * self.finv[b] % self.mod * self.finv[a - b] % self.mod

    def __call__(self, a, b): return self.C(a, b)
    def P(self, a, b): return self.fac[a] * self.finv[a - b] % self.mod if 0 <= b <= a else 0
    def H(self, a, b): return self.C(a + b - 1, b)

    def prefix(self) -> CombPrefix:
        return CombPrefix(self)
