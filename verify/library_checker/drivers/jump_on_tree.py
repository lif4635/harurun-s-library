import sys

from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition


def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n, q = next(data), next(data)
    graph = [[] for _ in range(n)]
    for _ in range(n - 1):
        u, v = next(data), next(data)
        graph[u].append(v)
        graph[v].append(u)
    tree = HeavyLightDecomposition(graph)
    answer = [str(tree.jump(next(data), next(data), next(data))) for _ in range(q)]
    print("\n".join(answer))


if __name__ == "__main__":
    solve()
