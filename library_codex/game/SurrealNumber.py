"""dyadic有理数としてsurreal numberの比較・四則演算・子を扱う。"""

class SurrealNumber:
    """A short surreal number represented as numerator / 2**exponent."""

    __slots__ = ("numerator", "exponent")

    def __init__(self, numerator=0, exponent=0):
        if exponent < 0:
            raise ValueError("exponent must be nonnegative")
        while numerator and exponent and numerator & 1 == 0:
            numerator >>= 1
            exponent -= 1
        if numerator == 0:
            exponent = 0
        self.numerator = numerator
        self.exponent = exponent

    @property
    def p(self):
        return self.numerator

    @property
    def q(self):
        return self.exponent

    def _coerce(self, other):
        return other if isinstance(other, SurrealNumber) else SurrealNumber(other)

    def __add__(self, other):
        other = self._coerce(other)
        exponent = max(self.exponent, other.exponent)
        numerator = ((self.numerator << (exponent - self.exponent))
                     + (other.numerator << (exponent - other.exponent)))
        return SurrealNumber(numerator, exponent)

    def __sub__(self, other):
        return self + -self._coerce(other)

    def __neg__(self):
        return SurrealNumber(-self.numerator, self.exponent)

    def _difference(self, other):
        return (self - self._coerce(other)).numerator

    def __lt__(self, other):
        return self._difference(other) < 0

    def __le__(self, other):
        return self._difference(other) <= 0

    def __gt__(self, other):
        return self._difference(other) > 0

    def __ge__(self, other):
        return self._difference(other) >= 0

    def __eq__(self, other):
        try:
            return self._difference(other) == 0
        except (TypeError, ValueError):
            return False

    def __hash__(self):
        return hash((self.numerator, self.exponent))

    def __repr__(self):
        if self.exponent == 0:
            return f"SurrealNumber({self.numerator})"
        return f"SurrealNumber({self.numerator}, {self.exponent})"

    def children(self):
        if self.numerator == 0:
            return SurrealNumber(-1), SurrealNumber(1)
        if self.exponent == 0 and self.numerator > 0:
            return (SurrealNumber(self.numerator * 2 - 1, 1),
                    SurrealNumber(self.numerator + 1))
        if self.exponent == 0:
            return (SurrealNumber(self.numerator - 1),
                    SurrealNumber(self.numerator * 2 + 1, 1))
        difference = SurrealNumber(1, self.exponent + 1)
        return self - difference, self + difference

    child = children

    def larger(self):
        if self.numerator < 0:
            return SurrealNumber()
        return SurrealNumber((self.numerator >> self.exponent) + 1)

    def smaller(self):
        if self.numerator > 0:
            return SurrealNumber()
        ceiling = -((-self.numerator) >> self.exponent)
        return SurrealNumber(ceiling - 1)

    @staticmethod
    def between(left, right):
        left = left if isinstance(left, SurrealNumber) else SurrealNumber(left)
        right = right if isinstance(right, SurrealNumber) else SurrealNumber(right)
        if not left < right:
            raise ValueError("left must be smaller than right")
        exponent = 0
        while True:
            if exponent >= left.exponent:
                lower = left.numerator << (exponent - left.exponent)
            else:
                lower = left.numerator // (1 << (left.exponent - exponent))
            numerator = lower + 1

            common = max(exponent, right.exponent)
            scaled_numerator = numerator << (common - exponent)
            scaled_right = right.numerator << (common - right.exponent)
            if scaled_numerator < scaled_right:
                return SurrealNumber(numerator, exponent)
            exponent += 1

def reduce_surreal(left, right):
    return SurrealNumber.between(left, right)
