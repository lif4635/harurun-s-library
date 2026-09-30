import random


MODULE = "union_find/UnionFind.py"
MAX_SIZE = 200000
FAMILIES = ("random", "chain")


def make_case(n, family, seed):
    rng = random.Random(seed)
    labels = list(range(n)) if n <= 256 else None
    expected = [] if labels is not None else None
    lines = [f"{n} {n}"]
    for i in range(n):
        t = i % 2
        u, v = (i // 2, min(i // 2 + 1, n - 1)) if family == "chain" and t == 0 else (rng.randrange(n), rng.randrange(n))
        lines.append(f"{t} {u} {v}")
        if labels is not None:
            if t == 0:
                old, new = labels[v], labels[u]
                labels = [new if label == old else label for label in labels]
            else:
                expected.append(str(int(labels[u] == labels[v])).encode())
    return ("\n".join(lines) + "\n").encode(), expected


def solve():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    uf = UnionFind(n)
    answer = []
    for _ in range(q):
        t, u, v = map(int, read().split())
        if t == 0:
            uf.merge(u, v)
        else:
            answer.append(int(uf.same(u, v)))
    print("\n".join(map(str, answer)))
