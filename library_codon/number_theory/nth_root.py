def nth_root(x:int, n:int, is_64bit = True) -> int:
    """
    floor(x^(1/n))
    """
    ngs = [-1, -1, 4294967296, 2642246, 65536, 7132, 1626, 566, 256, 139, 85, 57, 41, 31, 24, 20, 16, 14, 12, 11, 10, 9, 8, 7, 7, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    if x <= 1 or n == 1:
        return x
    if is_64bit:
        if n >= 64: return 1
        ng = ngs[n]
    else:
        ng = x
    
    ok = 0
    while abs(ok - ng) > 1:
        mid = (ok + ng)//2
        if mid**n <= x:
            ok = mid
        else:
            ng = mid
    return ok    