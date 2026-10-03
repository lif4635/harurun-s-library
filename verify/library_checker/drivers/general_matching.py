import sys
from library_codex.graph_matching.GeneralMatching import GeneralMatching

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
graph = [[] for _ in range(n)]
for _ in range(m):
    u, v = map(int, read().split())
    graph[u].append(v)
    graph[v].append(u)
matching = GeneralMatching(graph)
print(matching.matching_size)
for u, v in enumerate(matching.mate):
    if u < v:
        print(u, v)
