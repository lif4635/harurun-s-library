"""階乗表を使うCombと、小さいk向けの乗法式で二項係数を計算する。"""

DEFAULT_MOD = 998244353

class Comb:
    """素数mod上の階乗表を必要なところまで自動で拡張する。"""

    __slots__ = ("mod", "factorial", "inverse_factorial")

    def __init__(self, size=0, mod=DEFAULT_MOD):
        """0からsizeまでの階乗表を構築する。O(size)。"""
        self.mod = mod
        self.factorial = [1]
        self.inverse_factorial = [1]
        self.ensure(size)

    def ensure(self, size):
        """階乗表と逆階乗表をsizeまで拡張する。"""
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

    def F(self, n):
        """n!をmodで割った余りを返す。O(1)、表の拡張時は償却O(n)。"""
        if n < 0:
            raise ValueError("n must be nonnegative")
        self.ensure(n)
        return self.factorial[n]

    def Fi(self, n):
        """1/n!をmodで割った余りを返す。O(1)、表の拡張時は償却O(n)。"""
        if n < 0:
            raise ValueError("n must be nonnegative")
        self.ensure(n)
        return self.inverse_factorial[n]

    def inv(self, n):
        """nのmodにおける乗法逆元を返す。O(1)、表の拡張時は償却O(n)。"""
        if not 0 < n < self.mod:
            raise ValueError("n must satisfy 0 < n < mod")
        self.ensure(n)
        return self.factorial[n - 1] * self.inverse_factorial[n] % self.mod

    def C(self, n, k):
        """二項係数C(n, k)を返す。O(1)、表の拡張時は償却O(n)。"""
        if k < 0 or n < k or n < 0:
            return 0
        self.ensure(n)
        return (self.factorial[n] * self.inverse_factorial[k]
                % self.mod * self.inverse_factorial[n - k] % self.mod)

    def __call__(self, n, k):
        """C(n, k)を返す。O(1)、表の拡張時は償却O(n)。"""
        return self.C(n, k)

    def P(self, n, k):
        """順列数P(n, k)を返す。O(1)、表の拡張時は償却O(n)。"""
        if k < 0 or n < k or n < 0:
            return 0
        self.ensure(n)
        return self.factorial[n] * self.inverse_factorial[n - k] % self.mod

    def H(self, n, k):
        """n種類から重複を許してk個選ぶ重複組合せH(n, k)を返す。O(1)。"""
        if n == 0:
            return int(k == 0)
        return self.C(n + k - 1, k)

    def catalan(self, n, m, k=0):
        """y <= x + kを保つ(n, m)までの格子路数を返す。O(1)。

        (0, 0)から右へn回、上へm回進む。境界y = x + k上は通れるが、
        その上へ出る経路は数えない。
        """
        if n < 0 or m < 0 or k < 0 or m > n + k:
            return 0
        return (self.C(n + m, m) - self.C(n + m, m - k - 1)) % self.mod

def comb_small_k(n, k, mod=DEFAULT_MOD):
    """nが大きくkが小さいときに二項係数C(n, k)を乗法式で求める。

    O(min(k, n-k))。1からmin(k, n-k)までがmodで可逆である必要がある。
    """
    if k < 0 or n < k:
        return 0
    k = min(k, n - k)
    numerator = denominator = 1
    for i in range(1, k + 1):
        numerator = numerator * (n - k + i) % mod
        denominator = denominator * i % mod
    return numerator * pow(denominator, -1, mod) % mod
