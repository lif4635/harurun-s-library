import sys

from library_codex.graph_spanning.MinimumSpanningTree import manhattan_mst


read = sys.stdin.buffer.readline
n = int(read())
points = [tuple(map(int, read().split())) for _ in range(n)]
cost, pairs = manhattan_mst(points)
print(cost)
sys.stdout.write("\n".join(f"{u} {v}" for u, v in pairs) + "\n")
