"""Small algebraic and number-theoretic structures."""

from fractions import Fraction
from math import gcd


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


class SternBrocotNode:
    """A positive reduced rational and its run-length Stern--Brocot path."""

    __slots__ = ("lx", "ly", "x", "y", "rx", "ry", "path")

    def __init__(self, numerator=1, denominator=1, path=None):
        self.lx, self.ly = 0, 1
        self.x, self.y = 1, 1
        self.rx, self.ry = 1, 0
        self.path = []
        if path is not None:
            for step in path:
                if step > 0:
                    self.go_right(step)
                elif step < 0:
                    self.go_left(-step)
                else:
                    raise ValueError("path runs must be nonzero")
            return
        if numerator <= 0 or denominator <= 0:
            raise ValueError("fraction must be positive")
        divisor = gcd(numerator, denominator)
        numerator //= divisor
        denominator //= divisor
        while numerator != denominator:
            if numerator > denominator:
                steps = (numerator - 1) // denominator
                numerator -= steps * denominator
                self.go_right(steps)
            else:
                steps = (denominator - 1) // numerator
                denominator -= steps * numerator
                self.go_left(steps)

    def get(self):
        return self.x, self.y

    def lower_bound(self):
        return self.lx, self.ly

    def upper_bound(self):
        return self.rx, self.ry

    def depth(self):
        return sum(abs(step) for step in self.path)

    def go_left(self, steps=1):
        if steps <= 0:
            return self
        if not self.path or self.path[-1] > 0:
            self.path.append(-steps)
        else:
            self.path[-1] -= steps
        self.rx += self.lx * steps
        self.ry += self.ly * steps
        self.x = self.rx + self.lx
        self.y = self.ry + self.ly
        return self

    def go_right(self, steps=1):
        if steps <= 0:
            return self
        if not self.path or self.path[-1] < 0:
            self.path.append(steps)
        else:
            self.path[-1] += steps
        self.lx += self.rx * steps
        self.ly += self.ry * steps
        self.x = self.rx + self.lx
        self.y = self.ry + self.ly
        return self

    def go_parent(self, steps=1):
        if steps < 0 or steps > self.depth():
            return False
        while steps:
            amount = min(steps, abs(self.path[-1]))
            if self.path[-1] > 0:
                self.x -= self.rx * amount
                self.y -= self.ry * amount
                self.lx = self.x - self.rx
                self.ly = self.y - self.ry
                self.path[-1] -= amount
            else:
                self.x -= self.lx * amount
                self.y -= self.ly * amount
                self.rx = self.x - self.lx
                self.ry = self.y - self.ly
                self.path[-1] += amount
            steps -= amount
            if self.path[-1] == 0:
                self.path.pop()
        return True

    @staticmethod
    def lca(first, second):
        path = []
        for left, right in zip(first.path, second.path):
            if (left < 0) != (right < 0):
                break
            amount = min(abs(left), abs(right))
            path.append(amount if left > 0 else -amount)
            if left != right:
                break
        return SternBrocotNode(path=path)


def grundy_numbers(graph):
    """Return DAG Grundy numbers, or None when the graph has a cycle."""
    n = len(graph)
    indegree = [0] * n
    for row in graph:
        for to in row:
            indegree[to] += 1
    order = [v for v in range(n) if indegree[v] == 0]
    for v in order:
        for to in graph[v]:
            indegree[to] -= 1
            if indegree[to] == 0:
                order.append(to)
    if len(order) != n:
        return None
    grundy = [0] * n
    marker = [0] * (n + 1)
    stamp = 0
    for v in reversed(order):
        stamp += 1
        for to in graph[v]:
            marker[grundy[to]] = stamp
        value = 0
        while marker[value] == stamp:
            value += 1
        grundy[v] = value
    return grundy


def mex(values):
    values = set(value for value in values if value >= 0)
    result = 0
    while result in values:
        result += 1
    return result
