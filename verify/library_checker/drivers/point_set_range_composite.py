import sys

from library_codex.segment_tree.SegTree import SegTree


def compose(first, second):
    a, b = first
    c, d = second
    return a * c % 998244353, (b * c + d) % 998244353


def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n, q = next(data), next(data)
    tree = SegTree(compose, (1, 0), [(next(data), next(data)) for _ in range(n)])
    answer = []
    for _ in range(q):
        kind, x, y, z = next(data), next(data), next(data), next(data)
        if kind == 0:
            tree.set(x, (y, z))
        else:
            a, b = tree.prod(x, y)
            answer.append(str((a * z + b) % 998244353))
    print("\n".join(answer))


if __name__ == "__main__":
    solve()
