"""Mode queries on an immutable sequence."""

from bisect import bisect_left
from math import isqrt


class StaticRangeMode:
    """Return a most frequent value in a half-open range in O(sqrt(N) log N)."""

    __slots__ = ("values", "n", "block_size", "block_count", "modes", "positions")

    def __init__(self, values, block_size=None):
        values = list(values)
        n = len(values)
        if block_size is None:
            block_size = max(1, isqrt(max(1, n)))
        if block_size <= 0:
            raise ValueError("block_size must be positive")
        block_count = (n + block_size - 1) // block_size
        modes = [[None] * block_count for _ in range(block_count)]
        for first_block in range(block_count):
            count = {}
            first_position = {}
            best_value = None
            best_count = 0
            best_position = n
            for index in range(first_block * block_size, n):
                value = values[index]
                if value not in count:
                    first_position[value] = index
                current = count.get(value, 0) + 1
                count[value] = current
                position = first_position[value]
                if current > best_count or current == best_count and position < best_position:
                    best_count = current
                    best_value = value
                    best_position = position
                if (index + 1) % block_size == 0 or index + 1 == n:
                    modes[first_block][index // block_size] = best_value
        positions = {}
        for index, value in enumerate(values):
            positions.setdefault(value, []).append(index)
        self.values = values
        self.n = n
        self.block_size = block_size
        self.block_count = block_count
        self.modes = modes
        self.positions = positions

    def count(self, value, left, right):
        """Return occurrences of ``value`` in ``[left, right)``."""
        row = self.positions.get(value, ())
        return bisect_left(row, right) - bisect_left(row, left)

    def mode(self, left, right):
        """Return ``(value, count)``; ties use the earliest range occurrence."""
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        if left == right:
            return None, 0
        width = self.block_size
        first_full = (left + width - 1) // width
        after_full = right // width
        candidates = []
        if first_full < after_full:
            candidates.append(self.modes[first_full][after_full - 1])
        candidates.extend(self.values[left:min(right, first_full * width)])
        candidates.extend(self.values[max(left, after_full * width):right])
        best_value = candidates[0]
        best_count = -1
        best_position = self.n
        seen = set()
        for value in candidates:
            if value in seen:
                continue
            seen.add(value)
            row = self.positions[value]
            begin = bisect_left(row, left)
            count = bisect_left(row, right) - begin
            position = row[begin]
            if count > best_count or count == best_count and position < best_position:
                best_value = value
                best_count = count
                best_position = position
        return best_value, best_count

    query = mode
