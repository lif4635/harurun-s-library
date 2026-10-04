import sys

from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition
from library_codex.fenwick_tree.BIT import BIT


def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n, q = next(data), next(data)
    values = [next(data) for _ in range(n)]
    graph = [[] for _ in range(n)]
    for _ in range(n - 1):
        u, v = next(data), next(data)
        graph[u].append(v)
        graph[v].append(u)
    tree = HeavyLightDecomposition(graph)
    bit = BIT([values[v] for v in tree.rev])
    answer = []
    for _ in range(q):
        kind, u, v = next(data), next(data), next(data)
        if kind == 0:
            bit.add(tree.tin[u], v)
        else:
            answer.append(str(sum(bit.sum(l, r) for l, r in tree.path(u, v))))
    print("\n".join(answer))


if __name__ == "__main__":
    solve()
