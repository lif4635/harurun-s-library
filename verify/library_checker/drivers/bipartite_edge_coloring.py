import sys

from library_codex.graph_matching.BipartiteEdgeColoring import bipartite_edge_coloring

data = list(map(int, sys.stdin.buffer.read().split()))
left_size, right_size, m = data[:3]
edges = list(zip(data[3::2], data[4::2]))
colors = bipartite_edge_coloring(left_size, right_size, edges)
print(max(colors, default=-1) + 1)
sys.stdout.write("\n".join(map(str, colors)))
