class SparseTable:
    def __init__(self, op, lst):
        self.n = len(lst)
        self.h = self.n.bit_length()
        self.op = op
        self.data = [0]*(self.n*self.h)
        for i in range(self.n):
            self.data[i] = lst[i]
        for i in range(1,self.h):
            for j in range(self.n - (1<<i) + 1):
                self.data[i*self.n + j] = op(self.data[(i-1)*self.n + j], self.data[(i-1)*self.n + j+(1<<(i-1))])
    
    def prod(self, l ,r):
        level = (r - l).bit_length() - 1
        return self.op(self.data[level*self.n + l], self.data[level*self.n + r-(1<<level)])

import io,os,sys
input = io.BytesIO(os.read(0,os.fstat(0).st_size)).readline
MI = lambda : map(int, input().split())
LI = lambda : list(map(int, input().split()))

n,q = MI()
a = LI()
st = SparseTable(min,a)

ans = [0]*q
for i in range(q):
    l,r = MI()
    ans[i] = st.prod(l, r)
os.write(1," ".join(map(str,ans)).encode())