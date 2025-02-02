# https://judge.yosupo.jp/submission/262467

import sys
input = sys.stdin.buffer.readline
II = lambda : int(input())
MI = lambda : map(int, input().split())
LI = lambda : list(map(int, input().split()))
SI = lambda : input().rstrip()
LLI = lambda n : [list(map(int, input().split())) for _ in range(n)]
LSI = lambda n : [input().rstrip() for _ in range(n)]
MI_1 = lambda : map(lambda x:int(x)-1, input().split())
LI_1 = lambda : list(map(lambda x:int(x)-1, input().split()))

def miller_rabin(num):
    # assert 1 <= num < (1<<63)-1
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
            for i in range(s-1):
                t = t*t%num
                if t == num-1: break
            else:
                return False
    return True

q = II()
for i in range(q):
    print("Yes" if miller_rabin(II()) else "No")