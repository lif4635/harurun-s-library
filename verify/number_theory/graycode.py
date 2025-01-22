# https://atcoder.jp/contests/agc031/submissions/61939119

from collections import deque

def graycode(n:int):
    for i in range(1<<n):
        yield i ^ (i>>1)

def graycode_a_to_b(n:int, a:int ,b:int):
    assert (a^b).bit_count()&1
    
    code = list(graycode(n))
    for i in range(1<<n):
        code[i] ^= a
    code = deque(code)
    
    sgn = [0,-1,-1,0]
    for i in range(1<<n):
        si = sgn[i&3]
        if code[si] == b:
            break
        if si == 0:
            yield code.popleft()
        else:
            yield code.pop()
    
    if si == 0:
        while code:
            yield code.pop()
    else:
        while code:
            yield code.popleft()

n,a,b = map(int, input().split())
if (a^b).bit_count()&1:
    print("YES")
    print(*graycode_a_to_b(n,a,b))
else:
    print("NO")