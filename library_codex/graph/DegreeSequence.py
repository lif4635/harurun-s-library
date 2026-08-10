"""次数列が単純無向グラフとして実現可能か判定し、辺を構成する。"""

import heapq


def is_graphical(degrees):
    """degreesを次数列にもつ単純無向グラフが存在するか返す。"""
    degree = list(degrees)
    n = len(degree)
    counts = [0] * n
    total_degree = 0
    for value in degree:
        if value < 0 or value >= n:
            return False
        counts[value] += 1
        total_degree += value
    if total_degree & 1:
        return False
    degree = []
    for value in range(n - 1, -1, -1):
        degree.extend([value] * counts[value])
    prefix = [0] * (n + 1)
    for index, value in enumerate(degree):
        prefix[index + 1] = prefix[index] + value

    boundary = 0
    total = prefix[n]
    for size in range(n, 0, -1):
        while boundary < n and degree[boundary] >= size:
            boundary += 1
        if boundary < size:
            right = size * (size - 1) + total - prefix[size]
        else:
            right = (
                size * (size - 1)
                + (boundary - size) * size
                + total - prefix[boundary]
            )
        if prefix[size] > right:
            return False
    return True


def realize(degrees):
    """degreesを実現する単純無向グラフの辺listを返す。"""
    degree = list(degrees)
    if not is_graphical(degree):
        return None
    heap = [(-value, vertex) for vertex, value in enumerate(degree) if value]
    heapq.heapify(heap)
    edges = []
    while heap:
        negative, vertex = heapq.heappop(heap)
        need = -negative
        selected = []
        if need > len(heap):
            return None
        for _ in range(need):
            other_negative, other = heapq.heappop(heap)
            edges.append((vertex, other))
            other_negative += 1
            if other_negative:
                selected.append((other_negative, other))
        for entry in selected:
            heapq.heappush(heap, entry)
    return edges
