"""Maximum and minimum subarray sums under point updates.

``MaxInterval`` is the mergeable state for one interval: total sum, maximum
and minimum subarray sums, and the corresponding prefix/suffix sums.
``max_interval_segment_tree`` builds a SegmentTree so changing one value and
reading the whole array's best contiguous sum both take logarithmic time.
Empty subarrays are not selected for nonempty input intervals.
"""

from library_codex.segment_tree.SegmentTree import SegmentTree


class MaxInterval:
    __slots__ = (
        "sum", "maximum", "left_maximum", "right_maximum",
        "minimum", "left_minimum", "right_minimum", "length"
    )

    def __init__(self, value=0, length=0):
        self.length = length
        if length == 0:
            self.sum = 0
            self.maximum = 0
            self.left_maximum = 0
            self.right_maximum = 0
            self.minimum = 0
            self.left_minimum = 0
            self.right_minimum = 0
        else:
            total = value * length
            self.sum = total
            self.maximum = self.left_maximum = self.right_maximum = (
                total if value > 0 else value
            )
            self.minimum = self.left_minimum = self.right_minimum = (
                total if value < 0 else value
            )

    @classmethod
    def single(cls, value):
        return cls(value, 1)


def merge_max_interval(first, second):
    if first.length == 0:
        return second
    if second.length == 0:
        return first
    result = MaxInterval()
    result.length = first.length + second.length
    result.sum = first.sum + second.sum
    result.maximum = max(
        first.maximum,
        second.maximum,
        first.right_maximum + second.left_maximum,
    )
    result.left_maximum = max(
        first.left_maximum, first.sum + second.left_maximum
    )
    result.right_maximum = max(
        second.right_maximum, second.sum + first.right_maximum
    )
    result.minimum = min(
        first.minimum,
        second.minimum,
        first.right_minimum + second.left_minimum,
    )
    result.left_minimum = min(
        first.left_minimum, first.sum + second.left_minimum
    )
    result.right_minimum = min(
        second.right_minimum, second.sum + first.right_minimum
    )
    return result


def max_interval_segment_tree(values):
    return SegmentTree(
        merge_max_interval,
        MaxInterval(),
        [MaxInterval.single(value) for value in values],
    )
