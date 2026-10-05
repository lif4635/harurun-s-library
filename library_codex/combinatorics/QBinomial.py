"""固定したqと素数の法で、q二項係数を繰り返し求める。"""

from library_codex.combinatorics.Combination import Comb, comb_small_k


class QBinomial:
    """q階乗表と通常の二項係数表を使う。q=0・1や小さい位数にも対応する。"""

    __slots__ = ("q", "mod", "order", "factorial", "inverse_factorial", "_ordinary")

    def __init__(self, q, maximum, mod=998244353):
        """number<=maximumの問い合わせ用に表を構築する。modは素数。"""
        if maximum < 0 or mod < 2:
            raise ValueError("requires maximum >= 0 and prime mod >= 2")
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
            raise ValueError("number exceeds the prepared range")
        high_n, low_n = divmod(number, order)
        high_k, low_k = divmod(chosen, order)
        if low_k > low_n:
            return 0
        result = factorial[low_n] * inverse[low_k] % mod * inverse[low_n - low_k] % mod
        ordinary = self._ordinary
        while high_n:
            high_n, n = divmod(high_n, mod)
            high_k, k = divmod(high_k, mod)
            if k > n:
                return 0
            if n < len(ordinary.factorial):
                result = result * ordinary.C(n, k) % mod
            else:
                result = result * comb_small_k(n, k, mod) % mod
        return result
