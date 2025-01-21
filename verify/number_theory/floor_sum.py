# https://judge.yosupo.jp/submission/262794

def floor_sum(n, m, a, b):
    res = 0
    while n:
        if a < 0 or m <= a:
            k, a = divmod(a, m)
            res += n*(n-1) * k >> 1
        if b < 0 or m <= b:
            k, b = divmod(b, m)
            res += n * k
        n, b = divmod(a*n+b, m)
        a, m = m, a
    return res

import io,os,sys
input = io.BytesIO(os.read(0,os.fstat(0).st_size)).readline
MI = lambda : map(int, input().split())
t = int(input())
ans = [0]*t
for i in range(t):
    n,m,a,b = MI()
    ans[i] = floor_sum(n,m,a,b)

os.write(1," ".join(map(str,ans)).encode())