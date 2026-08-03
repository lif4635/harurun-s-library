"""一次関数の評価・合成・反転を扱う。"""

class Affine:
    """f(x)=a*x+b; multiplication means apply left then right."""

    __slots__ = ("a", "b", "mod")

    def __init__(self, a=1, b=0, mod=None):
        self.mod = mod
        self.a = a if mod is None else a % mod
        self.b = b if mod is None else b % mod

    def __call__(self, value):
        result = self.a * value + self.b
        return result if self.mod is None else result % self.mod

    def __mul__(self, other):
        if self.mod != other.mod:
            raise ValueError("different moduli")
        # other(self(x))
        return Affine(self.a * other.a, self.b * other.a + other.b, self.mod)

    def __eq__(self, other):
        return (isinstance(other, Affine) and self.a == other.a
                and self.b == other.b and self.mod == other.mod)

