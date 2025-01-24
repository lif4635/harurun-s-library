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

def fastest_count_primes(n):
    if n < 2:
        return 0
    v = int(n ** 0.5) + 1
    smalls = [i // 2 for i in range(1, v + 1)]
    smalls[1] = 0
    s = v // 2
    roughs = [2 * i + 1 for i in range(s)]
    larges = [(n // (2 * i + 1) + 1) // 2 for i in range(s)]
    skip = [False] * v

    pc = 0
    for p in range(3, v):
        if smalls[p] <= smalls[p - 1]:
            continue
        else:
            print(p)
        
        q = p * p
        pc += 1 #n^(1/4)以下の素数の個数
        if q * q > n:
            break
        # 素数じゃないフラグ
        skip[p] = True
        for i in range(q, v, 2 * p):
            skip[i] = True
            
        ns = 0
        for k in range(s):
            i = roughs[k]
            if skip[i]:
                continue
            d = i * p
            larges[ns] = larges[k] - (larges[smalls[d] - pc] if d < v else smalls[n // d]) + pc
            roughs[ns] = i
            ns += 1
        print(roughs)
        
        # ふるわれる個数のけいさんがらくだね
        s = ns
        for j in range((v - 1) // p, p - 1, -1):
            c = smalls[j] - pc
            e = min((j + 1) * p, v)
            for i in range(j * p, e):
                smalls[i] -= c
                print(i,c)

    for k in range(1, s):
        m = n // roughs[k]
        s = larges[k] - (pc + k - 1)
        for l in range(1, k):
            p = roughs[l]
            if p * p > m:
                break
            s -= smalls[m // p] - (pc + l - 1)
        larges[0] -= s

    return larges[0]


fastest_count_primes(1000)