def chromatic_number(edge):
    n = len(edge)
    e = [0] * n
    for u in range(n):
        for v in edge[u]:
            e[u] += 1 << v
    
    dp = [0] * (1 << n)
    dp[0] = 1
    for bit in range(1, 1 << n):
        u = (~bit & (bit - 1)).bit_count()
        msb = 1 << u
        dp[bit] = dp[bit ^ msb] + dp[(bit ^ msb) & (~e[u])]
    
    cnt = [0] * (1 << n)
    sgn = [1, -1]
    for bit in range(1 << n):
        cnt[bit] = sgn[(n - bit.bit_count()) & 1]
    
    for k in range(1, n):
        tmp = 0
        for bit in range(1 << n):
            cnt[bit] *= dp[bit]
            tmp += cnt[bit]
        if tmp != 0:
            return k
    else:
        return n