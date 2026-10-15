MOD = 998244353
def lagrange_poly(xs, ys):
    """
    f(x_i) = y_i となる k 次多項式
    """
    n = len(xs) - 1
    dp = [0] * (n + 3)
    dp[0] = 1
    for i in range(n + 1):
        for j in range(n + 1, -1, -1):
            dp[j] = (dp[j] * -xs[i] + dp[j-1]) % MOD
    
    res = [0] * (n + 1)
    for i in range(n + 1):
        d = 1
        for j in range(n + 1):
            if i != j:
                d = d * (xs[i] - xs[j]) % MOD
        coef = ys[i] * pow(d, -1, MOD)
        if xs[i] == 0:
            for j in range(n + 1):
                res[j] = (res[j] + dp[j+1] * coef) % MOD
        else:
            inv = pow(-xs[i], -1, MOD)
            cur = 0
            for j in range(n + 1):
                cur = (dp[j] - cur) * inv % MOD
                res[j] = (res[j] + cur * coef) % MOD
    return res
