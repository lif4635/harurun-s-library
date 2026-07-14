"""Core modular combinatorics and integer floor arithmetic."""


DEFAULT_MOD = 998244353


def gcd(first, second):
    first = abs(first)
    second = abs(second)
    while second:
        first, second = second, first % second
    return first


def lcm(first, second):
    return 0 if not first or not second else abs(first // gcd(first, second) * second)


def extended_gcd(first, second):
    """Return (g,x,y) with first*x + second*y = g = gcd(first,second)."""
    old_r, r = first, second
    old_x, x = 1, 0
    old_y, y = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y
    if old_r < 0:
        old_r, old_x, old_y = -old_r, -old_x, -old_y
    return old_r, old_x, old_y


def inverse_mod(value, modulus):
    gcd, inverse, _ = extended_gcd(value, modulus)
    if gcd != 1:
        raise ValueError("inverse does not exist")
    return inverse % modulus


def inverse_table(size, mod=DEFAULT_MOD):
    if size >= mod:
        raise ValueError("table entries must be invertible")
    inverse = [0] * (size + 1)
    if size:
        inverse[1] = 1
    for value in range(2, size + 1):
        inverse[value] = mod - mod // value * inverse[mod % value] % mod
    return inverse


class Combination:
    """Dynamically extended factorial table over a prime modulus."""

    __slots__ = ("mod", "factorial", "inverse_factorial")

    def __init__(self, size=0, mod=DEFAULT_MOD):
        self.mod = mod
        self.factorial = [1]
        self.inverse_factorial = [1]
        self.ensure(size)

    def ensure(self, size):
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

    def factorial_value(self, n):
        self.ensure(n)
        return self.factorial[n]

    def binomial(self, n, k):
        if k < 0 or n < k or n < 0:
            return 0
        self.ensure(n)
        return (self.factorial[n] * self.inverse_factorial[k]
                % self.mod * self.inverse_factorial[n - k] % self.mod)

    C = binomial
    nCr = binomial

    def permutation(self, n, k):
        if k < 0 or n < k or n < 0:
            return 0
        self.ensure(n)
        return self.factorial[n] * self.inverse_factorial[n - k] % self.mod

    P = permutation
    nPr = permutation

    def multiset(self, n, k):
        if n == 0:
            return int(k == 0)
        return self.binomial(n + k - 1, k)


def binomial_multiplicative(n, k, mod=DEFAULT_MOD):
    """O(k) binomial for huge n and small k over a prime modulus."""
    if k < 0 or n < k:
        return 0
    k = min(k, n - k)
    numerator = denominator = 1
    for i in range(1, k + 1):
        numerator = numerator * (n - k + i) % mod
        denominator = denominator * i % mod
    return numerator * pow(denominator, -1, mod) % mod


def floor_sum(n, modulus, multiplier, addend):
    """Sum floor((multiplier*i+addend)/modulus), 0 <= i < n.

    Unlike ACL's narrow interface, multiplier and addend may be negative.
    """
    if n < 0 or modulus <= 0:
        raise ValueError("requires n >= 0 and modulus > 0")
    quotient_a, multiplier = divmod(multiplier, modulus)
    quotient_b, addend = divmod(addend, modulus)
    answer = quotient_a * n * (n - 1) // 2 + quotient_b * n
    while True:
        if multiplier >= modulus:
            quotient, multiplier = divmod(multiplier, modulus)
            answer += quotient * n * (n - 1) // 2
        if addend >= modulus:
            quotient, addend = divmod(addend, modulus)
            answer += quotient * n
        maximum = multiplier * n + addend
        if maximum < modulus:
            return answer
        n, addend = divmod(maximum, modulus)
        multiplier, modulus = modulus, multiplier


def mod_affine_range_count(multiplier, addend, modulus, x_limit, y_limit):
    """Count x in [0,x_limit) with (multiplier*x+addend)%modulus<y_limit."""
    if not 0 <= y_limit <= modulus:
        raise ValueError("y_limit out of range")
    return (floor_sum(x_limit, modulus, multiplier, addend + modulus)
            - floor_sum(x_limit, modulus, multiplier,
                        addend + modulus - y_limit))


def enumerate_quotient(number):
    """Yield ``(number//x, left, right)`` for maximal x ranges [left,right)."""
    if number < 0:
        raise ValueError("number must be nonnegative")
    left = 1
    while left <= number:
        quotient = number // left
        right = number // quotient + 1
        yield quotient, left, right
        left = right


def gray_code(value):
    return value ^ (value >> 1)


def inverse_gray_code(value):
    result = 0
    while value:
        result ^= value
        value >>= 1
    return result
