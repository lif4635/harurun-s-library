"""非負重みグラフの単一始点最短距離と直前頂点を求める。"""
import heapq
INF = float('inf')

def _shortest_path_dijkstra_edge(entry):
    if isinstance(entry, int):
        return (entry, 1)
    return (entry[0], entry[1])

def dijkstra(graph, start=0, goal=None):
    n = len(graph)
    distance = [INF] * n
    previous = [-1] * n
    distance[start] = 0
    heap = [(0, start)]
    while heap:
        (current, node) = heapq.heappop(heap)
        if current != distance[node]:
            continue
        if node == goal:
            break
        for entry in graph[node]:
            (other, weight) = _shortest_path_dijkstra_edge(entry)
            if weight < 0:
                raise ValueError('Dijkstra requires nonnegative weights')
            next_distance = current + weight
            if next_distance < distance[other]:
                distance[other] = next_distance
                previous[other] = node
                heapq.heappush(heap, (next_distance, other))
    return (distance, previous)
import sys
read = sys.stdin.buffer.readline
(n, m, start, goal) = map(int, read().split())
graph = [[] for _ in range(n)]
for _ in range(m):
    (u, v, weight) = map(int, read().split())
    graph[u].append((v, weight))
(distance, previous) = dijkstra(graph, start, goal)
if previous[goal] == -1:
    print(-1)
else:
    path = []
    vertex = goal
    while vertex != start:
        path.append((previous[vertex], vertex))
        vertex = previous[vertex]
    print(distance[goal], len(path))
    for (u, v) in reversed(path):
        print(u, v)
