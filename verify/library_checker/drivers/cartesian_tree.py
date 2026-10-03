import sys
from library_codex.sequence_structure.CartesianTree import cartesian_tree

read = sys.stdin.buffer.readline
n = int(read())
parent, left, right, root = cartesian_tree(list(map(int, read().split())))
parent[root] = root
print(*parent)
