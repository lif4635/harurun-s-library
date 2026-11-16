"""長方形内の整数解ax+by=cを、列挙せずに数え、辞書順に取得する。"""

from library_codex.number_theory.IntegerArithmetic import extended_gcd


class LinearDiophantine:
    """半開区間内の整数解を個数と等差数列で保持する。"""

    __slots__ = ("count", "_x", "_y", "_dx", "_dy", "_height")

    def __init__(self, a, b, c, xl, xr, yl, yr):
        if xl > xr or yl > yr:
            raise ValueError("invalid half-open range")
        self.count = 0
        self._x = self._y = self._dx = self._dy = self._height = 0
        if xl == xr or yl == yr:
            return
        if a == b == 0:
            if c == 0:
                self.count = (xr - xl) * (yr - yl)
                self._x, self._y, self._height = xl, yl, yr - yl
            return
        g, x, y = extended_gcd(a, b)
        if c % g:
            return
        x *= c // g
        y *= c // g
        dx, dy = b // g, -a // g
        if dx < 0 or dx == 0 and dy < 0:
            dx, dy = -dx, -dy
        lower = upper = None
        for base, step, lo, hi in ((x, dx, xl, xr), (y, dy, yl, yr)):
            if step == 0:
                if not lo <= base < hi:
                    return
                continue
            if step > 0:
                low, high = -((base - lo) // step), (hi - 1 - base) // step
            else:
                low, high = -((base - hi + 1) // step), (lo - base) // step
            lower = low if lower is None else max(lower, low)
            upper = high if upper is None else min(upper, high)
        if lower > upper:
            return
        self.count = upper - lower + 1
        self._x, self._y = x + dx * lower, y + dy * lower
        self._dx, self._dy = dx, dy

    def kth(self, k):
        """x、次にyの昇順でk番目の整数解(x, y)を返す。"""
        if not 0 <= k < self.count:
            raise IndexError("solution index out of range")
        if self._height:
            return self._x + k // self._height, self._y + k % self._height
        return self._x + k * self._dx, self._y + k * self._dy

    def __repr__(self):
        return "LinearDiophantine(count=" + str(self.count) + ", first=" + str(self.kth(0) if self.count else None) + ")"
