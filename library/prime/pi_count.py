import math

def pi_count(n):
    """
    LucyDP : O(n^(3/4)) 
    """
    sqrtn = math.isqrt(n)
    q = [n//i for i in range(1,sqrtn+1)]
    q += [*range(q[-1]-1,0,-1)]
    s = {i:i-1 for i in q}
    
    for x in range(2,sqrtn+1):
        if s[x] > s[x-1]:
            for m in q:
                if m < x*x: break
                s[m] -= s[m//x] - s[x-1]
    return s[n]
