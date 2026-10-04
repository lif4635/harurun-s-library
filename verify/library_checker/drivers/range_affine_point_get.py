import sys

from library_codex.segment_tree.DualSegTree import DualSegTree


def mapping(action, value):
    a, b = action
    return (a * value + b) % 998244353


def composition(new, old):
    a, b = new
    c, d = old
    return a * c % 998244353, (a * d + b) % 998244353


def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n, q = next(data), next(data)
    tree = DualSegTree(mapping, composition, (1, 0), [next(data) for _ in range(n)])
    answer = []
    for _ in range(q):
        if next(data) == 0:
            l, r, a, b = next(data), next(data), next(data), next(data)
            tree.apply(l, r, (a, b))
        else:
            answer.append(str(tree.get(next(data))))
    print("\n".join(answer))


if __name__ == "__main__":
    solve()
