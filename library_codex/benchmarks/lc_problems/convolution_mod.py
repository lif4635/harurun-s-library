from library_codex.benchmarks.lc_problems._series import MOD, coefficients


MODULE = "convolution/NTT998.py"
MAX_SIZE = 524288
FAMILIES = ("dense", "sparse", "unbalanced")


def make_case(n, family, seed):
    m = min(n, 7) if family == "unbalanced" else n
    a = coefficients(n, "dense" if family == "unbalanced" else family, seed)
    b = coefficients(m, "dense" if family == "unbalanced" else family, seed + 1)
    expected = None
    if n <= 256:
        c = [0] * (n + m - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                c[i + j] = (c[i + j] + x * y) % MOD
        expected = [str(x).encode() for x in c]
    return (f"{n} {m}\n" + " ".join(map(str, a)) + "\n" + " ".join(map(str, b)) + "\n").encode(), expected


def solve():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    a = list(map(int, read().split()))
    b = list(map(int, read().split()))
    print(" ".join(map(str, multiply(a, b))))
