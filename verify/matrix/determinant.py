mod = 998244353
def determinant(a, mod = mod):
    # assert len(a) == len(a[0])
    n = len(a)
    res = 1
    for i in range(n):
        for j in range(i,n):
            if a[j][i] == 0: continue
            if i != j:
                a[i],a[j] = a[j],a[i]
                res *= -1
            break
        else:
            # det = 0
            return 0
        
        res *= a[i][i]
        res %= mod
        # det != 0
        if a[i][i]%mod == 0: return 0
        
        inv = pow(a[i][i],-1,mod)
        for j in range(n):
            a[i][j] *= inv
            a[i][j] %= mod
        for j in range(i+1,n):
            tmp = a[j][i]
            for k in range(n):
                a[j][k] -= a[i][k]*tmp
                a[j][k] %= mod
    return res%mod

n = int(input())
mat = [[int(x) for x in input().split()] for i in range(n)]
print(determinant(mat))