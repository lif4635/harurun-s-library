def floor_sum(n, m, a, b):
    """
    sum_{0 <= i <= n - 1} floor(a * i + b / m)
    """
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

# https://qiita.com/sounansya/items/51b39e0d7bf5cc194081
def floor_sum_pq(n, m, a, b):
    """
    (p, q) = (0, 1), (0, 2), (1, 1) 
    """
    if m == 0:
        return 0, 0, 0
    a1, a2 = divmod(a, m)
    b1, b2 = divmod(b, m)
    y = (a2 * n + b2) // m
    s01, s02, s11 = floor_sum_pq(y, a2, m, m + a2 - b2 - 1)
    nn = n * (n - 1) // 2
    r01 = n * y - s01
    r02 = n * y * y - s01 - 2 * s11
    r11 = nn * y + (s01 - s02) // 2
    r02 += n * (2 * n - 1) * (n - 1) * a1 * a1 // 6
    r02 += 2 * nn * a1 * b1
    r02 += b1 * b1 * n
    r02 += 2 * a1 * r11
    r02 += 2 * b1 * r01
    r01 += a1 * nn + b1 * n
    r11 += nn * (a1 * (2 * n - 1) + 3 * b1) // 3
    return r01, r02, r11