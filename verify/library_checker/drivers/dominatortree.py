import sys
from library_codex.graph_connectivity.DominatorTree import dominator_tree

read = sys.stdin.buffer.readline
n, m, root = map(int, read().split())
graph = [[] for _ in range(n)]
for _ in range(m):
    u, v = map(int, read().split())
    graph[u].append(v)
print(*dominator_tree(graph, root))
