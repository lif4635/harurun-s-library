"""素数と原始根を固定して前計算し、離散対数を1回O(1)で求める。"""

from math import isqrt


class FixedDiscreteLog:
    """primeと原始根rootに対し、呼び出した値の最小非負の離散対数を返す。"""

    __slots__ = ("prime", "root", "_logs", "_before", "_after", "_shift", "_mask", "_scale")

    def __init__(self, prime, root):
        if not 2 <= prime <= 10**9 or not 1 <= root < prime:
            raise ValueError("require 2 <= prime <= 10^9 and 1 <= root < prime")
        limit = isqrt(prime)
        least = [0] * (limit + 1)
        primes = []
        for value in range(2, limit + 1):
            if least[value] == 0:
                least[value] = value
                primes.append(value)
            for factor in primes:
                product = value * factor
                if product > limit:
                    break
                least[product] = factor
                if factor == least[value]:
                    break
        remaining = prime - 1
        for factor in primes:
            if prime % factor == 0:
                raise ValueError("prime must be prime")
            if remaining % factor == 0:
                if pow(root, (prime - 1) // factor, prime) == 1:
                    raise ValueError("root must be a primitive root")
                while remaining % factor == 0:
                    remaining //= factor
        if remaining > 1 and pow(root, (prime - 1) // remaining, prime) == 1:
            raise ValueError("root must be a primitive root")
        self.prime = prime
        self.root = root
        self._before = self._after = ()
        self._shift = self._mask = self._scale = 0
        if prime <= 4096:
            logs = [0] * prime
            value = 1
            for exponent in range(prime - 1):
                logs[value] = exponent
                value = value * root % prime
            self._logs = logs
            return
        bound = 1
        while bound ** 3 < prime:
            bound <<= 1
        scale = bound * bound
        shift = bound.bit_length()
        mask = (1 << shift) - 1
        before = [0] * (scale + 1)
        for numerator in range(bound + 1):
            for denominator in range(1 if numerator == 1 else numerator + 1, bound + 1):
                index = numerator * scale // denominator
                if before[index] == 0:
                    before[index] = numerator << shift | denominator
        after = before.copy()
        previous = before[0]
        for i in range(scale + 1):
            if before[i]:
                previous = before[i]
            else:
                before[i] = previous
        following = after[-1]
        for i in range(scale, -1, -1):
            if after[i]:
                following = after[i]
            else:
                after[i] = following
        logs = [0] * (scale + 1)
        width = min(prime - 1, isqrt(prime * len(primes)) + 1)
        baby = {}
        value = 1
        for exponent in range(width):
            baby[value] = exponent
            value = value * root % prime
        step = pow(value, -1, prime)
        for factor in primes:
            value = factor
            offset = 0
            while value not in baby:
                value = value * step % prime
                offset += width
            logs[factor] = offset + baby[value]
        del baby
        order = prime - 1
        half = order >> 1
        for value in range(4, limit + 1):
            factor = least[value]
            if factor != value:
                logs[value] = (logs[factor] + logs[value // factor]) % order
        for value in range(limit + 1, scale + 1):
            quotient, remainder = divmod(prime, value)
            logs[value] = (half + logs[remainder] - logs[quotient]) % order
        self._logs = logs
        self._before = before
        self._after = after
        self._shift = shift
        self._mask = mask
        self._scale = scale

    def __call__(self, value):
        """root**x % prime == value % primeとなる最小のx。0の剰余なら-1。"""
        prime = self.prime
        value %= prime
        if value == 0:
            return -1
        logs = self._logs
        if value < len(logs):
            return logs[value]
        index = value * self._scale // prime
        fraction = self._before[index]
        denominator = fraction & self._mask
        residual = value * denominator - prime * (fraction >> self._shift)
        if abs(residual) > self._scale:
            fraction = self._after[index]
            denominator = fraction & self._mask
            residual = value * denominator - prime * (fraction >> self._shift)
        exponent = logs[abs(residual)] - logs[denominator]
        if residual < 0:
            exponent += (prime - 1) >> 1
        return exponent % (prime - 1)

    def __repr__(self):
        return f"FixedDiscreteLog(prime={self.prime}, root={self.root})"
