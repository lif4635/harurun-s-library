import sys
from library_codex.graph_matching.BipartiteMatching import BipartiteMatching

read = sys.stdin.buffer.readline
left, right, m = map(int, read().split())
matching = BipartiteMatching(left, right)
for _ in range(m):
    matching.add_edge(*map(int, read().split()))
matching.solve()
print(matching.matching_size)
for u, v in enumerate(matching.match_left):
    if v != -1:
        print(u, v)
