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

def primefact(n):
    result = dict()
    for p in range(2, 500):
        if p * p > n:
            break
        if n % p == 0:
            c = 0
            while n%p == 0:
                n //= p
                c += 1
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