mod = 998244353

def mat_add(a, b, mod = mod):
    assert len(a) == len(b)
    assert len(a[0]) == len(b[0])
    n = len(a)
    m = len(a[0])
    res = [[0]*m for i in range(n)]
    for i in range(n):
        for j in range(m):
            res[i][j] = (a[i][j] + b[i][j])%mod
    return res

def mat_sub(a, b, mod = mod):
    assert len(a) == len(b)
    assert len(a[0]) == len(b[0])
    n = len(a)
    m = len(a[0])
    res = [[0]*m for i in range(n)]
    for i in range(n):
        for j in range(m):
            res[i][j] = (a[i][j] - b[i][j])%mod
    return res

def mat_mul(a, b, mod = mod):
    # assert len(a[0]) == len(b)
    res = [[0]*len(b[0]) for i in range(len(a))]
    for i,ri in enumerate(res):
        for k,aik in enumerate(a[i]):
            for j,bkj in enumerate(b[k]):
                ri[j] = (ri[j]+aik*bkj)%mod
    return res

def mat_inv(a, mod = mod):
    """いつか実装します"""
    pass

def mat_pow(a, exp, mod = mod):
    assert len(a) == len(a[0])
    n = len(a)
    res = [[1 if i == j else 0 for i in range(n)] for j in range(n)]
    while exp > 0:
        if exp&1: res = mat_mul(res, a, mod)
        a = mat_mul(a, a, mod)
        exp >>= 1
    return res
