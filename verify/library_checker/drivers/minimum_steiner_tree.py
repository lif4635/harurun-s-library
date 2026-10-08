import sys

from library_codex.graph_spanning.MinimumSteinerTree import minimum_steiner_tree


data = iter(map(int, sys.stdin.buffer.read().split()))
n, m = next(data), next(data)
edges = [(next(data), next(data), next(data)) for _ in range(m)]
k = next(data)
terminals = [next(data) for _ in range(k)]
cost, selected = minimum_steiner_tree(n, edges, terminals)
print(cost, len(selected))
print(*selected)
