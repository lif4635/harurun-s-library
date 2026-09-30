import random


MODULE = "fenwick_tree/BIT.py"
FAMILIES = ("random", "boundary")


def make_case(n, family, seed):
    rng = random.Random(seed)
    a = [rng.randrange(10**9) for _ in range(n)]
    lines = [f"{n} {n}", " ".join(map(str, a))]
    expected = [] if n <= 256 else None
    for i in range(n):
        if i % 2 == 0:
            p = (0 if i % 4 == 0 else n - 1) if family == "boundary" else rng.randrange(n)
            x = rng.randrange(10**9)
            lines.append(f"0 {p} {x}")
            if expected is not None:
                a[p] += x
        else:
            l = 0 if family == "boundary" else rng.randrange(n)
            r = (n if i % 4 == 1 else 1) if family == "boundary" else rng.randrange(l + 1, n + 1)
            lines.append(f"1 {l} {r}")
            if expected is not None:
                expected.append(str(sum(a[l:r])).encode())
    return ("\n".join(lines) + "\n").encode(), expected


def solve():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    bit = BIT(list(map(int, read().split())))
    answer = []
    for _ in range(q):
        t, x, y = map(int, read().split())
        if t == 0:
            bit.add(x, y)
        else:
            answer.append(bit.sum(x, y))
    print("\n".join(map(str, answer)))
