def primefact(n:int) -> dict[int,int]:
    p = 2
    res = dict()
    while p*p <= n:
        cnt = 0
        while n%p == 0:
            n //= p
            cnt += 1
        if cnt:
            res[p] = cnt
        p += 1
    if n != 1:
        res[n] = 1
    return res