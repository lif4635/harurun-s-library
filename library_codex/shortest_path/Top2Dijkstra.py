"""各頂点に最も近い異なる2個のsourceと距離を求める。"""

import heapq


INF = float("inf")


def _edge(entry):
    if isinstance(entry, int):
        return entry, 1
    return entry[0], entry[1]


def top2_dijkstra(graph, sources):
    """各頂点について距離が小さい順の異なる2始点を返す。"""
    n = len(graph)
    nearest = [[] for _ in range(n)]
    heap = []
    used_sources = set()
    for source in sources:
        if not 0 <= source < n:
            raise IndexError("a source is outside the graph")
        if source not in used_sources:
            used_sources.add(source)
            heapq.heappush(heap, (0, source, source))

    while heap:
        distance, source, vertex = heapq.heappop(heap)
        current = nearest[vertex]
        if any(label == source for _, label in current) or len(current) == 2:
            continue
        current.append((distance, source))
        for entry in graph[vertex]:
            to, weight = _edge(entry)
            if not 0 <= to < n:
                raise IndexError("an edge endpoint is outside the graph")
            if weight < 0:
                raise ValueError("top2_dijkstra requires nonnegative weights")
            heapq.heappush(heap, (distance + weight, source, to))

    missing = (INF, -1)
    return [
        (row[0] if row else missing, row[1] if len(row) == 2 else missing)
        for row in nearest
    ]
