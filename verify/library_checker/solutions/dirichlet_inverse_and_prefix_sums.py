"""素数列挙、最小素因数・Möbius・φの表、素数と平方因子を持たない数の個数。"""
from math import isqrt

class LinearSieve:
    __slots__ = ('limit', 'primes', 'least_prime', 'mobius', 'phi')

    def __init__(self, limit):
        if limit < 0:
            raise ValueError('limit must be nonnegative')
        least = [0] * (limit + 1)
        mobius = [0] * (limit + 1)
        phi = [0] * (limit + 1)
        if limit >= 1:
            mobius[1] = phi[1] = 1
        primes = []
        for value in range(2, limit + 1):
            if least[value] == 0:
                least[value] = value
                primes.append(value)
                mobius[value] = -1
                phi[value] = value - 1
            for prime in primes:
                product = value * prime
                if product > limit:
                    break
                least[product] = prime
                if value % prime == 0:
                    mobius[product] = 0
                    phi[product] = phi[value] * prime
                    break
                mobius[product] = -mobius[value]
                phi[product] = phi[value] * (prime - 1)
        self.limit = limit
        self.primes = primes
        self.least_prime = least
        self.mobius = mobius
        self.phi = phi

    def is_prime(self, value):
        return 2 <= value <= self.limit and self.least_prime[value] == value

    def factor_count(self, value):
        if not 1 <= value <= self.limit:
            raise ValueError('value outside sieve')
        result = []
        while value > 1:
            prime = self.least_prime[value]
            exponent = 0
            while value % prime == 0:
                value //= prime
                exponent += 1
            result.append((prime, exponent))
        return result

def prime_sieve(limit):
    """limit以下の素数を昇順listで返す。時間 O(N log log N)。"""
    return enumerate_primes(limit)[1]

def enumerate_primes(limit, step=1, offset=0):
    """素数の総数と、素数列のoffset番目からstep個おきの値を返す。"""
    if limit < 0 or step <= 0 or (not 0 <= offset < step):
        raise ValueError('require limit >= 0 and 0 <= offset < step')
    if limit < 2:
        return (0, [])
    root = isqrt(limit)
    small = bytearray(b'\x01') * ((root + 1) // 2)
    if small:
        small[0] = 0
    for i in range(1, (isqrt(root) + 1) // 2):
        if small[i]:
            prime = 2 * i + 1
            start = prime * prime // 2
            small[start::prime] = b'\x00' * ((len(small) - 1 - start) // prime + 1)
    primes = [2 * i + 1 for i in range(1, len(small)) if small[i]]
    block = max(1 << 18, root)
    total = 1
    result = [2] if offset == 0 else []
    wanted = offset + step if offset == 0 else offset
    for low in range(3, limit + 1, 2 * block):
        size = min(block, (limit - low) // 2 + 1)
        flags = bytearray(b'\x01') * size
        high = low + 2 * size
        for prime in primes:
            square = prime * prime
            if square >= high:
                break
            first = max(square, (low + prime - 1) // prime * prime)
            if first & 1 == 0:
                first += prime
            start = (first - low) // 2
            flags[start::prime] = b'\x00' * ((size - 1 - start) // prime + 1)
        count = flags.count(1)
        if wanted < total + count:
            rank = total
            for i in range(size):
                if flags[i]:
                    if rank == wanted:
                        result.append(low + 2 * i)
                        wanted += step
                    rank += 1
        total += count
    return (total, result)

def prime_count(number):
    """number以下の素数の個数を返す。時間 O(N^(3/4)/log N)、メモリ O(√N)。"""
    if number < 2:
        return 0
    root = isqrt(number)
    size = (root + 1) // 2
    small = list(range(size))
    large = [(number // (2 * i + 1) - 1) // 2 for i in range(size)]
    for position in range(1, size):
        previous = small[position - 1]
        if small[position] == previous:
            continue
        prime = 2 * position + 1
        square = prime * prime
        stop = min(size, (number // square + 1) // 2)
        split = min(stop, ((2 * size - 1) // prime + 1) // 2)
        source = position
        for i in range(split):
            large[i] -= large[source] - previous
            source += prime
        divisor = prime * (2 * split + 1)
        for i in range(split, stop):
            large[i] -= small[(number // divisor - 1) // 2] - previous
            divisor += 2 * prime
        for i in range(size - 1, square // 2 - 1, -1):
            small[i] -= small[((2 * i + 1) // prime - 1) // 2] - previous
    return large[0] + 1

def count_square_free(number):
    """1以上number以下で、1以外の平方数を因子に持たない整数を数える。"""
    if number <= 0:
        return 0
    count = max(1, int(number ** 0.2))
    while (count + 1) ** 5 <= number:
        count += 1
    while count ** 5 > number:
        count -= 1
    limit = isqrt(number // count)
    prefix = [1] * (limit + 1)
    composite = bytearray(limit + 1)
    for prime in range(2, limit + 1):
        if not composite[prime]:
            prefix[prime] = -1
            for multiple in range(2 * prime, limit + 1, prime):
                composite[multiple] = 1
                prefix[multiple] = -prefix[multiple]
            square = prime * prime
            for multiple in range(square, limit + 1, square):
                prefix[multiple] = 0
    del composite
    prefix[0] = 0
    total = 0
    running = 0
    for value in range(1, limit + 1):
        mu = prefix[value]
        if mu:
            total += mu * (number // (value * value))
        running += mu
        prefix[value] = running
    large = [0] * count
    total -= (count - 1) * running
    for index in range(count - 1, 0, -1):
        value = isqrt(number // index)
        root = isqrt(value)
        boundary = min(root, value // (limit + 1))
        mertens = 1
        for divisor in range(2, boundary + 1):
            mertens -= large[index * divisor * divisor]
        for divisor in range(max(2, boundary + 1), root + 1):
            mertens -= prefix[value // divisor]
        previous = value
        for quotient in range(1, value // (root + 1) + 1):
            end = value // (quotient + 1)
            mertens -= (previous - end) * prefix[quotient]
            previous = end
        large[index] = mertens
        total += mertens
    return total

def sum_totient(limit, mod=None):
    """1からlimitまでのφの総和を返す。modを指定するとその余りを返す。"""
    if mod is not None and mod <= 0:
        raise ValueError('mod must be positive')
    if limit < 1:
        return 0
    if mod == 1:
        return 0
    cutoff = min(limit, max(64, int(limit ** (2.0 / 3.0))))
    prefix = list(range(cutoff + 1))
    for prime in range(2, cutoff + 1):
        if prefix[prime] == prime:
            for multiple in range(prime, cutoff + 1, prime):
                prefix[multiple] -= prefix[multiple] // prime
    total = 0
    if mod is None:
        for value in range(1, cutoff + 1):
            total += prefix[value]
            prefix[value] = total
    else:
        for value in range(1, cutoff + 1):
            total = (total + prefix[value]) % mod
            prefix[value] = total
    size = limit // (cutoff + 1)
    large = [0] * (size + 1)
    for index in range(size, 0, -1):
        value = limit // index
        root = isqrt(value)
        result = value * (value + 1) // 2
        boundary = min(root, value // (cutoff + 1))
        for divisor in range(2, boundary + 1):
            result -= large[index * divisor]
        for divisor in range(max(2, boundary + 1), root + 1):
            result -= prefix[value // divisor]
        previous = root
        for quotient in range(value // (root + 1), 0, -1):
            end = value // quotient
            result -= (end - previous) * prefix[quotient]
            previous = end
        large[index] = result if mod is None else result % mod
    return large[1] if size else prefix[limit]
from math import isqrt as _number_theory_multiplicative_functions_isqrt

def _number_theory_multiplicative_functions_small_quotient(value, divisor):
    if value <= 1125899906842624:
        return int(value / divisor)
    return value // divisor

class DirichletQuotientSeries:
    """Prefix sums stored at all distinct values floor(N/i)."""
    __slots__ = ('n', 'square', 'size', 'data', 'mod')

    def __init__(self, n, values=None, mod=None):
        if n < 1:
            raise ValueError('n must be positive')
        self.n = n
        self.square = _number_theory_multiplicative_functions_isqrt(n)
        self.size = self.square + n // (self.square + 1) + 1
        self.data = [0] * self.size if values is None else list(values)
        if len(self.data) != self.size:
            raise ValueError('invalid quotient-series storage length')
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
        raise ValueError('series parameters differ')
    n = first.n
    square = first.square
    size = first.size
    mod = first.mod
    (a, b) = (first.data, second.data)
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
        (ax, bx) = (da[x], db[x])
        if not ax and (not bx):
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
        stop = min((_number_theory_multiplicative_functions_isqrt(4 * value + 1) - 1) // 2, value // (z + 1))
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
        raise ValueError('series parameters differ')
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
            stop = min((_number_theory_multiplicative_functions_isqrt(4 * value + 1) - 1) // 2, value // (z + 1))
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
        (ax, bx) = (da[i], db[i])
        if not ax and (not bx):
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
        raise ValueError('limit must be nonnegative')
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
    return enumerate_multiplicative_function(limit, lambda power, prime, exponent: exponent + 1)

def divisor_sum_values(limit):
    return enumerate_multiplicative_function(limit, lambda power, prime, exponent: (power * prime - 1) // (prime - 1))

def totient_values(limit):
    return LinearSieve(limit).phi

class EnumerateMultiplicativePrefixSum:
    """Recover S_f(N/i) from prefix sums of g and h=f*g."""
    __slots__ = ('N', 'square', 'small', 'large')

    def __init__(self, n, prefix_g, prefix_h):
        self.N = n
        self.square = _number_theory_multiplicative_functions_isqrt(n)
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
                    current -= self.get(quotient) * (prefix_g(right) - prefix_g(left))
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
    __slots__ = ('limit', 'square', 'split', 'size', 'primes', 'mod')

    def __init__(self, limit, mod=None):
        if limit < 0:
            raise ValueError('limit must be nonnegative')
        self.limit = limit
        self.mod = mod
        self.square = _number_theory_multiplicative_functions_isqrt(limit)
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
            high[index] = (self.limit // index - 1) // 2
        small = list(range((self.square + 1) // 2))
        counted = 0
        for prime in self.primes[1:]:
            square = prime * prime
            maximum = min(self.split, self.limit // square + 1)
            boundary = min(maximum, (self.split - 1) // prime + 1)
            multiple = prime
            for index in range(1, boundary):
                high[index] -= high[multiple] - counted
                multiple += prime
            for index in range(boundary, maximum):
                high[index] -= small[(_number_theory_multiplicative_functions_small_quotient(self.limit, multiple) - 1) // 2] - counted
                multiple += prime
            half = prime // 2
            for value in range(len(small) - 1, square // 2 - 1, -1):
                small[value] -= small[_number_theory_multiplicative_functions_small_quotient(value - half, prime)] - counted
            counted += 1
        for index in range(1, self.split):
            high[index] += 1
        return high + [small[(value - 1) // 2] + (value >= 2) for value in range(self.square, 0, -1)]
    pi_table = prime_count_table

    def prime_sum_table(self, linear=1, constant=0):
        if self.limit == 0:
            return []
        if self.mod == 1 or linear == constant == 0:
            return [0] * self.size
        if linear == 0:
            table = [constant * x for x in self.prime_count_table()]
            return table if self.mod is None else [x % self.mod for x in table]
        if self.mod is not None:
            linear %= self.mod
            constant %= self.mod
            if constant:
                return self._prime_affine_table_mod(linear, constant)
            table = self._prime_sum_table_mod()
            return table if linear == 1 else [linear * x % self.mod for x in table]
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
                source = table[multiple] if multiple < self.split else table[self.size - self.limit // multiple]
                table[index] -= (source - previous) * prime
                multiple += prime
            for value in range(self.square, square - 1, -1):
                table[self.size - value] -= (table[self.size - value // prime] - previous) * prime
        if constant:
            counts = self.prime_count_table()
            return [linear * x + constant * y for (x, y) in zip(table, counts)]
        if linear != 1:
            table = [linear * x for x in table]
        return table

    def _prime_sum_table_mod(self):
        (limit, split, root, mod) = (self.limit, self.split, self.square, self.mod)
        high = [0] * split
        for i in range(1, split):
            x = (limit // i + 1) // 2
            high[i] = (x * x - 1) % mod
        small = [((i + 1) ** 2 - 1) % mod for i in range((root + 1) // 2)]
        for p in self.primes[1:]:
            previous = small[(p - 3) // 2]
            stop = min(split, limit // (p * p) + 1)
            boundary = min(stop, (split - 1) // p + 1)
            source = p
            for i in range(1, boundary):
                high[i] = (high[i] - p * (high[source] - previous)) % mod
                source += p
            for i in range(boundary, stop):
                high[i] = (high[i] - p * (small[(_number_theory_multiplicative_functions_small_quotient(limit, source) - 1) // 2] - previous)) % mod
                source += p
            half = p // 2
            for x in range(len(small) - 1, p * p // 2 - 1, -1):
                small[x] = (small[x] - p * (small[_number_theory_multiplicative_functions_small_quotient(x - half, p)] - previous)) % mod
        for i in range(1, split):
            high[i] = (high[i] + 2) % mod
        return high + [(small[(x - 1) // 2] + 2 * (x >= 2)) % mod for x in range(root, 0, -1)]

    def _prime_affine_table_mod(self, linear, constant):
        (limit, split, root, mod) = (self.limit, self.split, self.square, self.mod)
        count = [0] * split
        high = [0] * split
        for i in range(1, split):
            x = (limit // i + 1) // 2
            count[i] = x - 1
            high[i] = (x * x - 1) % mod
        small_count = list(range((root + 1) // 2))
        small = [((i + 1) ** 2 - 1) % mod for i in range(len(small_count))]
        for (pi, p) in enumerate(self.primes[1:]):
            previous = small[(p - 3) // 2]
            stop = min(split, limit // (p * p) + 1)
            boundary = min(stop, (split - 1) // p + 1)
            source = p
            for i in range(1, boundary):
                high[i] = (high[i] - p * (high[source] - previous)) % mod
                count[i] -= count[source] - pi
                source += p
            reduced = limit // p
            middle = max(boundary, min(stop, 4 * _number_theory_multiplicative_functions_isqrt(reduced) + 1))
            for i in range(boundary, middle):
                j = (_number_theory_multiplicative_functions_small_quotient(reduced, i) - 1) // 2
                high[i] = (high[i] - p * (small[j] - previous)) % mod
                count[i] -= small_count[j] - pi
            i = middle
            while i < stop:
                q = _number_theory_multiplicative_functions_small_quotient(reduced, i)
                j = (q - 1) // 2
                end = min(stop, _number_theory_multiplicative_functions_small_quotient(reduced, 2 * j + 1) + 1)
                dc = small_count[j] - pi
                ds = p * (small[j] - previous) % mod
                while i < end:
                    value = high[i] - ds
                    high[i] = value + (value < 0) * mod
                    count[i] -= dc
                    i += 1
            half = p // 2
            end = p * p // 2
            x = len(small) - 1
            while x >= end:
                j = _number_theory_multiplicative_functions_small_quotient(x - half, p)
                left = max(end, j * p + half)
                dc = small_count[j] - pi
                ds = p * (small[j] - previous) % mod
                while x >= left:
                    value = small[x] - ds
                    small[x] = value + (value < 0) * mod
                    small_count[x] -= dc
                    x -= 1
        for i in range(1, split):
            high[i] = (constant * (count[i] + 1) + linear * (high[i] + 2)) % mod
        return high + [(constant * (small_count[(x - 1) // 2] + (x >= 2)) + linear * (small[(x - 1) // 2] + 2 * (x >= 2))) % mod for x in range(root, 0, -1)]

    def run(self, prime_prefix, prime_power):
        if self.limit == 0:
            return 0
        if len(prime_prefix) != self.size:
            raise ValueError('prime prefix table has the wrong size')
        (limit, square, size, mod) = (self.limit, self.square, self.size, self.mod)
        primes = self.primes
        count = len(primes)
        pi = [0] * (square + 1)
        start = 2
        for (rank, prime) in enumerate(primes):
            for x in range(start, prime):
                pi[x] = rank
            start = prime
        for x in range(start, square + 1):
            pi[x] = count
        first = [prime_power(p, 1) for p in primes]
        second = [prime_power(p, 2) for p in primes]
        base = [prime_prefix[size - p] for p in primes]
        answer = prime_prefix[self.index(limit)] + 1
        stack = [(i, 1, limit // primes[i], 1) for i in range(count)]
        while stack:
            (index, exponent, remaining, coefficient) = stack.pop()
            prime = primes[index]
            if exponent == 1:
                (value, next_value) = (first[index], second[index])
            else:
                value = prime_power(prime, exponent)
                next_value = prime_power(prime, exponent + 1)
            answer += coefficient * next_value
            if remaining >= prime * prime:
                stack.append((index, exponent + 1, remaining // prime, coefficient))
            coefficient *= value
            if mod is not None:
                coefficient %= mod
            position = size - remaining if remaining <= square else limit // remaining
            answer += coefficient * (prime_prefix[position] - base[index])
            subtotal = 0
            stop = pi[_number_theory_multiplicative_functions_isqrt(remaining)]
            next_index = index + 1
            while next_index < stop:
                next_prime = primes[next_index]
                if next_prime * next_prime * next_prime > remaining:
                    break
                stack.append((next_index, 1, remaining // next_prime, coefficient))
                next_index += 1
            boundary = max(next_index, min(stop, pi[remaining // (square + 1)]))
            for j in range(next_index, boundary):
                subtotal += second[j] + first[j] * (prime_prefix[position * primes[j]] - base[j])
                if mod is not None and (subtotal > 4611686018427387904 or subtotal < -4611686018427387904):
                    subtotal %= mod
            for j in range(boundary, stop):
                subtotal += second[j] + first[j] * (prime_prefix[size - _number_theory_multiplicative_functions_small_quotient(remaining, primes[j])] - base[j])
                if mod is not None and (subtotal > 4611686018427387904 or subtotal < -4611686018427387904):
                    subtotal %= mod
            answer += coefficient * subtotal
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
                    updated[index] += value * (current[self.index(n // power)] - base) + next_value
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
    return sum_totient(limit, mod)
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
import sys

def main():
    read = sys.stdin.buffer.readline
    write = sys.stdout.write
    for _ in range(int(read())):
        n = int(read())
        a = DirichletQuotientSeries(n, [0] + list(map(int, read().split())), 998244353)
        unit = DirichletQuotientSeries(n, [0] + [1] * (a.size - 1), 998244353)
        write(' '.join(map(str, dirichlet_divide(unit, a).data[1:])) + '\n')
if __name__ == '__main__':
    main()
