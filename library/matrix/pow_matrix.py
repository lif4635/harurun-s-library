def pow_matrix(mat, exp, mod = mod):
    N = len(mat)
    res = [[1 if i == j else 0 for i in range(N)] for j in range(N)]
    while exp > 0 :
        if exp&1: res = mul_matrix(res, mat, mod)
        mat = mul_matrix(mat, mat, mod)
        exp >>= 1
    return res
