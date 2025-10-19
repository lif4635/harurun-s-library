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