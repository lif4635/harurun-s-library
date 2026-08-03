"""部分列の昇順・降順sortと区間monoid積を処理する列構造。"""

from math import isqrt

class SortableSegmentTree:
    """Sortable sequence with point update and monoid range product."""

    __slots__ = ("n", "keys", "values", "op", "identity", "block",
                 "forward", "reverse")

    def __init__(self, keys, values, op=lambda a, b: a + b, identity=0,
                 block_size=None):
        if len(keys) != len(values):
            raise ValueError("key and value lengths differ")
        self.n = len(keys)
        self.keys = list(keys)
        self.values = list(values)
        self.op = op
        self.identity = identity
        self.block = block_size or max(32, isqrt(max(1, self.n)) + 1)
        count = (self.n + self.block - 1) // self.block
        self.forward = [identity] * count
        self.reverse = [identity] * count
        for index in range(count):
            self._rebuild(index)

    def _rebuild(self, block):
        left = block * self.block
        right = min(self.n, left + self.block)
        forward = reverse = self.identity
        for index in range(left, right):
            forward = self.op(forward, self.values[index])
        for index in range(right - 1, left - 1, -1):
            reverse = self.op(reverse, self.values[index])
        self.forward[block] = forward
        self.reverse[block] = reverse

    def update(self, index, key, value):
        self.keys[index] = key
        self.values[index] = value
        self._rebuild(index // self.block)

    set = update

    def query(self, left, right):
        result = self.identity
        while left < right and left % self.block:
            result = self.op(result, self.values[left])
            left += 1
        while left + self.block <= right:
            result = self.op(result, self.forward[left // self.block])
            left += self.block
        while left < right:
            result = self.op(result, self.values[left])
            left += 1
        return result

    def sort(self, left, right, reverse=False):
        pairs = list(zip(self.keys[left:right], self.values[left:right]))
        pairs.sort(key=lambda pair: pair[0], reverse=reverse)
        for offset, (key, value) in enumerate(pairs, left):
            self.keys[offset] = key
            self.values[offset] = value
        if left < right:
            first = left // self.block
            last = (right - 1) // self.block
            for block in range(first, last + 1):
                self._rebuild(block)
