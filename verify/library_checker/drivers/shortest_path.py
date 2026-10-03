import sys
from library_codex.shortest_path.Dijkstra import dijkstra

read = sys.stdin.buffer.readline
n, m, start, goal = map(int, read().split())
graph = [[] for _ in range(n)]
for _ in range(m):
    u, v, weight = map(int, read().split())
    graph[u].append((v, weight))
distance, previous = dijkstra(graph, start, goal)
if previous[goal] == -1:
    print(-1)
else:
    path = []
    vertex = goal
    while vertex != start:
        path.append((previous[vertex], vertex))
        vertex = previous[vertex]
    print(distance[goal], len(path))
    for u, v in reversed(path):
        print(u, v)
