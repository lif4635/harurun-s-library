"""形式的冪級数と双対列の変換・作用を扱う。"""

from library_codex.fps.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_add,
    fps_multiply,
    fps_shrink,
    fps_subtract,
)

class DualFormalPowerSeries:
    """FPS value type with convolution-backed arithmetic.

    The C++ source caches the NTT domain.  Python callers get the same algebraic
    API while multiplication still routes through the optimized NTT backend.
    """

    __slots__ = ("coefficients", "mod")

    def __init__(self, coefficients=None, mod=DEFAULT_MOD):
        self.mod = mod
        self.coefficients = fps_shrink(coefficients or [], mod)

    @property
    def deg(self):
        return len(self.coefficients)

    def get(self):
        return self.coefficients[:]

    def _coerce(self, other):
        if isinstance(other, DualFormalPowerSeries):
            if self.mod != other.mod:
                raise ValueError("moduli differ")
            return other.coefficients
        return [other % self.mod]

    def __add__(self, other):
        return DualFormalPowerSeries(
            fps_add(self.coefficients, self._coerce(other), self.mod), self.mod
        )

    __radd__ = __add__

    def __sub__(self, other):
        return DualFormalPowerSeries(
            fps_subtract(self.coefficients, self._coerce(other), self.mod), self.mod
        )

    def __rsub__(self, other):
        return DualFormalPowerSeries(self._coerce(other), self.mod) - self

    def __neg__(self):
        return DualFormalPowerSeries(
            [-value % self.mod for value in self.coefficients], self.mod
        )

    def __mul__(self, other):
        return DualFormalPowerSeries(
            fps_multiply(self.coefficients, self._coerce(other), self.mod), self.mod
        )

    __rmul__ = __mul__

    def __lshift__(self, shift):
        if shift < 0:
            raise ValueError("shift must be nonnegative")
        if not self.coefficients:
            return DualFormalPowerSeries([], self.mod)
        return DualFormalPowerSeries([0] * shift + self.coefficients, self.mod)

