import sys

from library_codex.graph_enumeration.MaximumIndependentSet import maximum_independent_set


data = iter(map(int, sys.stdin.buffer.read().split()))
n, m = next(data), next(data)
graph = [[] for _ in range(n)]
for _ in range(m):
    u, v = next(data), next(data)
    graph[u].append(v)
    graph[v].append(u)
answer = maximum_independent_set(graph)
print(len(answer))
print(*answer)
