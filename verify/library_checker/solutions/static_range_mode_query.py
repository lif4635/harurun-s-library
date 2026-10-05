"""Mode queries on an immutable sequence."""
from bisect import bisect_left
from math import isqrt

class StaticRangeMode:
    """Return a most frequent value in a half-open range in O(sqrt(N))."""
    __slots__ = ('values', 'n', 'block_size', 'block_count', 'modes', 'positions', '_ids', '_ranks', '_occurrences', '_mode_counts', '_mode_indices')

    def __init__(self, values, block_size=None):
        values = list(values)
        n = len(values)
        if block_size is None:
            block_size = max(1, isqrt(max(1, n)))
        if block_size <= 0:
            raise ValueError('block_size must be positive')
        ids = []
        ranks = []
        mapping = {}
        occurrences = []
        positions = {}
        for (index, value) in enumerate(values):
            if value not in mapping:
                mapping[value] = len(occurrences)
                row = []
                occurrences.append(row)
                positions[value] = row
            code = mapping[value]
            row = occurrences[code]
            ids.append(code)
            ranks.append(len(row))
            row.append(index)
        block_count = (n + block_size - 1) // block_size
        modes = [[None] * block_count for _ in range(block_count)]
        mode_counts = [[0] * block_count for _ in range(block_count)]
        mode_indices = [[n] * block_count for _ in range(block_count)]
        for first_block in range(block_count):
            count = [0] * len(occurrences)
            first_position = [n] * len(occurrences)
            best_count = 0
            best_position = n
            for last_block in range(first_block, block_count):
                for index in range(last_block * block_size, min(n, (last_block + 1) * block_size)):
                    code = ids[index]
                    if count[code] == 0:
                        first_position[code] = index
                    current = count[code] + 1
                    count[code] = current
                    position = first_position[code]
                    if current > best_count or (current == best_count and position < best_position):
                        best_count = current
                        best_position = position
                modes[first_block][last_block] = values[best_position]
                mode_counts[first_block][last_block] = best_count
                mode_indices[first_block][last_block] = best_position
        self.values = values
        self.n = n
        self.block_size = block_size
        self.block_count = block_count
        self.modes = modes
        self.positions = positions
        self._ids = ids
        self._ranks = ranks
        self._occurrences = occurrences
        self._mode_counts = mode_counts
        self._mode_indices = mode_indices

    def count(self, value, left, right):
        """Return occurrences of value in [left, right)."""
        row = self.positions.get(value, ())
        return bisect_left(row, right) - bisect_left(row, left)

    def mode(self, left, right):
        """Return (value, count); ties use the earliest range occurrence."""
        if not 0 <= left <= right <= self.n:
            raise IndexError('invalid half-open range')
        if left == right:
            return (None, 0)
        width = self.block_size
        first_full = (left + width - 1) // width
        after_full = right // width
        best_count = 0
        best_position = self.n
        left_end = right
        right_start = right
        if first_full < after_full:
            best_count = self._mode_counts[first_full][after_full - 1]
            best_position = self._mode_indices[first_full][after_full - 1]
            left_end = first_full * width
            right_start = after_full * width
        ids = self._ids
        ranks = self._ranks
        occurrences = self._occurrences
        for index in range(left, left_end):
            row = occurrences[ids[index]]
            rank = ranks[index]
            if rank and row[rank - 1] >= left:
                continue
            while rank + best_count < len(row) and row[rank + best_count] < right:
                best_count += 1
                best_position = index
            if index < best_position and rank + best_count <= len(row):
                if row[rank + best_count - 1] < right:
                    best_position = index
        for index in range(right - 1, right_start - 1, -1):
            row = occurrences[ids[index]]
            rank = ranks[index]
            if rank + 1 < len(row) and row[rank + 1] < right:
                continue
            while rank - best_count >= 0 and row[rank - best_count] >= left:
                best_count += 1
                best_position = row[rank - best_count + 1]
            begin = rank - best_count + 1
            if begin >= 0 and left <= row[begin] < best_position:
                best_position = row[begin]
        return (self.values[best_position], best_count)
    query = mode

    def tolist(self):
        return self.values[:]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'StaticRangeMode(%r)' % self.tolist()
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, q) = map(int, read().split())
    table = StaticRangeMode(list(map(int, read().split())))
    result = []
    for _ in range(q):
        (left, right) = map(int, read().split())
        (value, count) = table.mode(left, right)
        result.append(f'{value} {count}')
    sys.stdout.write('\n'.join(result))
if __name__ == '__main__':
    main()
