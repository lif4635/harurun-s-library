import sys
from library_codex.graph_connectivity.ComplementGraph import complement_components

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
graph = [[] for _ in range(n)]
for _ in range(m):
    u, v = map(int, read().split())
    graph[u].append(v)
    graph[v].append(u)
groups = complement_components(graph)
print(len(groups))
for group in groups:
    print(len(group), *group)
