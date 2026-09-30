import random


MODULE = "tree/LCA.py"
MIN_SIZE = 2
FAMILIES = ("random", "chain", "star", "balanced")
VARIANTS = {"hld": ("tree/HeavyLightDecomposition.py", "solve_hld")}


def make_case(n, family, seed):
    rng = random.Random(seed)
    parent = [-1] + [rng.randrange(v) if family == "random" else v - 1 if family == "chain" else 0 if family == "star" else (v - 1) // 2 for v in range(1, n)]
    lines = [f"{n} {n}", " ".join(map(str, parent[1:]))]
    expected = [] if n <= 256 else None
    for i in range(n):
        u, v = (0, n - 1) if i % 17 == 0 else (rng.randrange(n), rng.randrange(n))
        lines.append(f"{u} {v}")
        if expected is not None:
            ancestors = set()
            while u >= 0:
                ancestors.add(u)
                u = parent[u]
            while v not in ancestors:
                v = parent[v]
            expected.append(str(v).encode())
    return ("\n".join(lines) + "\n").encode(), expected


def solve():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    parents = list(map(int, read().split()))
    tree = [[] for _ in range(n)]
    for v, p in enumerate(parents, 1):
        tree[v].append(p)
        tree[p].append(v)
    solver = LCA(tree)
    answer = []
    for _ in range(q):
        u, v = map(int, read().split())
        answer.append(solver(u, v))
    print("\n".join(map(str, answer)))


def solve_hld():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    parents = list(map(int, read().split()))
    tree = [[] for _ in range(n)]
    for v, p in enumerate(parents, 1):
        tree[v].append(p)
        tree[p].append(v)
    solver = HeavyLightDecomposition(tree)
    answer = []
    for _ in range(q):
        u, v = map(int, read().split())
        answer.append(solver.lca(u, v))
    print("\n".join(map(str, answer)))
