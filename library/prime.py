def primefact(n:int) -> dict[int,int]:
    p = 2
    res = dict()
    while p*p <= n:
        if n%p == 0:
            cnt = 0
            while n%p == 0:
                n //= p
                cnt += 1
            res[p] = cnt
        p += 1
    if n != 1:
        res[n] = 1
    return res

def prime_enumerate(lim:int, get:int = 0) -> list[int]:
    """
    get = 0 : enumerate
    get = 1 : flag
    """
    lim += 1
    prime_flag = [1]*lim
    prime_enu = []
    prime_flag[0] = 0
    prime_flag[1] = 0
    for p in range(2,lim):
        if prime_flag[p]:
            prime_enu.append(p)
            for q in range(2*p,lim,p):
                prime_flag[q] = 0
    if get == 0:
        return prime_enu
    else:
        return prime_flag  

def divisors(n:int) -> list[int]:
    divs_small, divs_big = [], []
    i = 1
    while i*i <= n:
        if n % i == 0:
            divs_small.append(i)
            if i != n//i:
                divs_big.append(n//i)
        i += 1
    return divs_small + divs_big[::-1]

def miller_rabin(num:int) -> bool:
    assert 1 <= num < (1 << 63) - 1
    if num == 1: return False
    elif num == 2: return True
    elif num % 2 == 0: return False
    
    d, s = num-1, 0
    while d&1 == 0:
        d >>= 1
        s += 1
    
    if num < 4759123141: tests = (2,7,61)
    else: tests = (2,325,9375,28178,450775,9780504,1795265022)
    
    for test in tests:
        if test >= num: continue
        if pow(test, d, num) == 1: continue
        if any(pow(test, d * 2**i, num) == num - 1 for i in range(s)): continue
        return False
    
    return True
