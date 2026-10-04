import sys

from library_codex.tree.TreeIsomorphism import RootedTreeIsomorphism


def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n = next(data)
    graph = [[] for _ in range(n)]
    for v in range(1, n):
        p = next(data)
        graph[p].append(v)
        graph[v].append(p)
    tree = RootedTreeIsomorphism(graph)
    print(tree.num_classes)
    print(*tree.class_id)


if __name__ == "__main__":
    solve()
