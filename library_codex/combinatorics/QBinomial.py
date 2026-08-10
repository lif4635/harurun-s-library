"""q二項係数を計算する。"""

import math

class QBinomial:
    __slots__ = ("q", "mod", "order", "factorial", "inverse_factorial")

    def __init__(self, q, maximum, mod=998244353):
        self.q = q % mod
        self.mod = mod
        quantum = 1
        quantum_numbers = []
        factorial = [1]
        order = None
        for index in range(1, maximum + 2):
            quantum_numbers.append(quantum)
            factorial.append(factorial[-1] * quantum % mod)
            quantum = (quantum * self.q + 1) % mod
            if quantum == 0:
                order = index + 1
                break
        if order is None:
            order = maximum + 2
        self.order = order
        factorial = factorial[:order]
        inverse_factorial = [1] * len(factorial)
        inverse_factorial[-1] = pow(factorial[-1], -1, mod)
        for index in range(len(factorial) - 1, 0, -1):
            inverse_factorial[index - 1] = (
                inverse_factorial[index] * quantum_numbers[index - 1] % mod
            )
        self.factorial = factorial
        self.inverse_factorial = inverse_factorial

    def C(self, number, chosen):
        if chosen < 0 or chosen > number:
            return 0
        order = self.order
        high_n, low_n = divmod(number, order)
        high_k, low_k = divmod(chosen, order)
        if low_k > low_n:
            return 0
        low = (self.factorial[low_n] * self.inverse_factorial[low_k]
               % self.mod * self.inverse_factorial[low_n - low_k] % self.mod)
        return math.comb(high_n, high_k) % self.mod * low % self.mod
