"""一点変更される列で、区間内の指定値の出現回数を数える構造。"""

from bisect import bisect_left
from math import isqrt

class PointSetRangeFrequency:
    __slots__ = ("values", "positions", "block_size")

    def __init__(self, values):
        if isinstance(values, int):
            values = [0] * values
        else:
            values = list(values)
        groups = {}
        for index, value in enumerate(values):
            if value not in groups:
                groups[value] = []
            groups[value].append(index)
        self.block_size = width = max(32, isqrt(len(values)))
        positions = {}
        for value, indices in groups.items():
            blocks = [indices[i:i + width] for i in range(0, len(indices), width)]
            positions[value] = (blocks, [block[-1] for block in blocks])
        self.values = values
        self.positions = positions

    def set(self, index, value):
        if index < 0:
            index += len(self.values)
        if not 0 <= index < len(self.values):
            raise IndexError("index out of range")
        old = self.values[index]
        if old == value:
            return
        positions = self.positions
        blocks, ends = positions[old]
        bi = bisect_left(ends, index)
        block = blocks[bi]
        block.pop(bisect_left(block, index))
        if not block:
            del blocks[bi]
            del ends[bi]
        else:
            ends[bi] = block[-1]
        if not blocks:
            del positions[old]
        elif len(blocks) > 1:
            bi = min(bi, len(blocks) - 1)
            if bi and len(blocks[bi - 1]) + len(blocks[bi]) <= self.block_size:
                blocks[bi - 1].extend(blocks.pop(bi))
                ends.pop(bi - 1)
                bi -= 1
            if bi + 1 < len(blocks) and len(blocks[bi]) + len(blocks[bi + 1]) <= self.block_size:
                blocks[bi].extend(blocks.pop(bi + 1))
                ends.pop(bi)
        target = positions.get(value)
        if target is None:
            positions[value] = ([[index]], [index])
        else:
            blocks, ends = target
            bi = min(bisect_left(ends, index), len(blocks) - 1)
            block = blocks[bi]
            block.insert(bisect_left(block, index), index)
            ends[bi] = block[-1]
            if len(block) > 2 * self.block_size:
                middle = len(block) // 2
                blocks[bi:bi + 1] = [block[:middle], block[middle:]]
                ends[bi:bi + 1] = [block[middle - 1], block[-1]]
        self.values[index] = value

    def query(self, left, right, value):
        positions = self.positions.get(value)
        if positions is None:
            return 0
        if left >= right:
            return 0
        blocks, ends = positions
        first = bisect_left(ends, left)
        if first == len(blocks):
            return 0
        last = bisect_left(ends, right)
        if first == last:
            block = blocks[first]
            return bisect_left(block, right) - bisect_left(block, left)
        count = len(blocks[first]) - bisect_left(blocks[first], left)
        for bi in range(first + 1, last):
            count += len(blocks[bi])
        if last < len(blocks):
            count += bisect_left(blocks[last], right)
        return count

    def tolist(self):
        return self.values.copy()

    def __str__(self):
        return str(self.values)

    def __repr__(self):
        return "PointSetRangeFrequency(%r)" % self.values
