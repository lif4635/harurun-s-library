"""重みなしグラフの単一始点最短距離と直前頂点を求める。"""

from collections import deque

def bfs(graph, start=0, goal=None):
    n = len(graph)
    distance = [-1] * n
    previous = [-1] * n
    distance[start] = 0
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            break
        next_distance = distance[node] + 1
        for entry in graph[node]:
            other = entry if isinstance(entry, int) else entry[0]
            if distance[other] < 0:
                distance[other] = next_distance
                previous[other] = node
                queue.append(other)
    return distance, previous

