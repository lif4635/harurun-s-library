"""小さい素数を法に、巨大なn・kのStirling数を繰り返し求める。"""
from array import array

class StirlingNumberQuery:
    """第一種（符号付き）・第二種のStirling数を、小さい素数で割った余りを求める。"""
    __slots__ = ('prime', '_fact', '_ifact', 'first', 'second')

    def __init__(self, prime):
        """階乗を前計算する。各Stirling表はその種類を初めて問い合わせるときに作る。"""
        p = prime
        if not 2 <= p <= 65535:
            raise ValueError('prime must be a prime between 2 and 65535')
        d = 2
        while d * d <= p:
            if p % d == 0:
                raise ValueError('prime must be prime')
            d += 1
        self.prime = p
        fact = [1] * p
        for i in range(2, p):
            fact[i] = fact[i - 1] * i % p
        ifact = [1] * p
        ifact[-1] = pow(fact[-1], p - 2, p)
        for i in range(p - 1, 0, -1):
            ifact[i - 1] = ifact[i] * i % p
        self._fact = fact
        self._ifact = ifact
        self.first = self.second = None

    def _build(self, kind):
        p = self.prime
        table = [array('H', [1])]
        prev = [1]
        if kind == 1:
            for n in range(1, p):
                row = [0] * (n + 1)
                for k in range(1, n):
                    row[k] = (prev[k - 1] - (n - 1) * prev[k]) % p
                row[n] = 1
                table.append(array('H', row))
                prev = row
        else:
            for n in range(1, p):
                row = [0] * (n + 1)
                for k in range(1, n):
                    row[k] = (prev[k - 1] + k * prev[k]) % p
                row[n] = 1
                table.append(array('H', row))
                prev = row
        return table

    def _comb(self, n, k):
        if k < 0 or k > n:
            return 0
        p = self.prime
        fact = self._fact
        ifact = self._ifact
        result = 1
        while k:
            a = n % p
            b = k % p
            if a < b:
                return 0
            result = result * fact[a] % p * ifact[b] % p * ifact[a - b] % p
            n //= p
            k //= p
        return result

    def first_kind(self, n, k):
        """下降階乗x(x-1)…(x-n+1)のx^k係数をprimeで割った余りを返す。"""
        if n < 0 or k < 0 or k > n:
            return 0
        if k == n:
            return 1
        if k == 0:
            return 0
        p = self.prime
        (i, j) = divmod(n, p)
        if i > k:
            return 0
        (a, b) = divmod(k - i, p - 1)
        if b == 0 and j:
            b = p - 1
            a -= 1
        if a < 0 or a > i or b > j:
            return 0
        if self.first is None:
            self.first = self._build(1)
        result = self._comb(i, a) * self.first[j][b] % p
        return -result % p if i + a & 1 else result
    FirstKind = first_kind

    def second_kind(self, n, k):
        """n個の区別できる要素をk個の空でないグループへ分ける個数の剰余を返す。"""
        if n < 0 or k < 0 or k > n:
            return 0
        if k == n:
            return 1
        if k == 0:
            return 0
        p = self.prime
        (i, j) = divmod(k, p)
        (a, b) = divmod(n - i, p - 1)
        if b == 0:
            b = p - 1
            a -= 1
        if a < 0 or j > b:
            return 0
        if b == p - 1 and j == 0:
            return self._comb(a, i - 1)
        if self.second is None:
            self.second = self._build(2)
        return self._comb(a, i) * self.second[b][j] % p
    SecondKind = second_kind

    def __repr__(self):
        return f'StirlingNumberQuery(prime={self.prime})'
import sys

def main():
    read = sys.stdin.buffer.readline
    (t, p) = map(int, read().split())
    query = StirlingNumberQuery(p).first_kind
    result = []
    for _ in range(t):
        (n, k) = map(int, read().split())
        result.append(str(query(n, k)))
    sys.stdout.write('\n'.join(result))
if __name__ == '__main__':
    main()
