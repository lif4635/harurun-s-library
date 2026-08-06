"""Ordering, compression, and interval operations for sequences."""

from bisect import bisect_left, bisect_right


def inversion_count(values):
    """Count pairs i < j with values[i] > values[j]."""
    values = list(values)
    compressed = {value: i for i, value in enumerate(sorted(set(values)))}
    bit = [0] * (len(compressed) + 1)
    answer = 0
    for seen, value in enumerate(values):
        index = compressed[value] + 1
        prefix = 0
        i = index
        while i:
            prefix += bit[i]
            i &= i - 1
        answer += seen - prefix
        i = index
        while i < len(bit):
            bit[i] += 1
            i += i & -i
    return answer


def lis(values, strict=True, restore=False):
    """Return LIS length, or ``(length, indices, subsequence)``."""
    values = list(values)
    tails = []
    tail_index = []
    parent = [-1] * len(values)
    search = bisect_left if strict else bisect_right
    for index, value in enumerate(values):
        position = search(tails, value)
        if position:
            parent[index] = tail_index[position - 1]
        if position == len(tails):
            tails.append(value)
            tail_index.append(index)
        else:
            tails[position] = value
            tail_index[position] = index
    if not restore:
        return len(tails)
    indices = []
    index = tail_index[-1] if tail_index else -1
    while index >= 0:
        indices.append(index)
        index = parent[index]
    indices.reverse()
    return len(tails), indices, [values[index] for index in indices]


def coordinate_compress(values):
    """Return sorted unique values and their 0-indexed ranks."""
    ordered = sorted(set(values))
    mapping = {value: i for i, value in enumerate(ordered)}
    return ordered, mapping


def merge_intervals(intervals, merge_adjacent=True):
    """Merge overlapping intervals and optionally touching intervals."""
    intervals = sorted(intervals)
    result = []
    for left, right in intervals:
        if left > right:
            raise ValueError("interval endpoints are reversed")
        separated = result and (
            left > result[-1][1] if merge_adjacent else left >= result[-1][1]
        )
        if not result or separated:
            result.append([left, right])
        elif right > result[-1][1]:
            result[-1][1] = right
    return [tuple(interval) for interval in result]
