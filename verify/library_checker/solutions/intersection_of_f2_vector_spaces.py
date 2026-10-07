"""整数集合のxor線形基底を構築し、表現可能性や最大値を求める。"""

class XorBasis:
    """Reduced nonnegative integer XOR basis with ordered-value queries."""
    __slots__ = ('basis',)

    def __init__(self, values=()):
        basis = []
        for value in values:
            for previous in basis:
                candidate = value ^ previous
                if candidate < value:
                    value = candidate
            if value:
                basis.append(value)
        basis.sort()
        for i in range(len(basis)):
            value = basis[i]
            for j in range(i):
                candidate = value ^ basis[j]
                if candidate < value:
                    value = candidate
            basis[i] = value
        self.basis = basis

    def insert(self, value):
        reduced = value
        for basis in self.basis:
            if reduced ^ basis < reduced:
                reduced ^= basis
        if reduced == 0:
            return False
        for (i, basis) in enumerate(self.basis):
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
        for (i, basis) in enumerate(self.basis):
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

    def intersection(self, other):
        """Return a new basis for values representable by both operands."""
        if self.basis == other.basis:
            result = XorBasis()
            result.basis = self.basis[:]
            return result
        residuals = []
        tags = []
        common = []
        for value in other.basis:
            residual = self.minimum(value)
            tag = value ^ residual
            for (previous, previous_tag) in zip(residuals, tags):
                candidate = residual ^ previous
                if candidate < residual:
                    residual = candidate
                    tag ^= previous_tag
            if residual:
                residuals.append(residual)
                tags.append(tag)
            else:
                common.append(tag)
        return XorBasis(common)

    def tolist(self):
        return self.basis[:]

    def __str__(self):
        return str(self.basis)

    def __repr__(self):
        return 'XorBasis(' + str(self.basis) + ')'
import sys
read = sys.stdin.buffer.readline
answers = []
for _ in range(int(read())):
    first = XorBasis(list(map(int, read().split()))[1:])
    second = XorBasis(list(map(int, read().split()))[1:])
    common = first.intersection(second).basis
    answers.append(' '.join(map(str, [len(common)] + common)))
sys.stdout.write('\n'.join(answers))
