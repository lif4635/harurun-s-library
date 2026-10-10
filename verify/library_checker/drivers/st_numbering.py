import sys

from library_codex.graph_connectivity.STNumbering import st_numbering


read = sys.stdin.buffer.readline
answers = []
for _ in range(int(read())):
    n, m, source, target = map(int, read().split())
    graph = [[] for _ in range(n)]
    for _ in range(m):
        u, v = map(int, read().split())
        graph[u].append(v)
        graph[v].append(u)
    rank = st_numbering(graph, source, target)
    if rank is None:
        answers.append("No")
    else:
        answers.extend(("Yes", " ".join(map(str, rank))))
sys.stdout.write("\n".join(answers) + "\n")
