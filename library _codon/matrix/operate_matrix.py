mod = 998244353

def mat_add(a, b):
    # assert len(a) == len(b)
    # assert len(a[0]) == len(b[0])
    n = len(a)
    m = len(a[0])
    res = [[0]*m for i in range(n)]
    for i in range(n):
        for j in range(m):
            res[i][j] = (a[i][j] + b[i][j])%mod
    return res

def mat_sub(a, b):
    # assert len(a) == len(b)
    # assert len(a[0]) == len(b[0])
    n = len(a)
    m = len(a[0])
    res = [[0]*m for i in range(n)]
    for i in range(n):
        for j in range(m):
            res[i][j] = (a[i][j] - b[i][j])%mod
    return res

def mat_mul(a, b):
    # assert len(a[0]) == len(b)
    n = len(a)
    m = len(b[0])
    res = [[0]*m for i in range(n)]
    for i,r_i in enumerate(res):
        for k,a_ik in enumerate(a[i]):
            for j,b_kj in enumerate(b[k]):
                r_i[j] = (r_i[j] + a_ik*b_kj)%mod
    return res

def mat_pow2(a):
    n = len(a)
    res = [[0]*n for i in range(n)]
    for i,r_i in enumerate(res):
        for k,a_ik in enumerate(a[i]):
            for j,a_kj in enumerate(a[k]):
                r_i[j] = (r_i[j] + a_ik*a_kj)%mod
    return res

def mat_inv(a, mod = mod):
    """いつか実装します"""
    pass

def mat_pow(a, exp):
    n = len(a)
    res = [[int(i == j) for j in range(n)] for i in range(n)]
    
    d = exp.bit_length()
    for i in range(d, -1, -1):
        if (exp >> i) & 1: res = mat_mul(res, a)
        if i == 0: return res
        res = mat_pow2(res)