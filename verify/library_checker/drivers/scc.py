import sys
from library_codex.graph_connectivity.StronglyConnectedComponents import scc

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
graph = [[] for _ in range(n)]
for _ in range(m):
    source, target = map(int, read().split())
    graph[source].append(target)
_, groups = scc(graph)
print(len(groups))
for group in groups:
    print(len(group), *group)
