def floor_sum(n, m, a, b):
    res = 0
    while n:
        if a < 0 or m <= a:
            k, a = divmod(a, m)
            res += n*(n-1) * k >> 1
        if b < 0 or m <= b:
            k, b = divmod(b, m)
            res += n * k
        n, b = divmod(a*n+b, m)
        a, m = m, a
    return res