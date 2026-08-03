from math import isqrt

from library_codex.prime.Sieve import LinearSieve, prime_sieve


def _floor_two_thirds(number):
    value = max(1, int(number ** (2.0 / 3.0)))
    square = number * number
    while (value + 1) ** 3 <= square:
        value += 1
    while value ** 3 > square:
        value -= 1
    return max(1, value)


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
    result = DirichletQuotientSeries(n, mod=first.mod)
    threshold = first.index(_floor_two_thirds(n))
    square = first.square

    def collect(source, other):
        entries = []
        for index in range(1, square + 1):
            difference = source[index] - source[index - 1]
            if difference:
                entries.append((index, difference))
                for target in range(result.size - 1, threshold, -1):
                    value = result.value(target)
                    destination = other.index(value // index)
                    if destination < index:
                        break
                    result.data[target] += difference * other[destination]
        for index in range(square + 1, threshold + 1):
            difference = source[index] - source[index - 1]
            if difference:
                entries.append((source.value(index), difference))
        return entries

    left_entries = collect(first, second)
    right_entries = collect(second, first)
    for left_value, left_weight in left_entries:
        for right_value, right_weight in right_entries:
            destination = result.index(left_value * right_value)
            if destination > threshold:
                break
            result.data[destination] += left_weight * right_weight
    for index in range(1, threshold + 1):
        result.data[index] += result.data[index - 1]
    for index in range(result.size - 1, threshold, -1):
        root = isqrt(result.value(index))
        result.data[index] -= first[root] * second[root]
    if result.mod is not None:
        result.data = [value % result.mod for value in result.data]
    return result


def dirichlet_divide(convolution, divisor):
    if convolution.n != divisor.n or convolution.mod != divisor.mod:
        raise ValueError("series parameters differ")
    mod = divisor.mod
    if mod is None:
        inverse = 1 / divisor[1]
    else:
        inverse = pow(divisor[1], -1, mod)
    normalized = DirichletQuotientSeries(
        divisor.n, [value * inverse for value in divisor.data], mod
    )
    n = divisor.n
    square = divisor.square
    threshold = divisor.index(_floor_two_thirds(n))
    dc = DirichletQuotientSeries(n, convolution.data, mod).difference()
    da = DirichletQuotientSeries(n, normalized.data, mod).difference()
    db = DirichletQuotientSeries(n, mod=mod)
    result = DirichletQuotientSeries(n, mod=mod)
    db[1] = convolution[1]
    for index in range(2, threshold + 1):
        db[index] = dc[index] - da[index] * db[1]
        value = normalized.value(index)
        destination = normalized.index(value * value)
        if destination <= threshold:
            dc[destination] = dc[destination] - da[index] * db[index]
        for other in range(2, index):
            destination = normalized.index(value * normalized.value(other))
            if destination > threshold:
                break
            dc[destination] = (
                dc[destination] - da[index] * db[other]
                - da[other] * db[index]
            )
    for index in range(1, threshold + 1):
        result[index] = db[index] + result[index - 1]
    for index in range(threshold + 1, normalized.size):
        result[index] = convolution[index] - normalized[index] * result[1]
        value = normalized.value(index)
        root_index = normalized.index(isqrt(value))
        result[index] = result[index] + normalized[root_index] * result[root_index]
        for other in range(2, index + 1):
            destination = normalized.index(value // other)
            if other > destination:
                break
            result[index] = (
                result[index] - da[other] * result[destination]
                - normalized[destination] * db[other]
            )
    result.data = [value * inverse for value in result.data]
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
        answer = prime_prefix[self.index(self.limit)] + 1
        stack = []
        for index in range(len(self.primes) - 1, -1, -1):
            stack.append((index, 1, self.primes[index], 1))
        while stack:
            index, exponent, product, coefficient = stack.pop()
            prime = self.primes[index]
            answer += coefficient * prime_power(prime, exponent + 1)
            remaining = self.limit // product
            if remaining >= prime * prime:
                stack.append((index, exponent + 1,
                              product * prime, coefficient))
            coefficient *= prime_power(prime, exponent)
            answer += coefficient * (
                prime_prefix[self.index(remaining)]
                - prime_prefix[self.index(prime)]
            )
            for next_index in range(len(self.primes) - 1, index, -1):
                next_prime = self.primes[next_index]
                if next_prime * next_prime <= remaining:
                    stack.append((next_index, 1,
                                  product * next_prime, coefficient))
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
    if limit < 1:
        return 0
    quotients = set()
    left = 1
    while left <= limit:
        quotient = limit // left
        quotients.add(quotient)
        left = limit // quotient + 1
    prefix = {}
    for value in sorted(quotients):
        result = value * (value + 1) // 2
        lower = 2
        while lower <= value:
            quotient = value // lower
            upper = value // quotient + 1
            result -= (upper - lower) * prefix[quotient]
            lower = upper
        prefix[value] = result if mod is None else result % mod
    return prefix[limit]


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
