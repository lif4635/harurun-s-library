import sys
from library_codex.tree.TreeDiameter import tree_diameter

read = sys.stdin.buffer.readline
n = int(read())
tree = [[] for _ in range(n)]
for _ in range(n - 1):
    u, v, weight = map(int, read().split())
    tree[u].append((v, weight))
    tree[v].append((u, weight))
distance, path = tree_diameter(tree)
print(distance, len(path))
print(*path)
