class LCA:
    
    __slots__ = ["n", "h", "order", "path", "data"]
    
    def __init__(self, edge, root = 0):
        self.n = len(edge)
        self.order = [-1] * self.n
        self.path = [-1] * (self.n-1)
        parent = [-1] * self.n
        que = [root]
        t = -1
        while que:
            u = que.pop()
            self.path[t] = parent[u] 
            t += 1
            self.order[u] = t
            for v in edge[u]:
                if self.order[v] == -1:
                    que.append(v)
                    parent[v] = u
        self.n -= 1
        self.h = self.n.bit_length()
        self.data = [0] * (self.n * self.h)
        self.data[:self.n] = [self.order[u] for u in self.path]
        for i in range(1, self.h):
            for j in range(self.n - (1<<i) + 1):
                self.data[i*self.n + j] = min(self.data[(i-1)*self.n + j], self.data[(i-1)*self.n + j+(1<<(i-1))])
        
    def __call__(self, u, v):
        if u == v: return u
        l = self.order[u]
        r = self.order[v]
        if l > r:
            l,r = r,l
        level = (r - l).bit_length() - 1
        return self.path[min(self.data[level*self.n + l], self.data[level*self.n + r-(1<<level)])]
    
import io,os,sys
input = io.BytesIO(os.read(0,os.fstat(0).st_size)).readline
MI = lambda : map(int, input().split())
LI = lambda : [int(x) for x in input().split()]

n,q = MI()
p = LI()
edge = [[] for i in range(n)]
for i in range(n-1):
    edge[p[i]].append(i+1)

lca = LCA(edge)
ans = []
for _ in range(q):
    u,v = MI()
    ans.append(lca(u, v))

os.write(1," ".join(map(str,ans)).encode())