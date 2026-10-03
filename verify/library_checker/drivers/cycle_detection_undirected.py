import sys
from library_codex.graph.CycleDetection import find_cycle

read = sys.stdin.buffer.readline
n, m = map(int, read().split())
edges = [tuple(map(int, read().split())) for _ in range(m)]
vertices, cycle = find_cycle(n, edges, directed=False)
if cycle:
    print(len(cycle))
    print(*vertices)
    print(*cycle)
else:
    print(-1)
