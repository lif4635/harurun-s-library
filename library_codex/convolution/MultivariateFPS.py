from library_codex.convolution.AdvancedConvolution import multivariate_multiplication
from library_codex.convolution.FormalPowerSeries import DEFAULT_MOD


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
        for index in range(1, len(result)):
            result[index] = result[index] * pow(index, -1, self.mod) % self.mod
        return MultivariateFormalPowerSeries(result, self.base, self.mod)

    def inverse(self):
        if self.coefficients[0] == 0:
            raise ZeroDivisionError("constant coefficient is zero")
        size = len(self.coefficients)
        result = [0] * size
        result[0] = pow(self.coefficients[0], -1, self.mod)
        current = MultivariateFormalPowerSeries(result, self.base, self.mod)
        degree = 1
        maximum_degree = 1 + sum(radix - 1 for radix in self.base)
        while degree < maximum_degree:
            product = self * current
            correction = [-value % self.mod for value in product.coefficients]
            correction[0] = (correction[0] + 2) % self.mod
            current = current * MultivariateFormalPowerSeries(
                correction, self.base, self.mod
            )
            degree <<= 1
        return current

    inv = inverse

    def logarithm(self):
        if self.coefficients[0] != 1:
            raise ValueError("constant coefficient must be one")
        return (self.derivative() * self.inverse()).integral()

    log = logarithm

    def exponential(self):
        if self.coefficients[0] != 0:
            raise ValueError("constant coefficient must be zero")
        result = [0] * len(self.coefficients)
        result[0] = 1
        current = MultivariateFormalPowerSeries(result, self.base, self.mod)
        degree = 1
        maximum_degree = 1 + sum(radix - 1 for radix in self.base)
        while degree < maximum_degree:
            current = current * (self - current.logarithm() + 1)
            degree <<= 1
        return current

    exp = exponential

    def power(self, exponent):
        if exponent < 0:
            return self.inverse().power(-exponent)
        result_values = [0] * len(self.coefficients)
        result_values[0] = 1
        result = MultivariateFormalPowerSeries(
            result_values, self.base, self.mod
        )
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            exponent >>= 1
            if exponent:
                base = base * base
        return result

    pow = power


MultivariateFPS = MultivariateFormalPowerSeries
