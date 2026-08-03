"""固定長bit列の更新・個数・前後のset bit探索を行う集合。"""

class BitSet:
    __slots__ = ("n", "bits", "mask")

    def __init__(self, size, value=0):
        if size < 0:
            raise ValueError("size must be nonnegative")
        mask = (1 << size) - 1
        self.n = size
        self.bits = int(value) & mask
        self.mask = mask

    def set(self, index, value=True):
        if value:
            self.bits |= 1 << index
        else:
            self.bits &= ~(1 << index)

    def reset(self, index=None):
        if index is None:
            self.bits = 0
        else:
            self.bits &= ~(1 << index)

    def flip(self, index=None):
        if index is None:
            self.bits ^= self.mask
        else:
            self.bits ^= 1 << index

    def get(self, index):
        return self.bits >> index & 1

    def count(self):
        return self.bits.bit_count()

    def any(self):
        return bool(self.bits)

    def all(self):
        return self.bits == self.mask

    def find_next(self, index):
        shifted = self.bits >> max(0, index)
        if not shifted:
            return -1
        return max(0, index) + (shifted & -shifted).bit_length() - 1

    def find_prev(self, index):
        if index < 0:
            return -1
        value = self.bits & ((1 << (min(index, self.n - 1) + 1)) - 1)
        return value.bit_length() - 1

    def __getitem__(self, index):
        return self.get(index)

    def __len__(self):
        return self.n

    def __int__(self):
        return self.bits

    def __and__(self, other):
        return BitSet(max(self.n, other.n), self.bits & other.bits)

    def __or__(self, other):
        return BitSet(max(self.n, other.n), self.bits | other.bits)

    def __xor__(self, other):
        return BitSet(max(self.n, other.n), self.bits ^ other.bits)

    def __invert__(self):
        return BitSet(self.n, self.bits ^ self.mask)

    def __lshift__(self, shift):
        return BitSet(self.n, self.bits << shift)

    def __rshift__(self, shift):
        return BitSet(self.n, self.bits >> shift)
