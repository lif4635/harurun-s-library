"""列の辞書順最小な巡回shiftをBooth法で求める。"""


def minimum_cyclic_shift(sequence):
    """辞書順最小なrotationの開始位置を返す。"""
    n = len(sequence)
    if n == 0:
        return 0
    i, j, offset = 0, 1, 0
    while i < n and j < n and offset < n:
        first = sequence[(i + offset) % n]
        second = sequence[(j + offset) % n]
        if first == second:
            offset += 1
            continue
        if first > second:
            i += offset + 1
            if i == j:
                i += 1
        else:
            j += offset + 1
            if i == j:
                j += 1
        offset = 0
    return min(i, j)
