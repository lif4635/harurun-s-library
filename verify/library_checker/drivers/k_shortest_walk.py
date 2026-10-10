import sys

from library_codex.shortest_path.KShortestWalks import k_shortest_walks


read = sys.stdin.buffer.readline
n, m, source, target, k = map(int, read().split())
edges = [tuple(map(int, read().split())) for _ in range(m)]
answer = k_shortest_walks(n, edges, source, target, k)
sys.stdout.write("\n".join(map(str, answer + [-1] * (k - len(answer)))) + "\n")
