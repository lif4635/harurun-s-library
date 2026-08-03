"""非負重みグラフの単一始点最短距離と直前頂点を求める。"""

import heapq

INF = float("inf")

def _edge(entry):
    if isinstance(entry, int):
        return entry, 1
    return entry[0], entry[1]

def dijkstra(graph, start=0, goal=None):
    n = len(graph)
    distance = [INF] * n
    previous = [-1] * n
    distance[start] = 0
    heap = [(0, start)]
    while heap:
        current, node = heapq.heappop(heap)
        if current != distance[node]:
            continue
        if node == goal:
            break
        for entry in graph[node]:
            other, weight = _edge(entry)
            if weight < 0:
                raise ValueError("Dijkstra requires nonnegative weights")
            next_distance = current + weight
            if next_distance < distance[other]:
                distance[other] = next_distance
                previous[other] = node
                heapq.heappush(heap, (next_distance, other))
    return distance, previous

