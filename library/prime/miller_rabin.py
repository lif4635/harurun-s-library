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
