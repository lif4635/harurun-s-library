import sys
from library_codex.union_find.PersistentUnionFind import PersistentUnionFind


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    tree = PersistentUnionFind(n)
    versions = [0] * (q + 1)
    answer = []
    for i in range(q):
        kind, version, u, v = map(int, read().split())
        if kind == 0:
            versions[i + 1] = tree.unite(u, v, versions[version + 1])
        else:
            answer.append(str(int(tree.same(u, v, versions[version + 1]))))
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
