"""
まだです
"""

class RollbackUnionFind:
    def __init__(self, N):
        self.n = n
        self.par = [-1] * n
        self.snap = 0
        self.history = []
        # connected component
        self.cc = n
        pass
    
    def merge(self, a, b):
        a = self.find(a)
        b = self.find(b)
        self.history.append((a,self.par[a]))
        self.history.append((b,self.par[b]))
        if a == b: return False
        if self.par[a] > self.par[b]:
            a,b = b,a
        self.par[a] += self.par[b]
        self.par[b] = a
        self.cc -= 1
        return True
    
    def leader(self, a):
        while self.par[a] >= 0:
            a = self.par[a]
        return a
    
    def same(self, a, b):
        return self.leader(a) == self.leader(b)
    
    def size(self, a):
        return -self.par[self.leader(a)]
    
    def undo(self):
        x,px = self.history.pop()
        self.par[x] = px
        y,py = self.history.pop()
        self.par[y] = py
        if x != y:
            self.cc += 1
        
    def snapshot(self):
        self.snap = len(self.history) >> 1
        return self.snap
    
    def count(self):
        return len(self.history) >> 1
    
    def rollback(self, state = -1):
        if state == -1:
            state = self.snap
        state <<= 1
        while state < len(self.history):
            x,px = self.history.pop()
            self.par[x] = px
            y,py = self.history.pop()
            self.par[y] = py
            if x != y:
                self.cc += 1
        return
    
    def connect(self):
        return self.cc


import sys
input = sys.stdin.readline
II = lambda : int(input())
MI = lambda : map(int, input().split())
LI = lambda : list(map(int, input().split()))
SI = lambda : input().rstrip()
LLI = lambda n : [list(map(int, input().split())) for _ in range(n)]
LSI = lambda n : [input().rstrip() for _ in range(n)]
MI_1 = lambda : map(lambda x:int(x)-1, input().split())
LI_1 = lambda : list(map(lambda x:int(x)-1, input().split()))

def graph(n:int, m:int, dir:bool=False, index:int=-1) -> list[set[int]]:
    edge = [set() for i in range(n+1+index)]
    for _ in range(m):
        a,b = map(int, input().split())
        a += index
        b += index
        edge[a].add(b)
        if not dir:
            edge[b].add(a)
    return edge

n,q = MI()
g = [[] for i in range(q+1)]
qry = [[] for i in range(q+1)]
for i in range(q):
    t,k,u,v = MI()
    k += 1
    if t:
        qry[k].append((i,u,v))
    else:
        g[k].append((i,u,v))

uf = RollbackUnionFind(n)

ans = [-1]*q

uf = RollbackUnionFind(N)
que = [[-1, 0, -1, 0, 1]]
while q:
    a = que.pop()
    if a[0] == 1:
        ans[a[1]] = uf.same(a[2], a[3])
    else:
        if a[-1]:
            a[-1] = 0
            que.append(a)
            if a[0] == 0:
                uf.union(a[2], a[3])
            for aa in g[a[1]]:
                que.append(aa)
        else:
            if a[0] == 0:
                uf.undo()

for i in ans:
    if ans != -1: print(i)