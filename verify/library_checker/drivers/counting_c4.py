import sys

from library_codex.graph_enumeration.CountC4PerEdge import count_c4_per_edge


read = sys.stdin.buffer.readline
n, m = map(int, read().split())
edges = [tuple(map(int, read().split())) for _ in range(m)]
print(*count_c4_per_edge(n, edges))
