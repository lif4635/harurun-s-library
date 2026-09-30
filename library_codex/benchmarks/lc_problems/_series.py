import random


MOD = 998244353


def coefficients(n, family, seed):
    rng = random.Random(seed)
    if family == "dense":
        return [rng.randrange(MOD) for _ in range(n)]
    a = [0] * n
    for i in (0, 1, n // 2, n - 1):
        if i < n:
            a[i] = rng.randrange(MOD)
    return a


def fps_case(n, family, seed, operation):
    a = coefficients(n, family, seed)
    a[0] = 0 if operation == "exp" else max(a[0], 1)
    expected = None
    if n <= 256:
        b = [1 if operation == "exp" else pow(a[0], MOD - 2, MOD)]
        for k in range(1, n):
            if operation == "exp":
                value = sum(i * a[i] * b[k - i] for i in range(1, k + 1)) * pow(k, MOD - 2, MOD)
            else:
                value = -sum(a[i] * b[k - i] for i in range(1, k + 1)) * b[0]
            b.append(value % MOD)
        expected = [str(x).encode() for x in b]
    return (str(n) + "\n" + " ".join(map(str, a)) + "\n").encode(), expected
