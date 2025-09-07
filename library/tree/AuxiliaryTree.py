class AuxiliaryTree:
    __slots__ = ["n", "h", "order", "path", "data", "depth", "edge", "par"]
    
    def __init__(self, edge, root = 0):
        self.n = len(edge)
        self.order = [-1] * self.n
        self.path = [-1] * (self.n-1)
        self.depth = [0] * self.n
        self.edge = [[] for i in range(self.n)]
        self.par = [-1] * self.n
        
        if self.n == 1: return
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
                    self.depth[v] = self.depth[u] + 1
        
        # lca構築
        self.n -= 1
        self.h = self.n.bit_length()
        self.data = [0] * (self.n * self.h)
        self.data[:self.n] = [self.order[u] for u in self.path]
        for i in range(1, self.h):
            for j in range(self.n - (1<<i) + 1):
                self.data[i*self.n + j] = min(self.data[(i-1)*self.n + j], self.data[(i-1)*self.n + j+(1<<(i-1))])
        
        
    def make(self, vs):
        k = len(vs)
        vs.sort(key = self.order.__getitem__)
        
        self.edge[vs[0]] = []
        
        st = [vs[0]]
        
        for i in range(k - 1):
            l = self.order[vs[i]]
            r = self.order[vs[i+1]]
            level = (r - l).bit_length() - 1
            w = self.path[min(self.data[level*self.n + l], self.data[level*self.n + r-(1<<level)])]
            if w != vs[i]:
                p = st.pop()
                while st and self.depth[w] < self.depth[st[-1]]:
                    self.par[p] = st[-1]
                    self.edge[st[-1]].append(p)
                    p = st.pop()
                
                if not st or st[-1] != w:
                    st.append(w)
                    self.edge[w] = [p]
                else:
                    self.edge[w].append(p)
                self.par[p] = w
            
            st.append(vs[i+1])
            self.edge[vs[i+1]] = []
        
        for i in range(len(st) - 1):
            self.edge[st[i]].append(st[i+1])
            self.par[st[i+1]] = st[i]
        
        self.par[st[0]] = -1
        return st[0]
