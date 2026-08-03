"""Stern-Brocot木上の有理数と経路を扱う。"""

from math import gcd

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

