"""Gaussian整数の四則演算と最大公約数を扱う。"""

class GaussianInteger:
    __slots__ = ("real", "imag")

    def __init__(self, real=0, imag=0):
        self.real = real
        self.imag = imag

    @property
    def x(self):
        return self.real

    @property
    def y(self):
        return self.imag

    def norm(self):
        return self.real * self.real + self.imag * self.imag

    def conjugate(self):
        return GaussianInteger(self.real, -self.imag)

    conj = conjugate

    def __add__(self, other):
        return GaussianInteger(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return GaussianInteger(self.real - other.real, self.imag - other.imag)

    def __neg__(self):
        return GaussianInteger(-self.real, -self.imag)

    def __mul__(self, other):
        if isinstance(other, int):
            return GaussianInteger(self.real * other, self.imag * other)
        return GaussianInteger(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real,
        )

    def __eq__(self, other):
        return (isinstance(other, GaussianInteger)
                and self.real == other.real and self.imag == other.imag)

    def __repr__(self):
        return f"GaussianInteger({self.real}, {self.imag})"

    def __pow__(self, exponent):
        if exponent < 0:
            raise ValueError("negative Gaussian powers are not integral")
        result = GaussianInteger(1)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            exponent >>= 1
            if exponent:
                base = base * base
        return result

    def __divmod__(self, other):
        norm = other.norm()
        if norm == 0:
            raise ZeroDivisionError("Gaussian integer division by zero")
        product = self * other.conjugate()

        def nearest(value):
            quotient, remainder = divmod(value, norm)
            if remainder * 2 >= norm:
                quotient += 1
            return quotient

        quotient = GaussianInteger(nearest(product.real), nearest(product.imag))
        return quotient, self - quotient * other

    def __floordiv__(self, other):
        return divmod(self, other)[0]

    def __mod__(self, other):
        return divmod(self, other)[1]

def gaussian_gcd(first, second):
    while second != GaussianInteger():
        first, second = second, first % second
    return first

