from math import isqrt
from random import randint

def gcd(x, y):
    """ x < y """
    while y:
        x, y = y, x%y
    return x

def is_prime(num):
    """ 1 <= x < 1<<64 """
    if num < 4: return num > 1
    if not num&1: return False
    
    d, s = num-1, 0
    while not d&1:
        d >>= 1
        s += 1
        
    tests = (2,7,61) if num < 4759123141 else (2,325,9375,28178,450775,9780504,1795265022)
        
    for test in tests:
        if test >= num: return True
        t = pow(test, d, num)
        if 1 < t < num-1:
            for _ in range(s-1):
                t = t*t%num
                if t == num-1: break
            else:
                return False
    return True

def find_prime(n):
    b = n.bit_length() - 1
    b = (b >> 2) << 2
    m = (1 << (b >> 3)) << 1
    while True:
        c = randint(1, n - 1)
        y = 0
        g = q = r = 1
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = gcd(q, n)
                k += m
            r <<= 1
        if g == n:
            g = 1
            y = ys
            while g == 1:
                y = (y * y + c) % n
                g = gcd(abs(x - y), n)
        if g == n:
            continue
        if is_prime(g):
            return g
        elif is_prime(n // g):
            return n // g
        else:
            n = g

def _primefactor(n):
    result = []
    for p in range(2, 500):
        if p * p > n:
            break
        c = 0
        while n%p == 0:
            n //= p
            c += 1
        if c:
            result.append(p)
    
    while n > 1 and not is_prime(n):
        p = find_prime(n)
        while n % p == 0:
            n //= p
        result.append(p)
    if n > 1: result.append(p)
    return result

def primefact(n, deduplicate = True):
    if deduplicate == False:
        return _primefactor(n)
    result = dict()
    for p in range(2, 500):
        if p * p > n:
            break
        c = 0
        while n%p == 0:
            n //= p
            c += 1
        if c:
            result[p] = c
    
    while n > 1 and not is_prime(n):
        p = find_prime(n)
        c = 0
        while n % p == 0:
            n //= p
            c += 1
        result[p] = c
    if n > 1: result[n] = 1
    return result

def divisors_naive(n):
    divs_small, divs_big = [], []
    i = 1
    while i*i <= n:
        if n % i == 0:
            divs_small.append(i)
            if i != n//i:
                divs_big.append(n//i)
        i += 1
    return divs_small + divs_big[::-1]

def divisors(n):
    if n == 1: return [1]
    if n <= 100_000_000: # 10 ** 8
        return divisors_naive(n)
    
    pf = primefact(n)
    ps = list(pf.keys())
    es = list(pf.values())
    us = [p ** e for p,e in zip(ps, es)]
    
    l = len(es)
    nes = [0] * (l + 1)
    r = 1
    res = [1]
    while True:
        nes[0] += 1
        for i in range(l):
            if nes[i] > es[i]:
                if i+1 == l:
                    res.sort()
                    return res
                nes[i] = 0
                nes[i+1] += 1
                r //= us[i]
            else:
                r *= ps[i]
                break
        res.append(r)
        
def totient(n):
    """
    totient(n) = #{ m | (m,n) = 1, 1 <= m <= n }
    """
    pf = _primefactor(n)
    for p in pf:
        n //= p
        n *= p - 1
    return n

def mobius(n):
    pf = primefact(n)
    r = 1
    for p,e in pf.items():
        if e >= 2: return 0
        r *= -1
    return r

def primitive_root(p):
    """ p : prime """
    if p == 2: return 1
    
    r = p - 1
    tests = []
    for q in range(2, 500):
        if q * q > r:
            break
        if r % q == 0:
            while r % q == 0:
                r //= q
            tests.append((p - 1) // q)
    
    while r > 1 and not is_prime(r):
        q = find_prime(r)
        while r % q == 0:
            r //= q
        tests.append((p - 1) // q)
    if r > 1: tests.append((p - 1) // r)
    
    res = 2
    while True:
        for test in tests:
            if pow(res, test, p) == 1:
                break
        else:
            return res
        res = randint(3, p - 2)