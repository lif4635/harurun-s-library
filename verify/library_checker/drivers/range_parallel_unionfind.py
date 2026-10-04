import sys

from library_codex.union_find.RangeParallelUnionFind import RangeParallelUnionFind


def solve():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    values = list(map(int, read().split()))
    union = RangeParallelUnionFind(n)
    total = 0

    def merged(root, old):
        nonlocal total
        total = (total + values[root] * values[old]) % 998244353
        values[root] = (values[root] + values[old]) % 998244353

    answer = []
    for _ in range(q):
        k, a, b = map(int, read().split())
        union.merge(a, b, k, merged)
        answer.append(str(total))
    print("\n".join(answer))


if __name__ == "__main__":
    solve()
