"""辺重みが0または1のグラフの単一始点最短路を求める。"""

from collections import deque

INF = float("inf")

def _edge(entry):
    if isinstance(entry, int):
        return entry, 1
    return entry[0], entry[1]

def zero_one_bfs(graph, start=0):
    n = len(graph)
    distance = [INF] * n
    previous = [-1] * n
    distance[start] = 0
    queue = deque([start])
    while queue:
        node = queue.popleft()
        current = distance[node]
        for entry in graph[node]:
            other, weight = _edge(entry)
            if weight not in (0, 1):
                raise ValueError("edge weight must be 0 or 1")
            next_distance = current + weight
            if next_distance < distance[other]:
                distance[other] = next_distance
                previous[other] = node
                if weight:
                    queue.append(other)
                else:
                    queue.appendleft(other)
    return distance, previous

