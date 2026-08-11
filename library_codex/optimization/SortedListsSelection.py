"""複数の昇順listをmergeしたときの先頭k要素を、全体をmergeせず選ぶ。"""

import heapq


def _extend(rows, lengths, counts, k, shift):
    heap = []
    for row, count in enumerate(counts):
        index = ((count + 1) << shift) - 1
        if index < lengths[row]:
            heap.append((rows[row][index], row))
    heapq.heapify(heap)
    while k:
        _, row = heapq.heappop(heap)
        counts[row] += 1
        k -= 1
        if k:
            index = ((counts[row] + 1) << shift) - 1
            if index < lengths[row]:
                heapq.heappush(heap, (rows[row][index], row))
    return counts


def _take(rows, lengths, k):
    frames = []
    shift = 0
    while True:
        total = sum(length >> shift for length in lengths)
        if k == 0:
            counts = [0] * len(rows)
            break
        if k == total:
            counts = [length >> shift for length in lengths]
            break

        blocks = sum(length >= 1 << shift for length in lengths)
        if k <= blocks:
            counts = _extend(rows, lengths, [0] * len(rows), k, shift)
            break
        coarse = (k - blocks) >> 1
        frames.append((shift, k - (coarse << 1)))
        k = coarse
        shift += 1

    while frames:
        shift, remainder = frames.pop()
        for index in range(len(counts)):
            counts[index] <<= 1
        counts = _extend(rows, lengths, counts, remainder, shift)
    return counts


def take(rows, k):
    """全rowをstable mergeした先頭k要素が各rowから何個来るか返す。"""
    rows = list(rows)
    lengths = [len(row) for row in rows]
    total = sum(lengths)
    if not 0 <= k <= total:
        raise IndexError("k is outside the merged sequence")
    return _take(rows, lengths, k)


def kth(rows, k):
    """全rowをstable mergeした列のk番目の値を返す。"""
    rows = list(rows)
    total = sum(map(len, rows))
    if not 0 <= k < total:
        raise IndexError("k is outside the merged sequence")
    counts = _take(rows, [len(row) for row in rows], k + 1)
    return max(
        (rows[row][count - 1], row)
        for row, count in enumerate(counts)
        if count
    )[0]
