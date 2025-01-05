def miller_rabin(num):
    assert 1 <= num < (1<<63)-1
    
    if num < 4: return num > 1
    if not num&1: return False
    
    d, s = num-1, 0
    while not d&1:
        d >>= 1
        s += 1
        
    tests = (2,7,61) if num < 4759123141 else (2,325,9375,28178,450775,9780504,1795265022)
        
    for test in tests:
        if test >= num: continue
        if pow(test, d, num) == 1: continue
        if any(pow(test, d * 2**i, num) == num - 1 for i in range(s)): continue
        for i in range(s):
            test = test*test%num
            if test == num-1: break
        else:
            return False
    return True
