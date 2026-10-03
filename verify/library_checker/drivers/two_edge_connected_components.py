import sys
from library_codex.graph_connectivity.TwoEdgeConnectedComponents import TwoEdgeConnectedComponents

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
edges = [tuple(map(int, read().split())) for _ in range(m)]
groups = TwoEdgeConnectedComponents(n, edges).groups
print(len(groups))
for group in groups:
    print(len(group), *group)
