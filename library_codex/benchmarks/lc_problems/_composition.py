from library_codex.benchmarks.lc_problems._series import MOD, coefficients


def composition_case(n, family, seed):
    outer = coefficients(n, "dense", seed)
    inner = coefficients(n, "dense" if family == "dense" else "sparse", seed + 1)
    inner[0] = 0
    if family == "identity":
        inner = [0] * n
        if n > 1:
            inner[1] = 1
    expected = outer if family == "identity" else None
    if expected is None and n <= 256:
        result = [0] * n
        terms = [(j, value) for j, value in enumerate(inner) if value]
        for coefficient in reversed(outer):
            product = [0] * n
            for i, value in enumerate(result):
                if value:
                    for j, factor in terms:
                        if i + j >= n:
                            break
                        product[i + j] += value * factor
            result = [value % MOD for value in product]
            result[0] = coefficient
        expected = result
    data = str(n) + "\n" + " ".join(map(str, outer)) + "\n" + " ".join(map(str, inner)) + "\n"
    return data.encode(), None if expected is None else [str(value).encode() for value in expected]


def solve():
    n = int(sys.stdin.buffer.readline())
    outer = list(map(int, sys.stdin.buffer.readline().split()))
    inner = list(map(int, sys.stdin.buffer.readline().split()))
    print(" ".join(map(str, fps_compose(outer, inner, n))))


def solve_trimmed():
    n = int(sys.stdin.buffer.readline())
    outer = list(map(int, sys.stdin.buffer.readline().split()))
    inner = list(map(int, sys.stdin.buffer.readline().split()))
    while inner and inner[-1] == 0:
        inner.pop()
    print(" ".join(map(str, fps_compose(outer, inner, n))))
