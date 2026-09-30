import random


MODULE = "segment_tree/LazySegTree.py"
FAMILIES = ("random", "boundary")
VARIANTS = {"packed": (MODULE, "solve_packed")}


def make_case(n, family, seed):
    rng = random.Random(seed)
    mod = 998244353
    a = [rng.randrange(mod) for _ in range(n)]
    lines = [f"{n} {n}", " ".join(map(str, a))]
    expected = [] if n <= 256 else None
    for i in range(n):
        l = 0 if family == "boundary" else rng.randrange(n)
        r = (n if i % 4 < 2 else 1) if family == "boundary" else rng.randrange(l + 1, n + 1)
        if i % 2 == 0:
            b = (0, 1, mod - 1)[i % 3] if family == "boundary" else rng.randrange(mod)
            c = rng.randrange(mod)
            lines.append(f"0 {l} {r} {b} {c}")
            if expected is not None:
                for j in range(l, r):
                    a[j] = (a[j] * b + c) % mod
        else:
            lines.append(f"1 {l} {r}")
            if expected is not None:
                expected.append(str(sum(a[l:r]) % mod).encode())
    return ("\n".join(lines) + "\n").encode(), expected


def solve():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    mod = 998244353
    values = list(map(int, read().split()))
    tree = LazySegTree(
        lambda x, y: (x + y) % mod, 0,
        lambda f, x, length: (f[0] * x + f[1] * length) % mod,
        lambda f, g: (f[0] * g[0] % mod, (f[0] * g[1] + f[1]) % mod),
        (1, 0), values,
    )
    answer = []
    for _ in range(q):
        row = list(map(int, read().split()))
        if row[0] == 0:
            tree.apply(row[1], row[2], (row[3], row[4]))
        else:
            answer.append(tree.prod(row[1], row[2]))
    print("\n".join(map(str, answer)))


def solve_packed():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    mod = 998244353
    mask = (1 << 32) - 1
    values = list(map(int, read().split()))
    tree = LazySegTree(
        lambda x, y: (x + y) % mod, 0,
        lambda f, x, length: ((f >> 32) * x + (f & mask) * length) % mod,
        lambda f, g: ((((f >> 32) * (g >> 32) % mod) << 32)
            | (((f >> 32) * (g & mask) + (f & mask)) % mod)),
        1 << 32, values,
    )
    answer = []
    for _ in range(q):
        row = list(map(int, read().split()))
        if row[0] == 0:
            tree.apply(row[1], row[2], row[3] << 32 | row[4])
        else:
            answer.append(tree.prod(row[1], row[2]))
    print("\n".join(map(str, answer)))
