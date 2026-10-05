import sys

from library_codex.union_find.PotentialUnionFind import PotentialUnionFind


def op(a, b):
    mod = 998244353
    return ((a[0] * b[0] + a[1] * b[2]) % mod,
            (a[0] * b[1] + a[1] * b[3]) % mod,
            (a[2] * b[0] + a[3] * b[2]) % mod,
            (a[2] * b[1] + a[3] * b[3]) % mod)


def inv(a):
    return a[3], -a[1] % 998244353, -a[2] % 998244353, a[0]


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    tree = PotentialUnionFind(n, op, inv, (1, 0, 0, 1))
    result = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            result.append("1" if tree.merge(query[2], query[1], tuple(query[3:])) else "0")
        else:
            value = tree.diff(query[2], query[1])
            result.append("-1" if value is None else " ".join(map(str, value)))
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
