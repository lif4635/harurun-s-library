# https://judge.yosupo.jp/submission/262791

class SegTree:
    def __init__(self, op, e, lst):
        self.n = len(lst)
        self.N0 = 1 << (self.n - 1).bit_length()
        self.op = op
        self.e = e
        self.data = [e] * (2 * self.N0)
        for i in range(self.n):
            self.data[self.N0 + i] = lst[i]
        for i in range(self.N0 - 1, 0, -1):
            self.data[i] = self.op(self.data[2*i], self.data[2*i+1])
    
    def get(self, i):
        return self.data[self.N0+i]
    
    def add(self, i, x):
        i += self.N0
        self.data[i] = self.op(x, self.data[i])
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[2*i], self.data[2*i+1])
    
    def set(self, i, x):
        i += self.N0
        self.data[i] = x
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[2*i], self.data[2*i+1])
    
    def prod(self, l, r):
        if r <= l:
            return self.e
        lres = self.e
        rres = self.e
        l += self.N0
        r += self.N0
        while l < r:
            if l & 1:
                lres = self.op(lres, self.data[l])
                l += 1
            if r & 1:
                r -= 1
                rres = self.op(self.data[r], rres)
            l >>= 1
            r >>= 1
        return self.op(lres, rres)
    
    def all_prod(self):
        return self.data[1]
    
    def __str__(self):
        return str(self.data[self.N0:self.N0+self.n])

import io,os,sys
input = io.BytesIO(os.read(0,os.fstat(0).st_size)).readline
MI = lambda : map(int, input().split())

n,q = MI()

e = 1<<30
mask = e - 1
mod = 998244353
def op(x,y):
    a,b = x>>30,x&mask
    c,d = y>>30,y&mask
    return (a*c%mod<<30) + (b*c+d)%mod

data = [0]*n
for i in range(n):
    a,b = MI()
    data[i] = (a<<30) + b

st = SegTree(op,e,data)

ans = []
for i in range(q):
    t,p,c,d = MI()
    if t:
        res = st.prod(p,c)
        a,b = res>>30,res&mask
        ans.append((a*d+b)%mod)
    else:
        st.set(p, (c<<30) + d)

os.write(1," ".join(map(str,ans)).encode())