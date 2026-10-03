import sys
from library_codex.graph_spanning.MinimumSpanningTree import minimum_spanning_tree

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
edges = [tuple(map(int, read().split())) for _ in range(m)]
cost, selected = minimum_spanning_tree(n, edges)
print(cost)
print(*selected)
