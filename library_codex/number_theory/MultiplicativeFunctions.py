from math import isqrt

from library_codex.prime.Sieve import LinearSieve, prime_sieve
from library_codex.prime.Sieve import sum_totient as _sum_totient


class DirichletQuotientSeries:
    """Prefix sums stored at all distinct values floor(N/i)."""

    __slots__ = ("n", "square", "size", "data", "mod")

    def __init__(self, n, values=None, mod=None):
        if n < 1:
            raise ValueError("n must be positive")
        self.n = n
        self.square = isqrt(n)
        self.size = self.square + n // (self.square + 1) + 1
        self.data = [0] * self.size if values is None else list(values)
        if len(self.data) != self.size:
            raise ValueError("invalid quotient-series storage length")
        self.mod = mod

    def index(self, value):
        return value if value <= self.square else self.size - self.n // value

    idx = index

    def value(self, index):
        return index if index <= self.square else self.n // (self.size - index)

    val = value

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value if self.mod is None else value % self.mod

    def prefix(self):
        for index in range(self.size - 1):
            self.data[index + 1] += self.data[index]
            if self.mod is not None:
                self.data[index + 1] %= self.mod
        return self

    pref = prefix

    def difference(self):
        for index in range(self.size - 1, 0, -1):
            self.data[index] -= self.data[index - 1]
            if self.mod is not None:
                self.data[index] %= self.mod
        return self

    diff = difference


def dirichlet_multiply(first, second):
    if first.n != second.n or first.mod != second.mod:
        raise ValueError("series parameters differ")
    n = first.n
    square = first.square
    size = first.size
    mod = first.mod
    a, b = first.data, second.data
    if mod is not None:
        a = [x % mod for x in a]
        b = [x % mod for x in b]
    da = [a[i] - a[i - 1] for i in range(1, square + 1)]
    db = [b[i] - b[i - 1] for i in range(1, square + 1)]
    da.insert(0, 0)
    db.insert(0, 0)
    result = DirichletQuotientSeries(n, mod=mod)
    c = result.data
    for x in range(2, square + 1):
        ax, bx = da[x], db[x]
        if not ax and not bx:
            continue
        stop = min(x - 1, n // (x * x))
        total = 0
        for y in range(2, stop + 1):
            value = x * y
            target = value if value <= square else size - n // value
            weight = ax * db[y] + bx * da[y]
            c[target] += weight
            total += weight
            if mod is not None:
                c[target] %= mod
                total %= mod
        c[size - x + 1] -= total
        value = x * x
        target = value if value <= square else size - n // value
        c[target] += ax * bx
        if mod is not None:
            c[target] %= mod
    running = 0
    for i in range(1, size):
        running += c[i]
        c[i] = running + a[1] * b[i] + b[1] * a[i] - a[1] * b[1]
        if mod is not None:
            running %= mod
            c[i] %= mod
    for z in range(1, n // (square + 1) + 1):
        value = n // z
        stop = min((isqrt(4 * value + 1) - 1) // 2, value // (z + 1))
        total = c[size - z]
        for x in range(2, stop + 1):
            upper = value // x
            upper = upper if upper <= square else size - n // upper
            lower = max(x, z)
            total += da[x] * (b[upper] - b[lower]) + db[x] * (a[upper] - a[lower])
            if mod is not None:
                total %= mod
        c[size - z] = total
    return result


def dirichlet_divide(convolution, divisor):
    if convolution.n != divisor.n or convolution.mod != divisor.mod:
        raise ValueError("series parameters differ")
    mod = divisor.mod
    if mod is None:
        inverse = 1 / divisor[1]
    else:
        inverse = pow(divisor[1], -1, mod)
    n = divisor.n
    square = divisor.square
    size = divisor.size
    a = [value * inverse for value in divisor.data]
    h = convolution.data
    if mod is not None:
        a = [value % mod for value in a]
        h = [value % mod for value in h]
    da = [0] + [a[i] - a[i - 1] for i in range(1, square + 1)]
    db = [0] * (square + 1)
    delta = [0] * size
    result = DirichletQuotientSeries(n, mod=mod)
    b = result.data
    running = 0
    for i in range(1, size):
        running += delta[i]
        if mod is not None:
            running %= mod
        total = h[i] - h[1] * a[i] + h[1] - running
        if mod is not None:
            total %= mod
        if i > square:
            z = size - i
            value = n // z
            stop = min((isqrt(4 * value + 1) - 1) // 2, value // (z + 1))
            for x in range(2, stop + 1):
                upper = value // x
                upper = upper if upper <= square else size - n // upper
                lower = max(x, z)
                total -= da[x] * (b[upper] - b[lower]) + db[x] * (a[upper] - a[lower])
                if mod is not None:
                    total %= mod
        b[i] = total
        if i <= square:
            db[i] = b[i] - b[i - 1]
        if i < 2 or i > square:
            continue
        ax, bx = da[i], db[i]
        if not ax and not bx:
            continue
        stop = min(i - 1, n // (i * i))
        weight_sum = 0
        for y in range(2, stop + 1):
            value = i * y
            target = value if value <= square else size - n // value
            weight = ax * db[y] + bx * da[y]
            delta[target] += weight
            weight_sum += weight
            if mod is not None:
                delta[target] %= mod
                weight_sum %= mod
        delta[size - i + 1] -= weight_sum
        value = i * i
        target = value if value <= square else size - n // value
        delta[target] += ax * bx
        if mod is not None:
            delta[target] %= mod
    result.data = [value * inverse for value in b]
    if mod is not None:
        result.data = [value % mod for value in result.data]
    return result


def enumerate_multiplicative_function(limit, prime_power):
    """Enumerate f(0..limit), given f(p**e) as prime_power(value,p,e)."""
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    if limit == 0:
        return [0]
    sieve = LinearSieve(limit)
    result = [0] * (limit + 1)
    result[1] = 1
    for value in range(2, limit + 1):
        prime = sieve.least_prime[value]
        remaining = value
        power = 1
        exponent = 0
        while remaining % prime == 0:
            remaining //= prime
            power *= prime
            exponent += 1
        result[value] = result[remaining] * prime_power(power, prime, exponent)
    return result


def mobius_values(limit):
    return LinearSieve(limit).mobius


def divisor_count_values(limit):
    return enumerate_multiplicative_function(
        limit, lambda power, prime, exponent: exponent + 1
    )


def divisor_sum_values(limit):
    return enumerate_multiplicative_function(
        limit,
        lambda power, prime, exponent: (power * prime - 1) // (prime - 1),
    )


def totient_values(limit):
    return LinearSieve(limit).phi


class EnumerateMultiplicativePrefixSum:
    """Recover S_f(N/i) from prefix sums of g and h=f*g."""

    __slots__ = ("N", "square", "small", "large")

    def __init__(self, n, prefix_g, prefix_h):
        self.N = n
        self.square = isqrt(n)
        self.small = [0] * (self.square + 1)
        self.large = [0] * (self.square + 1)
        quotients = set()
        left = 1
        while left <= n:
            quotient = n // left
            quotients.add(quotient)
            left = n // quotient + 1
        for value in sorted(quotients):
            current = prefix_h(value)
            left = 1
            while left <= value:
                quotient = value // left
                right = value // quotient + 1
                if quotient != value:
                    current -= self.get(quotient) * (
                        prefix_g(right) - prefix_g(left)
                    )
                left = right
            self._set(value, current)

    def _set(self, value, result):
        if value <= self.square:
            self.small[value] = result
        else:
            self.large[self.N // value] = result

    def get(self, value):
        if value <= self.square:
            return self.small[value]
        return self.large[self.N // value]

    __call__ = get


class MultiplicativePrefixSum:
    """Min_25 style summatory engine for a multiplicative function."""

    __slots__ = ("limit", "square", "split", "size", "primes", "mod")

    def __init__(self, limit, mod=None):
        if limit < 0:
            raise ValueError("limit must be nonnegative")
        self.limit = limit
        self.mod = mod
        self.square = isqrt(limit)
        if limit == 0:
            self.split = self.size = 0
            self.primes = []
            return
        split = limit // max(1, self.square)
        while split != 1 and limit // (split - 1) == self.square:
            split -= 1
        self.split = split
        self.size = split + self.square
        self.primes = prime_sieve(self.square)

    def index(self, value):
        return self.size - value if value <= self.square else self.limit // value

    idx = index

    def _normalize(self, value):
        return value if self.mod is None else value % self.mod

    def prime_count_table(self):
        if self.limit == 0:
            return []
        high = [0] * self.split
        for index in range(1, self.split):
            high[index] = self.limit // index - 1
        small = [index - 1 for index in range(self.square + 1)]
        counted = 0
        for prime in self.primes:
            square = prime * prime
            maximum = min(self.split, self.limit // square + 1)
            multiple = prime
            for index in range(1, maximum):
                source = (high[multiple] if multiple < self.split
                          else small[self.limit // multiple])
                high[index] -= source - counted
                multiple += prime
            for value in range(self.square, square - 1, -1):
                small[value] -= small[value // prime] - counted
            counted += 1
        return high + [small[value] for value in range(self.square, 0, -1)]

    pi_table = prime_count_table

    def prime_sum_table(self):
        if self.limit == 0:
            return []
        table = [0] * self.size
        for index in range(1, self.split):
            value = self.limit // index
            table[index] = value * (value + 1) // 2 - 1
        for value in range(1, self.square + 1):
            table[self.size - value] = value * (value + 1) // 2 - 1
        for prime in self.primes:
            previous = table[self.size - prime + 1]
            square = prime * prime
            maximum = min(self.split, self.limit // square + 1)
            multiple = prime
            for index in range(1, maximum):
                source = (table[multiple] if multiple < self.split
                          else table[self.size - self.limit // multiple])
                table[index] -= (source - previous) * prime
                multiple += prime
            for value in range(self.square, square - 1, -1):
                table[self.size - value] -= (
                    table[self.size - value // prime] - previous
                ) * prime
        if self.mod is not None:
            table = [value % self.mod for value in table]
        return table

    def run(self, prime_prefix, prime_power):
        if self.limit == 0:
            return 0
        if len(prime_prefix) != self.size:
            raise ValueError("prime prefix table has the wrong size")
        limit, square, size, mod = self.limit, self.square, self.size, self.mod
        primes = self.primes
        count = len(primes)
        first = [prime_power(p, 1) for p in primes]
        second = [prime_power(p, 2) for p in primes]
        base = [prime_prefix[size - p] for p in primes]
        answer = prime_prefix[self.index(limit)] + 1
        stack = [(i, 1, limit // primes[i], 1) for i in range(count)]
        while stack:
            index, exponent, remaining, coefficient = stack.pop()
            prime = primes[index]
            if exponent == 1:
                value, next_value = first[index], second[index]
            else:
                value = prime_power(prime, exponent)
                next_value = prime_power(prime, exponent + 1)
            answer += coefficient * next_value
            if remaining >= prime * prime:
                stack.append((index, exponent + 1,
                              remaining // prime, coefficient))
            coefficient *= value
            if mod is not None:
                coefficient %= mod
            position = size - remaining if remaining <= square else limit // remaining
            answer += coefficient * (
                prime_prefix[position] - base[index]
            )
            for next_index in range(index + 1, count):
                next_prime = primes[next_index]
                next_square = next_prime * next_prime
                if next_square > remaining:
                    break
                quotient = remaining // next_prime
                if next_square <= quotient:
                    stack.append((next_index, 1,
                                  quotient, coefficient))
                else:
                    position = size - quotient if quotient <= square else limit // quotient
                    value = second[next_index] + first[next_index] * (
                        prime_prefix[position] - base[next_index]
                    )
                    if mod is not None:
                        value %= mod
                    answer += coefficient * value
            if mod is not None:
                answer %= mod
        return self._normalize(answer)

    def min_25_sieve(self, prime_prefix, prime_power):
        if self.limit == 0:
            return []
        values = [0]
        for index in range(1, self.split):
            values.append(self.limit // index)
        values.extend(range(self.square, 0, -1))
        current = list(prime_prefix)
        updated = list(prime_prefix)
        for prime in reversed(self.primes):
            power = prime
            exponent = 1
            while self.limit // prime >= power:
                value = prime_power(prime, exponent)
                next_value = prime_power(prime, exponent + 1)
                base = prime_prefix[self.index(prime)]
                for index in range(1, self.size):
                    n = values[index]
                    if prime * power > n:
                        break
                    updated[index] += value * (
                        current[self.index(n // power)] - base
                    ) + next_value
                exponent += 1
                power *= prime
            boundary = min(self.size, self.index(prime * prime) + 1)
            current[:boundary] = updated[:boundary]
        for index in range(1, len(current)):
            current[index] += 1
        if self.mod is not None:
            current = [value % self.mod for value in current]
        return current


def sum_totient_fast(limit, mod=None):
    return _sum_totient(limit, mod)


Dir = DirichletQuotientSeries
mult = dirichlet_multiply
div = dirichlet_divide
enamurate_multiplicative_function = enumerate_multiplicative_function
enumerate_mf_prefix_sum = EnumerateMultiplicativePrefixSum
mf_prefix_sum = MultiplicativePrefixSum
mobius_function = mobius_values
sigma0 = divisor_count_values
sigma1 = divisor_sum_values
totient = totient_values
sum_of_totient = sum_totient_fast
MultiplicativeSum = MultiplicativePrefixSum
