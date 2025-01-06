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
