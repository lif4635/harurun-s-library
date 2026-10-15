import sys
from library_codex.graph_spanning.MinimumCostArborescence import minimum_cost_arborescence

data = list(map(int, sys.stdin.buffer.read().split()))
n, m, root = data[:3]
edges = list(zip(data[3::3], data[4::3], data[5::3]))
cost, selected = minimum_cost_arborescence(n, root, edges)
parent = [root] * n
for edge_id in selected:
    source, target, _ = edges[edge_id]
    parent[target] = source
print(cost)
print(*parent)
