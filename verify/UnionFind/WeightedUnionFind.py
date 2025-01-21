# https://judge.yosupo.jp/submission/262701

mod = 998244353

class WeightedUnionFind:
    def __init__(self, n):
        self.n = n
        self.p = [*range(n)]
        self.w = [0] * n

    def leader(self, a):
        potential = 0
        while self.p[a] != a:
            self.w[a] += self.w[self.p[a]]
            self.w[a] %= mod
            potential += self.w[a]
            self.p[a] = a = self.p[self.p[a]]
        return a, potential

    def merge(self, a, b, d):
        """
        w[a] - w[b] = d
        """
        a,wa = self.leader(a)
        b,wb = self.leader(b)
        
        w = (d + wa - wb)%mod
        if a == b:
            if w == 0: return 1
            else: return 0
        
        self.p[b] = a
        self.w[b] = w
        return 1
    
    def diff(self, a, b):
        a,wa = self.leader(a)
        b,wb = self.leader(b)
        if a == b:
            return (wb - wa)%mod
        else:
            return -1


import io,os,sys
input = io.BytesIO(os.read(0,os.fstat(0).st_size)).readline
LI = lambda : list(map(int, input().split()))

n,q = map(int, input().split())
uf = WeightedUnionFind(n)

ans = [0]*q
for i in range(q):
    qry = LI()
    if qry[0]:
        _,u,v = qry
        ans[i] = uf.diff(u,v)
    else:
        _,u,v,x = qry
        ans[i] = uf.merge(u,v,x)
os.write(1," ".join(map(str,ans)).encode())