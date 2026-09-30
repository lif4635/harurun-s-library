import random


MODULE = "ordered_set/FastSet.py"
MAX_SIZE = 1000000
FAMILIES = ("random", "sparse")


def make_case(n, family, seed):
    rng = random.Random(seed)
    values = [int(rng.randrange(128 if family == "sparse" else 2) == 0) for _ in range(n)]
    lines = [f"{n} {n}", "".join(map(str, values))]
    expected = [] if n <= 256 else None
    for i in range(n):
        t = i % 5
        k = (0 if i % 2 else n - 1) if i % 13 == 0 else rng.randrange(n)
        lines.append(f"{t} {k}")
        if t < 2:
            values[k] = 1 - t
        elif expected is not None:
            if t == 2:
                answer = values[k]
            elif t == 3:
                answer = next((v for v in range(k, n) if values[v]), -1)
            else:
                answer = next((v for v in range(k, -1, -1) if values[v]), -1)
            expected.append(str(answer).encode())
    return ("\n".join(lines) + "\n").encode(), expected


def solve():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    initial = read().strip()
    tree = FastSet(n, (i for i, value in enumerate(initial) if value == 49))
    answer = []
    for _ in range(q):
        t, k = map(int, read().split())
        if t == 0:
            tree.add(k)
        elif t == 1:
            tree.discard(k)
        elif t == 2:
            answer.append(int(k in tree))
        elif t == 3:
            answer.append(tree.next(k))
        else:
            answer.append(tree.prev(k))
    print("\n".join(map(str, answer)))
