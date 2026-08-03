from fractions import Fraction


def _trim(values):
    result = [Fraction(value) for value in values]
    while result and result[-1] == 0:
        result.pop()
    return result


def _add(first, second):
    result = [Fraction(0)] * max(len(first), len(second))
    for index, value in enumerate(first):
        result[index] += value
    for index, value in enumerate(second):
        result[index] += value
    return result


def _multiply(first, second):
    if not first or not second:
        return []
    result = [Fraction(0)] * (len(first) + len(second) - 1)
    for i, left in enumerate(first):
        if left:
            for j, right in enumerate(second):
                result[i + j] += left * right
    return result


class RationalFormalPowerSeries:
    __slots__ = ("coefficients",)

    def __init__(self, coefficients=()):
        self.coefficients = [Fraction(value) for value in coefficients]

    def __len__(self):
        return len(self.coefficients)

    def __getitem__(self, index):
        return self.coefficients[index]

    def __iter__(self):
        return iter(self.coefficients)

    def _series(self, other):
        if isinstance(other, RationalFormalPowerSeries):
            return other.coefficients
        return [Fraction(other)]

    def __add__(self, other):
        return RationalFormalPowerSeries(_add(self.coefficients, self._series(other)))

    __radd__ = __add__

    def __neg__(self):
        return RationalFormalPowerSeries([-value for value in self.coefficients])

    def __sub__(self, other):
        return self + (-other if isinstance(other, RationalFormalPowerSeries)
                       else -Fraction(other))

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other):
        return RationalFormalPowerSeries(
            _multiply(self.coefficients, self._series(other))
        )

    __rmul__ = __mul__

    def pre(self, size):
        result = self.coefficients[:size]
        result.extend([Fraction(0)] * (size - len(result)))
        return RationalFormalPowerSeries(result)

    def shrink(self):
        self.coefficients = _trim(self.coefficients)
        return self

    def derivative(self):
        return RationalFormalPowerSeries([
            index * self.coefficients[index]
            for index in range(1, len(self.coefficients))
        ])

    diff = derivative

    def integral(self):
        return RationalFormalPowerSeries(
            [0] + [value / (index + 1)
                   for index, value in enumerate(self.coefficients)]
        )

    def evaluate(self, point):
        point = Fraction(point)
        result = Fraction(0)
        for value in reversed(self.coefficients):
            result = result * point + value
        return result

    eval = evaluate

    def inverse(self, degree=None):
        if degree is None:
            degree = len(self.coefficients)
        if not self.coefficients or self.coefficients[0] == 0:
            raise ZeroDivisionError("constant coefficient is zero")
        result = [1 / self.coefficients[0]]
        for index in range(1, degree):
            total = Fraction(0)
            for offset in range(1, min(index + 1, len(self.coefficients))):
                total += self.coefficients[offset] * result[index - offset]
            result.append(-total / self.coefficients[0])
        return RationalFormalPowerSeries(result)

    inv = inverse

    def logarithm(self, degree=None):
        if degree is None:
            degree = len(self.coefficients)
        if not self.coefficients or self.coefficients[0] != 1:
            raise ValueError("constant coefficient must be one")
        return (self.derivative() * self.inverse(degree)).pre(
            max(0, degree - 1)
        ).integral()

    log = logarithm

    def exponential(self, degree=None):
        if degree is None:
            degree = len(self.coefficients)
        if self.coefficients and self.coefficients[0] != 0:
            raise ValueError("constant coefficient must be zero")
        result = [Fraction(0)] * degree
        if degree:
            result[0] = 1
        for index in range(1, degree):
            total = Fraction(0)
            for offset in range(1, min(index + 1, len(self.coefficients))):
                total += offset * self.coefficients[offset] * result[index - offset]
            result[index] = total / index
        return RationalFormalPowerSeries(result)

    exp = exponential

    def power(self, exponent, degree=None):
        if degree is None:
            degree = len(self.coefficients)
        if exponent < 0:
            return self.inverse(degree).power(-exponent, degree)
        result = RationalFormalPowerSeries([1])
        base = self.pre(degree)
        while exponent:
            if exponent & 1:
                result = (result * base).pre(degree)
            exponent >>= 1
            if exponent:
                base = (base * base).pre(degree)
        return result.pre(degree)

    pow = power


FormalPowerSeries_rational = RationalFormalPowerSeries
