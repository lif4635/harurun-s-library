def Lagrange(f:list, t:int, mod:int = mod):
    """
    k次多項式の
    f(0)~f(k)を与えられた時
    f(t)を求める
    """
    k = len(f) - 1
    if t <= k:
        return f[t]
    
    top1 = [1]*(k+1)
    top2 = [1]*(k+1)

    for i in range(k):
        top1[i+1] = top1[i]*(t-i)%mod
    for i in range(k,0,-1):
        top2[i-1] = top2[i]*(i-t)%mod
    
    finv = [0]*(k+1)
    inv = 1
    for i in range(2,k+1):
        inv *= i
        inv %= mod
    finv[k] = pow(inv,-1,mod)
    for i in range(k,0,-1):
        finv[i-1] = finv[i]*i%mod
    
    res = 0
    for i in range(k+1):
        tmp = f[i]*top1[i]%mod*top2[i]%mod*finv[i]%mod*finv[k-i]%mod
        res += tmp
        res %= mod
    return res
