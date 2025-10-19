def GaussJordan_mod(a, mod, is_extended = False):
    """
    in-plece 掃き出し
    is_extended : 拡大係数行列かどうか
    
    行列の慣習に合わせて n, m が swap しています
    """
    n, m = len(a[0]), len(a)
    
    for i in range(m):
        for j in range(n):
            a[i][j] %= mod
    
    rank = 0
    for col in range(n - is_extended):
        for row in range(rank, m):
            if a[row][col] != 0:
                pivot = row
                break
        else:
            continue
        
        a[pivot], a[rank] = a[rank], a[pivot]
        
        inv = pow(a[rank][col], mod-2, mod)
        for i in range(n):
            if a[rank][i] != 0:
                a[rank][i] = a[rank][i] * inv % mod
        
        for row in range(m):
            if row != rank and a[row][col] != 0:
                coef = a[row][col]
                for i in range(n):
                    a[row][i] -= a[rank][i] * coef % mod
                    if a[row][i] < 0: a[row][i] += mod
        
        rank += 1
    return rank

def GaussJordan_xor(n, a, is_extended = False):
    """
    in-plece bit列での掃き出し
    n = 列数
    """
    m = len(a)
    rank = 0
    for col in reversed(range(is_extended, n)):
        for row in range(rank, m):
            if a[row] >> col & 1:
                pivot = row
                break
        else:
            continue
        a[pivot], a[rank] = a[rank], a[pivot]
        for row in range(m):
            if row != rank and a[row] >> col & 1:
                a[row] ^= a[rank]
        rank += 1
    return rank