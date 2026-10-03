import sys
from library_codex.graph.EulerianTrail import eulerian_trail

read = sys.stdin.buffer.readline
for _ in range(int(read())):
    n, m = map(int, read().split())
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    result = eulerian_trail(n, edges)
    if result is None:
        print("No")
    else:
        print("Yes")
        print(*result[0])
        print(*result[1])
