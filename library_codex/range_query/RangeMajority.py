"""Strict-majority queries on an immutable sequence."""

from bisect import bisect_left


class RangeMajority:
    """Find a value occurring more than half the time in a half-open range."""

    __slots__ = ("n", "size", "data", "positions")

    def __init__(self, values):
        values = list(values)
        n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        data = [(None, 0)] * (size << 1)
        positions = {}
        for index, value in enumerate(values):
            data[size + index] = (value, 1)
            positions.setdefault(value, []).append(index)
        for node in range(size - 1, 0, -1):
            data[node] = self._merge(data[node << 1], data[node << 1 | 1])
        self.n = n
        self.size = size
        self.data = data
        self.positions = positions

    @staticmethod
    def _merge(first, second):
        if first[0] == second[0]:
            return first[0], first[1] + second[1]
        if first[1] >= second[1]:
            return first[0], first[1] - second[1]
        return second[0], second[1] - first[1]

    def count(self, value, left, right):
        """Return occurrences of ``value`` in ``[left, right)``."""
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        row = self.positions.get(value, ())
        return bisect_left(row, right) - bisect_left(row, left)

    def majority(self, left, right):
        """Return ``(value, count)`` for the strict majority, or ``None``."""
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        if left == right:
            return None
        left_node = left + self.size
        right_node = right + self.size
        first = (None, 0)
        second = (None, 0)
        data = self.data
        while left_node < right_node:
            if left_node & 1:
                first = self._merge(first, data[left_node])
                left_node += 1
            if right_node & 1:
                right_node -= 1
                second = self._merge(data[right_node], second)
            left_node >>= 1
            right_node >>= 1
        candidate = self._merge(first, second)[0]
        count = self.count(candidate, left, right)
        return (candidate, count) if count * 2 > right - left else None

    def is_majority(self, value, left, right):
        """Return whether ``value`` is a strict majority of the range."""
        return self.count(value, left, right) * 2 > right - left
