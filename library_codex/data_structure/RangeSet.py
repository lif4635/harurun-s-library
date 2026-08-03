"""互いに素な整数区間を追加・削除し、包含判定とmexを行う集合。"""

from library_codex.data_structure.TreapSet import TreapSet

class RangeSet:
    __slots__ = ("starts", "ends", "covered_length")

    def __init__(self):
        self.starts = TreapSet()
        self.ends = {}
        self.covered_length = 0

    def add(self, left, right):
        if left >= right:
            return 0
        starts = self.starts
        ends = self.ends
        start = starts.le(left)
        if start is not None and ends[start] >= left:
            left = start
            right = max(right, ends[start])
            self.covered_length -= ends.pop(start) - start
            starts.discard(start)
        start = starts.ge(left)
        while start is not None and start <= right:
            right = max(right, ends[start])
            self.covered_length -= ends.pop(start) - start
            starts.discard(start)
            start = starts.ge(left)
        starts.add(left)
        ends[left] = right
        added = right - left
        self.covered_length += added
        return added

    def discard(self, left, right):
        if left >= right:
            return 0
        overlaps = []
        start = self.starts.le(left)
        if start is None or self.ends[start] <= left:
            start = self.starts.ge(left)
        while start is not None and start < right:
            overlaps.append((start, self.ends[start]))
            start = self.starts.gt(start)
        removed = 0
        for start, end in overlaps:
            self.starts.discard(start)
            del self.ends[start]
            overlap = max(0, min(end, right) - max(start, left))
            removed += overlap
            self.covered_length -= end - start
            if start < left:
                self.starts.add(start)
                self.ends[start] = left
                self.covered_length += left - start
            if right < end:
                self.starts.add(right)
                self.ends[right] = end
                self.covered_length += end - right
        return removed

    erase = discard

    def contains(self, value):
        start = self.starts.le(value)
        return start is not None and value < self.ends[start]

    def mex(self, value=0):
        start = self.starts.le(value)
        if start is not None and value < self.ends[start]:
            return self.ends[start]
        return value

    def intervals(self):
        return [(start, self.ends[start]) for start in self.starts]

    def __len__(self):
        return len(self.starts)
