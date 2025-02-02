def miller_rabin(num):
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