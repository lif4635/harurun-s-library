"""整数集合のxor線形基底を構築し、表現可能性や最大値を求める。"""

class XorBasis:
    """Reduced nonnegative integer XOR basis with ordered-value queries."""

    __slots__ = ("basis",)

    def __init__(self, values=()):
        self.basis = []
        for value in values:
            self.insert(value)

    def insert(self, value):
        reduced = value
        for basis in self.basis:
            if reduced ^ basis < reduced:
                reduced ^= basis
        if reduced == 0:
            return False
        for i, basis in enumerate(self.basis):
            if basis ^ reduced < basis:
                self.basis[i] = basis ^ reduced
        self.basis.append(reduced)
        self.basis.sort()
        return True

    add = insert

    def __len__(self):
        return len(self.basis)

    def contains(self, value):
        for basis in reversed(self.basis):
            if value ^ basis < value:
                value ^= basis
        return value == 0

    can_make = contains

    def kth_smallest(self, index):
        if not 0 <= index < 1 << len(self.basis):
            return -1
        result = 0
        for i, basis in enumerate(self.basis):
            if index >> i & 1:
                result ^= basis
        return result

    def maximum(self, xor=0):
        result = xor
        for basis in reversed(self.basis):
            if result ^ basis > result:
                result ^= basis
        return result

    def minimum(self, xor=0):
        result = xor
        for basis in reversed(self.basis):
            if result ^ basis < result:
                result ^= basis
        return result

    def xor_kth(self, xor, index):
        if not 0 <= index < 1 << len(self.basis):
            return -1
        return self.minimum(xor) ^ self.kth_smallest(index)

    def rank(self, value):
        """Index in sorted representable values, or -1 if unrepresentable."""
        index = 0
        reduced = value
        for i in range(len(self.basis) - 1, -1, -1):
            basis = self.basis[i]
            if reduced ^ basis < reduced:
                reduced ^= basis
                index |= 1 << i
        return index if reduced == 0 else -1

