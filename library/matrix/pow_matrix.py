mod = 998244353

def mul_matrix(A, B, mod = mod):
    N, K, M = len(A), len(A[0]), len(B[0])
    assert K == len(B)
    
    res = [[0 for _ in range(M)] for _ in range(N)]
    for i in range(N) :
        for j in range(K) :
            for k in range(M) :
                res[i][k] += A[i][j] * B[j][k] 
                res[i][k] %= mod
    return res

def pow_matrix(mat, exp, mod = mod):
    N = len(mat)
    res = [[1 if i == j else 0 for i in range(N)] for j in range(N)]
    while exp > 0 :
        if exp&1: res = mul_matrix(res, mat, mod)
        mat = mul_matrix(mat, mat, mod)
        exp >>= 1
    return res
