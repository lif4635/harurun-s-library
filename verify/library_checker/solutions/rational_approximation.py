"""Stern-Brocot木上の有理数と経路を扱う。"""
from math import gcd

class SternBrocotNode:
    """A positive reduced rational and its run-length Stern--Brocot path."""
    __slots__ = ('lx', 'ly', 'x', 'y', 'rx', 'ry', 'path', '_depth')

    def __init__(self, numerator=1, denominator=1, path=None):
        (self.lx, self.ly) = (0, 1)
        (self.x, self.y) = (1, 1)
        (self.rx, self.ry) = (1, 0)
        self.path = []
        self._depth = 0
        if path is not None:
            for step in path:
                if step > 0:
                    self.go_right(step)
                elif step < 0:
                    self.go_left(-step)
                else:
                    raise ValueError('path runs must be nonzero')
            return
        if numerator <= 0 or denominator <= 0:
            raise ValueError('fraction must be positive')
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
        return (self.x, self.y)

    def lower_bound(self):
        return (self.lx, self.ly)

    def upper_bound(self):
        return (self.rx, self.ry)

    def depth(self):
        return self._depth

    def go_left(self, steps=1):
        if steps <= 0:
            return self
        self._depth += steps
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
        self._depth += steps
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
        if steps < 0 or steps > self._depth:
            return False
        self._depth -= steps
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
        for (left, right) in zip(first.path, second.path):
            if (left < 0) != (right < 0):
                break
            amount = min(abs(left), abs(right))
            path.append(amount if left > 0 else -amount)
            if left != right:
                break
        return SternBrocotNode(path=path)
'分子・分母の上限内で、数値や単調な判定条件を挟む既約分数を求める。'

def rational_bounds(numerator, denominator, limit):
    """分子・分母がlimit以下の分数で、正の有理数を上下から挟む。"""
    if numerator <= 0 or denominator <= 0 or limit < 1:
        raise ValueError('requires a positive fraction and limit >= 1')
    (a, b, c, d) = (0, 1, 1, 0)
    (lower_error, upper_error) = (numerator, denominator)
    while a + c <= limit and b + d <= limit:
        if lower_error == upper_error:
            exact = (a + c, b + d)
            return (exact, exact)
        if lower_error > upper_error:
            steps = (lower_error - 1) // upper_error
            if c:
                steps = min(steps, (limit - a) // c)
            if d:
                steps = min(steps, (limit - b) // d)
            a += steps * c
            b += steps * d
            lower_error -= steps * upper_error
        else:
            steps = (upper_error - 1) // lower_error
            if a:
                steps = min(steps, (limit - c) // a)
            if b:
                steps = min(steps, (limit - d) // b)
            c += steps * a
            d += steps * b
            upper_error -= steps * lower_error
    return ((a, b), (c, d))

def stern_brocot_binary_search(predicate, limit):
    """Bracket a monotone predicate among reduced nonnegative fractions."""
    if limit < 0:
        raise ValueError('limit must be nonnegative')
    node = SternBrocotNode()
    if limit == 0:
        return (node.lower_bound(), node.upper_bound())
    if predicate((0, 1)):
        return ((0, 1), (0, 1))

    def over(return_value):
        return max(node.x, node.y) > limit or bool(predicate(node.get())) == return_value
    go_left = over(True)
    while True:
        if go_left:
            amount = 1
            while True:
                node.go_left(amount)
                if over(False):
                    node.go_parent(amount)
                    break
                amount <<= 1
            amount >>= 1
            while amount:
                node.go_left(amount)
                if over(False):
                    node.go_parent(amount)
                amount >>= 1
            node.go_left(1)
            if max(node.x, node.y) > limit:
                return (node.lower_bound(), node.upper_bound())
        else:
            amount = 1
            while True:
                node.go_right(amount)
                if over(True):
                    node.go_parent(amount)
                    break
                amount <<= 1
            amount >>= 1
            while amount:
                node.go_right(amount)
                if over(True):
                    node.go_parent(amount)
                amount >>= 1
            node.go_right(1)
            if max(node.x, node.y) > limit:
                return (node.lower_bound(), node.upper_bound())
        go_left = not go_left
binary_search_on_stern_brocot_tree = stern_brocot_binary_search
import sys
read = sys.stdin.buffer.readline
result = []
for _ in range(int(read())):
    (limit, numerator, denominator) = map(int, read().split())
    (lower, upper) = rational_bounds(numerator, denominator, limit)
    result.append('%d %d %d %d' % (lower + upper))
sys.stdout.write('\n'.join(result))
