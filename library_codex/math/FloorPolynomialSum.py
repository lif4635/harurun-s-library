from math import comb


class _FloorPolynomialMonoid:
    __slots__ = ("k", "l", "mod", "sums", "dx", "dy")

    def __init__(self, k, l, mod=None):
        self.k = k
        self.l = l
        self.mod = mod
        self.sums = [[0] * (l + 1) for _ in range(k + 1)]
        self.dx = 0
        self.dy = 0

    def copy(self):
        result = _FloorPolynomialMonoid(self.k, self.l, self.mod)
        result.sums = [row[:] for row in self.sums]
        result.dx = self.dx
        result.dy = self.dy
        return result

    @classmethod
    def x_step(cls, k, l, mod=None):
        result = cls(k, l, mod)
        result.sums[0][0] = 1
        result.dx = 1
        return result

    @classmethod
    def y_step(cls, k, l, mod=None):
        result = cls(k, l, mod)
        result.dy = 1
        return result

    @staticmethod
    def multiply(first, second):
        left = first.copy()
        right = second.copy()
        k, l, mod = left.k, left.l, left.mod
        powers_x = [1] * (k + 1)
        powers_y = [1] * (l + 1)
        for index in range(k):
            powers_x[index + 1] = powers_x[index] * left.dx
        for index in range(l):
            powers_y[index + 1] = powers_y[index] * left.dy
        for i in range(k + 1):
            for j in range(l, -1, -1):
                value = right.sums[i][j]
                if value:
                    for target in range(j + 1, l + 1):
                        right.sums[i][target] += (
                            comb(target, j) * powers_y[target - j] * value
                        )
        for j in range(l + 1):
            for i in range(k, -1, -1):
                value = right.sums[i][j]
                if value:
                    for target in range(i, k + 1):
                        left.sums[target][j] += (
                            comb(target, i) * powers_x[target - i] * value
                        )
        left.dx += right.dx
        left.dy += right.dy
        if mod is not None:
            left.dx %= mod
            left.dy %= mod
            left.sums = [[value % mod for value in row] for row in left.sums]
        return left

    @classmethod
    def power(cls, value, exponent):
        result = cls(value.k, value.l, value.mod)
        base = value
        while exponent:
            if exponent & 1:
                result = cls.multiply(result, base)
            exponent >>= 1
            if exponent:
                base = cls.multiply(base, base)
        return result


def _floor_path_product(n, modulus, multiplier, addend, x_step, y_step):
    monoid = _FloorPolynomialMonoid
    prefix = monoid(x_step.k, x_step.l, x_step.mod)
    suffix = monoid(x_step.k, x_step.l, x_step.mod)
    while True:
        x_step = monoid.multiply(
            x_step, monoid.power(y_step, multiplier // modulus)
        )
        multiplier %= modulus
        prefix = monoid.multiply(
            prefix, monoid.power(y_step, addend // modulus)
        )
        addend %= modulus
        total = multiplier * n + addend
        if total < modulus:
            prefix = monoid.multiply(prefix, monoid.power(x_step, n))
            break
        suffix = monoid.multiply(
            y_step,
            monoid.multiply(
                monoid.power(x_step, (total % modulus) // multiplier), suffix
            ),
        )
        n = total // modulus - 1
        addend = modulus - addend + multiplier - 1
        modulus, multiplier = multiplier, modulus
        x_step, y_step = y_step, x_step
    return monoid.multiply(prefix, suffix)


def floor_polynomial_sums(n, modulus, multiplier, addend,
                          max_x_power, max_y_power, mod=None):
    """Return sum i**k * floor((a*i+b)/m)**l for every k,l."""
    if max_x_power < 0 or max_y_power < 0:
        raise ValueError("power bounds must be nonnegative")
    result = [[0] * (max_y_power + 1)
              for _ in range(max_x_power + 1)]
    if n <= 0:
        return result
    if modulus == 0:
        raise ZeroDivisionError("modulus is zero")
    if modulus < 0:
        modulus = -modulus
        multiplier = -multiplier
        addend = -addend
    negative = multiplier < 0
    if negative:
        addend = modulus - 1 - addend
    quotient, remainder = divmod(addend, modulus)
    x_step = _FloorPolynomialMonoid.x_step(
        max_x_power, max_y_power, mod
    )
    y_step = _FloorPolynomialMonoid.y_step(
        max_x_power, max_y_power, mod
    )
    base = _floor_path_product(
        n, modulus, abs(multiplier), remainder, x_step, y_step
    )
    offset = _FloorPolynomialMonoid(max_x_power, max_y_power, mod)
    offset.dy = quotient
    base = _FloorPolynomialMonoid.multiply(offset, base)
    for i in range(max_x_power + 1):
        for j in range(max_y_power + 1):
            value = base.sums[i][j]
            if negative and j & 1:
                value = -value
            result[i][j] = value if mod is None else value % mod
    return result


ScarySum = floor_polynomial_sums
