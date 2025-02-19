from math import isqrt

def pi_count(n):
    """
    LucyDP : O(n^(3/4)) 
    """
    Q_n = [0]
    i = n
    while i:
        Q_n.append(i)
        i = n//(n//i+1)
    
    Q_size = len(Q_n)
    sqrt = isqrt(n)
    def Q_idx(x):
        return Q_size-x if x <= sqrt else n//x
    
    dp = [i-1 for i in Q_n]
    prime = [1]*(sqrt+1)
    for p in range(2,sqrt+1):
        tmp = dp[Q_size+1-p]
        if prime[p]:
            for q in range(p*p,sqrt+1,p):
                prime[q] = 0
            for i,x in enumerate(Q_n):
                if i == 0: continue
                if x < p*p: break
                dp[i] -= dp[Q_idx(x//p)] - tmp
    return dp[1]