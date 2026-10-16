import sys

from library_codex.graph_spanning.MinimumDiameterSpanningTree import minimum_diameter_spanning_tree

data = list(map(int, sys.stdin.buffer.read().split()))
n, m = data[:2]
edges = [tuple(data[i:i + 3]) for i in range(2, len(data), 3)]
diameter, selected = minimum_diameter_spanning_tree(n, edges)
print(diameter)
print(*selected)
