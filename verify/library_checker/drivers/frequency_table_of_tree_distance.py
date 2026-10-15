import sys
from library_codex.tree.TreeDistanceFrequency import tree_distance_counts

input = sys.stdin.buffer.readline
n = int(input())
tree = [[] for _ in range(n)]
for _ in range(n - 1):
    u, v = map(int, input().split())
    tree[u].append(v)
    tree[v].append(u)
answer = tree_distance_counts(tree)
answer.extend([0] * (n - len(answer)))
print(*answer[1:])
