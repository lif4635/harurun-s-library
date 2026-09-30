"""各変数の次数を打ち切った係数列で、積・逆数・log・exp・整数冪を求める。"""

from library_codex.convolution.MultivariateMultiplication import DEFAULT_MOD, _multiply_prefix, multivariate_multiplication
from library_codex.convolution.NTT998 import intt, ntt


def _inverse_prefix(series, base, mod, size):
    if mod == DEFAULT_MOD and len(base) == 2 and min(base) > 1 and 256 <= size <= 1 << 23:
        return _inverse_2d(series, base[0], size)
    result = [pow(series[0], -1, mod)]
    while len(result) < size:
        previous = len(result)
        target = min(2 * previous, size)
        error = _multiply_prefix(series, result, base, mod, target)
        error[:previous] = [0] * previous
        error = _multiply_prefix(error, result, base, mod, target)
        result.extend(-value % mod for value in error[previous:])
    return result


def _inverse_2d(series, width, size):
    mod = DEFAULT_MOD
    result = [pow(series[0], -1, mod)]
    while len(result) < size:
        degree = len(result)
        length = 2 * degree
        left = [[0] * length for _ in range(2)]
        right = [[0] * length for _ in range(2)]
        for i, value in enumerate(series[:length]):
            left[i // width & 1][i] = value
        for i, value in enumerate(result):
            right[i // width & 1][i] = value
        for row in left + right:
            ntt(row)
        a, b = left
        c, d = right
        high = [[(a[i] * c[i] + b[i] * d[i]) % mod for i in range(length)],
                [(a[i] * d[i] + b[i] * c[i]) % mod for i in range(length)]]
        for row in high:
            intt(row)
        left = [[0] * length for _ in range(2)]
        for i in range(degree, min(length, size)):
            color = i // width & 1
            left[color][i] = high[color][i]
        for row in left:
            ntt(row)
        a, b = left
        high = [[(a[i] * c[i] + b[i] * d[i]) % mod for i in range(length)],
                [(a[i] * d[i] + b[i] * c[i]) % mod for i in range(length)]]
        for row in high:
            intt(row)
        result.extend(-high[i // width & 1][i] % mod for i in range(degree, min(length, size)))
    return result


def _inverses(size, mod):
    result = [1] * size
    for index in range(2, size):
        result[index] = result[index - 1] * index % mod
    inverse = pow(result[-1], -1, mod)
    for index in range(size - 1, 0, -1):
        result[index], inverse = inverse * result[index - 1] % mod, inverse * index % mod
    result[0] = 0
    return result


def _log_prefix(series, base, mod, size, inverses):
    derivative = [index * value % mod for index, value in enumerate(series[:size])]
    inverse = _inverse_prefix(series, base, mod, size)
    result = _multiply_prefix(derivative, inverse, base, mod, size)
    for index in range(size):
        result[index] = result[index] * inverses[index] % mod
    return result


def _exp_prefix(series, base, mod, size):
    inverses = _inverses(size, mod)
    result = [1]
    while len(result) < size:
        target = min(2 * len(result), size)
        logarithm = _log_prefix(result, base, mod, target, inverses)
        correction = [(series[index] - logarithm[index]) % mod for index in range(target)]
        correction[0] += 1
        result = _multiply_prefix(result, correction, base, mod, target)
    return result


def _sparse_2d(series, base, mod, exponent=None, logarithm=False):
    if len(base) != 2 or mod != DEFAULT_MOD or len(series) >= mod:
        return None
    width = base[0]
    terms = []
    limit = min(64 if exponent == -1 else 128, max(16, len(series) // 8))
    inverse_constant = pow(series[0], -1, mod) if exponent is not None else 1
    for offset in range(1, len(series)):
        coefficient = series[offset] * inverse_constant % mod
        if coefficient:
            terms.append((offset, offset % width, coefficient))
            if len(terms) > limit:
                return None
    inverses = _inverses(len(series), mod)
    result = [0] * len(series)
    result[0] = 1 if exponent is None else pow(series[0], exponent, mod)
    if logarithm:
        result[0] = 0
        for index in range(1, len(series)):
            x = index % width
            total = index * series[index] % mod
            for offset, column, coefficient in terms:
                if offset >= index:
                    break
                if column <= x:
                    total -= coefficient * result[index - offset]
            result[index] = total % mod
        for index in range(1, len(series)):
            result[index] = result[index] * inverses[index] % mod
    elif exponent is None:
        terms = [(offset, x, offset * coefficient % mod) for offset, x, coefficient in terms]
        for index in range(1, len(series)):
            x = index % width
            total = 0
            for offset, column, coefficient in terms:
                if offset > index:
                    break
                if column <= x:
                    total += coefficient * result[index - offset]
            result[index] = total % mod * inverses[index] % mod
    else:
        factor = (exponent + 1) % mod
        terms = [(offset, x, coefficient, factor * offset * coefficient % mod) for offset, x, coefficient in terms]
        for index in range(1, len(series)):
            x = index % width
            total = 0
            for offset, column, coefficient, weighted in terms:
                if offset > index:
                    break
                if column <= x:
                    total += (weighted - index * coefficient) % mod * result[index - offset]
            result[index] = total % mod * inverses[index] % mod
    return result


class MultivariateFormalPowerSeries:
    __slots__ = ("coefficients", "base", "mod")

    def __init__(self, coefficients=None, base=(), mod=DEFAULT_MOD):
        self.base = tuple(base)
        size = 1
        for radix in self.base:
            if radix <= 0:
                raise ValueError("radices must be positive")
            size *= radix
        if coefficients is None:
            coefficients = [0] * size
        if len(coefficients) != size:
            raise ValueError("coefficient length must equal product(base)")
        self.coefficients = [value % mod for value in coefficients]
        self.mod = mod

    f = property(lambda self: self.coefficients)

    def index(self, *indices):
        if len(indices) != len(self.base):
            raise IndexError("wrong number of multivariate indices")
        result = 0
        stride = 1
        for value, radix in zip(indices, self.base):
            if not 0 <= value < radix:
                raise IndexError("multivariate index out of range")
            result += value * stride
            stride *= radix
        return result

    id = index

    def get(self, *indices):
        return self.coefficients[self.index(*indices)]

    def set(self, *indices_and_value):
        *indices, value = indices_and_value
        self.coefficients[self.index(*indices)] = value % self.mod

    def _series(self, other):
        if not isinstance(other, MultivariateFormalPowerSeries):
            result = [0] * len(self.coefficients)
            result[0] = other % self.mod
            return result
        if self.base != other.base or self.mod != other.mod:
            raise ValueError("bases or moduli differ")
        return other.coefficients

    def __add__(self, other):
        source = self._series(other)
        return MultivariateFormalPowerSeries(
            [(left + right) % self.mod
             for left, right in zip(self.coefficients, source)],
            self.base, self.mod,
        )

    __radd__ = __add__

    def __neg__(self):
        return MultivariateFormalPowerSeries(
            [-value % self.mod for value in self.coefficients],
            self.base, self.mod,
        )

    def __sub__(self, other):
        return self + (-other if isinstance(other, MultivariateFormalPowerSeries)
                       else -other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        if isinstance(other, MultivariateFormalPowerSeries):
            source = self._series(other)
            result = multivariate_multiplication(
                self.coefficients, source, self.base, self.mod
            )
        else:
            result = [value * other % self.mod for value in self.coefficients]
        return MultivariateFormalPowerSeries(result, self.base, self.mod)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, MultivariateFormalPowerSeries):
            return self * other.inverse()
        return self * pow(other, -1, self.mod)

    def derivative(self):
        return MultivariateFormalPowerSeries(
            [index * value % self.mod
             for index, value in enumerate(self.coefficients)],
            self.base, self.mod,
        )

    diff = derivative

    def integral(self):
        result = self.coefficients[:]
        inverses = _inverses(len(result), self.mod)
        for index in range(1, len(result)):
            result[index] = result[index] * inverses[index] % self.mod
        return MultivariateFormalPowerSeries(result, self.base, self.mod)

    def inverse(self):
        if self.coefficients[0] == 0:
            raise ZeroDivisionError("constant coefficient is zero")
        result = _sparse_2d(self.coefficients, self.base, self.mod, -1)
        if result is None:
            result = _inverse_prefix(self.coefficients, self.base, self.mod, len(self.coefficients))
        return MultivariateFormalPowerSeries(result, self.base, self.mod)

    inv = inverse

    def logarithm(self):
        if self.coefficients[0] != 1:
            raise ValueError("constant coefficient must be one")
        size = len(self.coefficients)
        result = _sparse_2d(self.coefficients, self.base, self.mod, logarithm=True)
        if result is None:
            result = _log_prefix(self.coefficients, self.base, self.mod, size, _inverses(size, self.mod))
        return MultivariateFormalPowerSeries(result, self.base, self.mod)

    log = logarithm

    def exponential(self):
        if self.coefficients[0] != 0:
            raise ValueError("constant coefficient must be zero")
        result = _sparse_2d(self.coefficients, self.base, self.mod)
        if result is None:
            result = _exp_prefix(self.coefficients, self.base, self.mod, len(self.coefficients))
        return MultivariateFormalPowerSeries(result, self.base, self.mod)

    exp = exponential

    def power(self, exponent):
        if exponent and self.coefficients[0]:
            values = _sparse_2d(self.coefficients, self.base, self.mod, exponent)
            if values is not None:
                return MultivariateFormalPowerSeries(values, self.base, self.mod)
            if abs(exponent) > 8 and self.mod == DEFAULT_MOD and len(self.coefficients) < self.mod:
                constant = self.coefficients[0]
                normalized = self * pow(constant, -1, self.mod)
                return (normalized.logarithm() * exponent).exponential() * pow(constant, exponent, self.mod)
        base = self
        if exponent < 0:
            base = self.inverse()
            exponent = -exponent
        result_values = [0] * len(self.coefficients)
        result_values[0] = 1
        result = MultivariateFormalPowerSeries(
            result_values, self.base, self.mod
        )
        while exponent:
            if exponent & 1:
                result = result * base
            exponent >>= 1
            if exponent:
                base = base * base
        return result

    pow = power


MultivariateFPS = MultivariateFormalPowerSeries
