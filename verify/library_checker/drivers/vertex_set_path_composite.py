import sys

from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition
from library_codex.segment_tree.SegTree import SegTree


def compose(first, second):
    a, b = first
    c, d = second
    return a * c % 998244353, (b * c + d) % 998244353


def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n, q = next(data), next(data)
    values = [(next(data), next(data)) for _ in range(n)]
    graph = [[] for _ in range(n)]
    for _ in range(n - 1):
        u, v = next(data), next(data)
        graph[u].append(v)
        graph[v].append(u)
    tree = HeavyLightDecomposition(graph)
    ordered = [values[v] for v in tree.rev]
    forward = SegTree(compose, (1, 0), ordered)
    backward = SegTree(compose, (1, 0), ordered[::-1])
    answer = []
    for _ in range(q):
        if next(data) == 0:
            p, a, b = next(data), next(data), next(data)
            i = tree.tin[p]
            forward.set(i, (a, b))
            backward.set(n - 1 - i, (a, b))
        else:
            u, v, x = next(data), next(data), next(data)
            for l, r, reverse in tree.path_ordered(u, v):
                a, b = backward.prod(n - r, n - l) if reverse else forward.prod(l, r)
                x = (a * x + b) % 998244353
            answer.append(str(x))
    print("\n".join(answer))


if __name__ == "__main__":
    solve()
