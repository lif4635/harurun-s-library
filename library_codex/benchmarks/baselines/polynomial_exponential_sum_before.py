import sys
DEFAULT_MOD = 998244353

def power_table(limit, exponent, mod=None):
    if limit < 0 or exponent < 0:
        raise ValueError('limit and exponent must be nonnegative')
    if mod is None:
        return [value ** exponent for value in range(limit + 1)]
    return [pow(value, exponent, mod) for value in range(limit + 1)]

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

def interpolate_consecutive(values, point, mod=DEFAULT_MOD):
    size = len(values)
    if size == 0:
        raise ValueError('at least one value is required')
    if size > mod:
        raise ValueError('the number of points must not exceed mod')
    point %= mod
    if point < size:
        return values[point] % mod
    left = [1] * (size + 1)
    right = [1] * (size + 1)
    for index in range(size):
        left[index + 1] = left[index] * (point - index) % mod
    for index in range(size - 1, -1, -1):
        right[index] = right[index + 1] * (point - index) % mod
    factorial = 1
    for index in range(2, size):
        factorial = factorial * index % mod
    try:
        inverse_factorial = pow(factorial, -1, mod)
    except ValueError as error:
        raise ZeroDivisionError('interpolation requires a field') from error
    inverse_factorials = [1] * size
    if size > 1:
        inverse_factorials[-1] = inverse_factorial
        for index in range(size - 1, 0, -1):
            inverse_factorials[index - 1] = inverse_factorials[index] * index % mod
    result = 0
    last = size - 1
    for index, value in enumerate(values):
        term = value * left[index] * right[index + 1] * inverse_factorials[index] * inverse_factorials[last - index] % mod
        if last - index & 1:
            result -= term
        else:
            result += term
    return result % mod

def limit_sum_polynomial_exponential(values, ratio, mod=DEFAULT_MOD):
    """Sum ratio**k*f(k), k >= 0, from consecutive samples of f."""
    if not values:
        raise ValueError('at least one sample is required')
    ratio %= mod
    if ratio == 1:
        raise ValueError('the infinite formal sum requires ratio != 1')
    degree = len(values) - 1
    combination = Comb(degree + 1, mod)
    powers = [1] * (degree + 1)
    for index in range(degree):
        powers[index + 1] = powers[index] * ratio % mod
    accumulated = 0
    answer = 0
    for index in range(degree + 1):
        accumulated = (accumulated + powers[index] * values[index]) % mod
        term = combination.C(degree + 1, index + 1) * powers[degree - index] % mod * accumulated % mod
        answer += -term if degree - index & 1 else term
    return answer % mod * pow(pow(1 - ratio, degree + 1, mod), -1, mod) % mod

def sum_polynomial_exponential(values, ratio, count, mod=DEFAULT_MOD):
    """Sum ratio**k*f(k), 0 <= k < count, from consecutive samples of f."""
    if not values:
        raise ValueError('at least one sample is required')
    if count <= 0:
        return 0
    ratio %= mod
    degree = len(values) - 1
    powers = [1] * (degree + 1)
    prefixes = [0] * (degree + 1)
    for index in range(degree + 1):
        if index:
            powers[index] = powers[index - 1] * ratio % mod
        prefixes[index] = powers[index] * values[index] % mod
        if index:
            prefixes[index] = (prefixes[index] + prefixes[index - 1]) % mod
    last = count - 1
    if ratio == 0:
        return values[0] % mod
    if ratio == 1:
        return interpolate_consecutive([0] + prefixes, count, mod)
    combination = Comb(degree + 1, mod)
    constant = 0
    for index in range(degree + 1):
        term = combination.C(degree + 1, index + 1) * powers[degree - index] % mod * prefixes[index] % mod
        constant += -term if degree - index & 1 else term
    constant %= mod
    constant = constant * pow(pow(1 - ratio, degree + 1, mod), -1, mod) % mod
    inverse_ratio = pow(ratio, -1, mod)
    inverse_power = 1
    adjusted = [0] * (degree + 1)
    for index in range(degree + 1):
        adjusted[index] = (prefixes[index] - constant) * inverse_power % mod
        inverse_power = inverse_power * inverse_ratio % mod
    return (pow(ratio, last, mod) * interpolate_consecutive(adjusted, last, mod) + constant) % mod

args = list(map(int, sys.stdin.buffer.read().split()))
ratio, degree = args[:2]
values = power_table(degree, degree, DEFAULT_MOD)
if len(args) == 3:
    print(sum_polynomial_exponential(values, ratio, args[2]))
else:
    print(limit_sum_polynomial_exponential(values, ratio))
