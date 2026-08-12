"""Frequency queries on an immutable sequence."""

from bisect import bisect_left


class StaticRangeFrequency:
    """Count equal values in half-open ranges using occurrence lists."""

    __slots__ = ("n", "index")

    def __init__(self, values):
        values = list(values)
        index = {}
        for position, value in enumerate(values):
            index.setdefault(value, []).append(position)
        self.n = len(values)
        self.index = index

    def count(self, value, left=0, right=None):
        """Return the number of ``value`` in ``[left, right)``."""
        if right is None:
            right = self.n
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        positions = self.index.get(value, ())
        return bisect_left(positions, right) - bisect_left(positions, left)

    def kth(self, value, k):
        """Return the index of the zero-based ``k``-th occurrence, or ``-1``."""
        positions = self.index.get(value, ())
        return positions[k] if 0 <= k < len(positions) else -1

    def positions(self, value):
        """Return all occurrence indices as an immutable tuple."""
        return tuple(self.index.get(value, ()))
