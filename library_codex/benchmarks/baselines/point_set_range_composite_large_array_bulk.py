"""Point updates and range products for an arbitrary monoid.

Use this when values change one position at a time and a half-open interval
must be folded with an associative operation.  ``max_right`` and ``min_left``
also find the first boundary where a monotone predicate stops holding.
"""

class SegTree:
    __slots__ = ('n', 'size', 'log', 'data', 'op', 'identity')

    def __init__(self, op, identity, values):
        if isinstance(values, int):
            n = values
            values = [identity] * n
        else:
            values = list(values)
            n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        data = [identity] * (size << 1)
        data[size:size + n] = values
        for node in range(size - 1, 0, -1):
            data[node] = op(data[node << 1], data[node << 1 | 1])
        self.n = n
        self.size = size
        self.log = size.bit_length() - 1
        self.data = data
        self.op = op
        self.identity = identity

    def set(self, index, value):
        node = index + self.size
        data = self.data
        data[node] = value
        op = self.op
        node >>= 1
        while node:
            data[node] = op(data[node << 1], data[node << 1 | 1])
            node >>= 1

    def add(self, index, value):
        """indexの現在値をop(value, current)で置き換える。O(log N)。"""
        node = index + self.size
        data = self.data
        op = self.op
        data[node] = op(value, data[node])
        node >>= 1
        while node:
            data[node] = op(data[node << 1], data[node << 1 | 1])
            node >>= 1

    def get(self, index):
        return self.data[index + self.size]

    def tolist(self):
        """現在の要素列をlistで返す。O(N)。"""
        return self.data[self.size:self.size + self.n]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'SegTree(%r)' % self.tolist()

    def prod(self, left, right):
        left += self.size
        right += self.size
        first = self.identity
        second = self.identity
        data = self.data
        op = self.op
        while left < right:
            if left & 1:
                first = op(first, data[left])
                left += 1
            if right & 1:
                right -= 1
                second = op(data[right], second)
            left >>= 1
            right >>= 1
        return op(first, second)
    query = prod

    def all_prod(self):
        return self.data[1]

    def max_right(self, left, predicate):
        if left == self.n:
            return self.n
        left += self.size
        value = self.identity
        data = self.data
        op = self.op
        while True:
            while not left & 1:
                left >>= 1
            merged = op(value, data[left])
            if not predicate(merged):
                while left < self.size:
                    left <<= 1
                    merged = op(value, data[left])
                    if predicate(merged):
                        value = merged
                        left += 1
                return min(left - self.size, self.n)
            value = merged
            left += 1
            if left & -left == left:
                break
        return self.n

    def min_left(self, right, predicate):
        if right == 0:
            return 0
        right += self.size
        value = self.identity
        data = self.data
        op = self.op
        while True:
            right -= 1
            while right > 1 and right & 1:
                right >>= 1
            merged = op(data[right], value)
            if not predicate(merged):
                while right < self.size:
                    right = right << 1 | 1
                    merged = op(data[right], value)
                    if predicate(merged):
                        value = merged
                        right -= 1
                return max(0, right + 1 - self.size)
            value = merged
            if right & -right == right:
                break
        return 0

    def __getitem__(self, index):
        return self.get(index)
import sys
from bisect import bisect_left

def compose(first, second):
    (a, b) = (first >> 30, first & 1073741823)
    (c, d) = (second >> 30, second & 1073741823)
    return a * c % 998244353 << 30 | (b * c + d) % 998244353
queries = list(map(int, sys.stdin.buffer.read().split()))
(n, q) = queries[:2]
positions = sorted({queries[i + 1] for i in range(2, len(queries), 4) if queries[i] == 0})
index = {value: i for (i, value) in enumerate(positions)}
tree = SegTree(compose, 1 << 30, len(positions))
answer = []
for i in range(2, len(queries), 4):
    if queries[i] == 0:
        tree.set(index[queries[i + 1]], queries[i + 2] << 30 | queries[i + 3])
    else:
        value = tree.prod(bisect_left(positions, queries[i + 1]), bisect_left(positions, queries[i + 2]))
        answer.append(((value >> 30) * queries[i + 3] + (value & 1073741823)) % 998244353)
print('\n'.join(map(str, answer)))
