"""形式的冪級数の分子と分母を保ったまま四則演算する。"""

from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_multiply,
    fps_shrink,
    fps_subtract,
)

class FPSFraction:
    __slots__ = ("numerator", "denominator", "mod")

    def __init__(self, numerator=None, denominator=None, mod=DEFAULT_MOD):
        self.mod = mod
        self.numerator = [0] if numerator is None else list(numerator)
        self.denominator = [1] if denominator is None else list(denominator)
        if not fps_shrink(self.denominator, mod):
            raise ZeroDivisionError("the denominator polynomial is zero")

    p = property(lambda self: self.numerator)
    q = property(lambda self: self.denominator)

    def _coerce(self, other):
        if isinstance(other, FPSFraction):
            if self.mod != other.mod:
                raise ValueError("moduli differ")
            return other
        return FPSFraction([other], [1], self.mod)

    def __add__(self, other):
        other = self._coerce(other)
        return FPSFraction(
            fps_add(
                fps_multiply(self.numerator, other.denominator, self.mod),
                fps_multiply(other.numerator, self.denominator, self.mod),
                self.mod,
            ),
            fps_multiply(self.denominator, other.denominator, self.mod),
            self.mod,
        )

    __radd__ = __add__

    def __neg__(self):
        return FPSFraction([-value % self.mod for value in self.numerator],
                           self.denominator, self.mod)

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        return FPSFraction(
            fps_multiply(self.numerator, other.numerator, self.mod),
            fps_multiply(self.denominator, other.denominator, self.mod),
            self.mod,
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other) / self

    def inverse(self):
        if not fps_shrink(self.numerator, self.mod):
            raise ZeroDivisionError("the zero fraction is not invertible")
        return FPSFraction(self.denominator, self.numerator, self.mod)

    def shrink(self):
        self.numerator = fps_shrink(self.numerator, self.mod)
        self.denominator = fps_shrink(self.denominator, self.mod)
        return self

