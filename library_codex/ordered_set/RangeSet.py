"""整数集合を互いに交わらない半開区間 $[left, right)$ で保持する。"""

from library_codex.ordered_set.TreapSet import TreapSet

class RangeSet:
    """A set of integers stored as disjoint half-open intervals."""
    __slots__ = ("starts", "ends", "covered_length")

    def __init__(self):
        self.starts = TreapSet()
        self.ends = {}
        self.covered_length = 0

    def add(self, left, right):
        """Add every integer in the half-open interval [left, right)."""
        if left >= right:
            return 0
        starts = self.starts
        ends = self.ends
        previously_covered = 0
        start = starts.le(left)
        if start is not None and ends[start] >= left:
            left = start
            right = max(right, ends[start])
            length = ends.pop(start) - start
            previously_covered += length
            self.covered_length -= length
            starts.discard(start)
        start = starts.ge(left)
        while start is not None and start <= right:
            right = max(right, ends[start])
            length = ends.pop(start) - start
            previously_covered += length
            self.covered_length -= length
            starts.discard(start)
            start = starts.ge(left)
        starts.add(left)
        ends[left] = right
        merged_length = right - left
        self.covered_length += merged_length
        return merged_length - previously_covered

    def discard(self, left, right):
        """Remove every integer in the half-open interval [left, right)."""
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
        """Return whether value belongs to one of the stored intervals."""
        start = self.starts.le(value)
        return start is not None and value < self.ends[start]

    def mex(self, value=0):
        """Return the smallest integer at least value that is not stored."""
        start = self.starts.le(value)
        if start is not None and value < self.ends[start]:
            return self.ends[start]
        return value

    def intervals(self):
        """Return disjoint half-open intervals [left, right) by left endpoint."""
        return [(start, self.ends[start]) for start in self.starts]

    def __len__(self):
        """Return the number of disjoint intervals, not covered integers."""
        return len(self.starts)
