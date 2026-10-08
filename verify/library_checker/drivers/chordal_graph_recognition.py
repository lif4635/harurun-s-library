import sys

from library_codex.graph_enumeration.GraphProperties import ChordalGraphRecognizer


read = sys.stdin.buffer.readline
n, m = map(int, read().split())
graph = [[] for _ in range(n)]
for _ in range(m):
    u, v = map(int, read().split())
    graph[u].append(v)
    graph[v].append(u)
recognizer = ChordalGraphRecognizer(graph)
del graph
if recognizer.is_chordal():
    print('YES')
    print(*recognizer.perfect_elimination_order())
else:
    cycle = recognizer.induced_cycle()
    print('NO')
    print(len(cycle))
    print(*cycle)
