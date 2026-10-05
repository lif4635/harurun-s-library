import sys

from library_codex.union_find.PotentialUnionFind import PotentialUnionFind


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    mod = 998244353
    tree = PotentialUnionFind(n, lambda a, b: (a + b) % mod, lambda a: -a % mod, 0)
    result = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            result.append("1" if tree.merge(query[2], query[1], query[3]) else "0")
        else:
            value = tree.diff(query[2], query[1])
            result.append("-1" if value is None else str(value))
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
