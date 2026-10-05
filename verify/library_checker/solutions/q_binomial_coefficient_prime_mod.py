"""階乗表を使うCombと、小さいk向けの乗法式で二項係数を計算する。"""
DEFAULT_MOD = 998244353

class Comb:
    """素数mod上の階乗表を必要なところまで自動で拡張する。"""
    __slots__ = ('mod', 'factorial', 'inverse_factorial')

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
            self.inverse_factorial[value - 1] = self.inverse_factorial[value] * value % mod

    def F(self, n):
        """n!をmodで割った余りを返す。O(1)、表の拡張時は償却O(n)。"""
        if n < 0:
            raise ValueError('n must be nonnegative')
        self.ensure(n)
        return self.factorial[n]

    def Fi(self, n):
        """1/n!をmodで割った余りを返す。O(1)、表の拡張時は償却O(n)。"""
        if n < 0:
            raise ValueError('n must be nonnegative')
        self.ensure(n)
        return self.inverse_factorial[n]

    def inv(self, n):
        """nのmodにおける乗法逆元を返す。O(1)、表の拡張時は償却O(n)。"""
        if not 0 < n < self.mod:
            raise ValueError('n must satisfy 0 < n < mod')
        self.ensure(n)
        return self.factorial[n - 1] * self.inverse_factorial[n] % self.mod

    def C(self, n, k):
        """二項係数C(n, k)を返す。O(1)、表の拡張時は償却O(n)。"""
        if k < 0 or n < k or n < 0:
            return 0
        self.ensure(n)
        return self.factorial[n] * self.inverse_factorial[k] % self.mod * self.inverse_factorial[n - k] % self.mod

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
        if n < 0 or m < 0 or k < 0 or (m > n + k):
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
'固定したqと素数の法で、q二項係数を繰り返し求める。'

class QBinomial:
    """q階乗表と通常の二項係数表を使う。q=0・1や小さい位数にも対応する。"""
    __slots__ = ('q', 'mod', 'order', 'factorial', 'inverse_factorial', '_ordinary')

    def __init__(self, q, maximum, mod=998244353):
        """number<=maximumの問い合わせ用に表を構築する。modは素数。"""
        if maximum < 0 or mod < 2:
            raise ValueError('requires maximum >= 0 and prime mod >= 2')
        q %= mod
        self.q = q
        self.mod = mod
        self.order = 0
        self.factorial = [1]
        self.inverse_factorial = [1]
        self._ordinary = None
        if q == 0:
            return
        if q == 1:
            limit = min(maximum, mod - 1)
            factorial = [1] * (limit + 1)
            inverse = [1] * (limit + 1)
            for index in range(1, limit + 1):
                factorial[index] = factorial[index - 1] * index % mod
            inverse[-1] = pow(factorial[-1], -1, mod)
            for index in range(limit, 0, -1):
                inverse[index - 1] = inverse[index] * index % mod
            ordinary = Comb(0, mod)
            ordinary.factorial = factorial
            ordinary.inverse_factorial = inverse
            self._ordinary = ordinary
            self.factorial = factorial
            self.inverse_factorial = inverse
            if maximum >= mod - 1:
                self.order = mod
            return
        quantum = 1
        factorial = self.factorial
        for index in range(1, maximum + 2):
            factorial.append(factorial[-1] * quantum % mod)
            quantum = (quantum * q + 1) % mod
            if quantum == 0:
                self.order = index + 1
                break
        inverse = [1] * len(factorial)
        inverse[-1] = pow(factorial[-1], -1, mod)
        inverse_q = pow(q, -1, mod)
        for index in range(len(factorial) - 1, 0, -1):
            quantum = (quantum - 1) * inverse_q % mod
            inverse[index - 1] = inverse[index] * quantum % mod
        self.inverse_factorial = inverse
        high = min(maximum // self.order, mod - 1) if self.order else 0
        self._ordinary = Comb(high, mod)

    def C(self, number, chosen):
        """q二項係数をmodで割った余り。範囲外のchosenには0を返す。"""
        if number < 0 or chosen < 0 or chosen > number:
            return 0
        if self.q == 0:
            return 1
        factorial = self.factorial
        inverse = self.inverse_factorial
        mod = self.mod
        if number < len(factorial):
            return factorial[number] * inverse[chosen] % mod * inverse[number - chosen] % mod
        order = self.order
        if not order:
            raise ValueError('number exceeds the prepared range')
        (high_n, low_n) = divmod(number, order)
        (high_k, low_k) = divmod(chosen, order)
        if low_k > low_n:
            return 0
        result = factorial[low_n] * inverse[low_k] % mod * inverse[low_n - low_k] % mod
        ordinary = self._ordinary
        while high_n:
            (high_n, n) = divmod(high_n, mod)
            (high_k, k) = divmod(high_k, mod)
            if k > n:
                return 0
            if n < len(ordinary.factorial):
                result = result * ordinary.C(n, k) % mod
            else:
                result = result * comb_small_k(n, k, mod) % mod
        return result
import sys
read = sys.stdin.buffer.readline
(count, mod, q) = map(int, read().split())
data = list(map(int, sys.stdin.buffer.read().split()))
maximum = max(data[::2], default=0)
table = QBinomial(q, maximum, mod)
result = [str(table.C(data[i], data[i + 1])) for i in range(0, count * 2, 2)]
sys.stdout.write('\n'.join(result))
