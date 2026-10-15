class MonoidUnionFind:
    """
    mergeの順序はcompでわたせる
    小さいほうにmerge
    """
    
    __slots__ = ["n", "op", "e", "par", "data", "comp"]
    
    def __init__(self, op, e, data, comp = None):
        self.n = len(data)
        self.op = op
        self.e = e
        self.par = [-1]*self.n
        self.data = data
        self.comp = comp
    
    def merge(self, a, b):
        a = self.leader(a)
        b = self.leader(b)
        if a == b: return a
        if self.comp == None:
            if -self.par[a] < -self.par[b]:
                a,b = b,a
        else:
            if self.comp(self.data[a], self.data[b]):
                a,b = b,a
        self.par[a] += self.par[b]
        self.par[b] = a
        self.data[a] = self.op(self.data[a], self.data[b])
        self.data[b] = self.e
        return a
    
    def same(self, a, b):
        return self.leader(a) == self.leader(b)
    
    def leader(self, a):
        if self.par[a] < 0: return a
        self.par[a] = self.leader(self.par[a])
        return self.par[a]
        
    def size(self, a):
        return -self.par[self.leader(a)]
    
    def set(self, a, x):
        self.data[self.leader(a)] = x
    
    def add(self, a, x):
        a = self.leader(a)
        self.data[a] = self.op(self.data[a], x)
    
    def get(self, a):
        return self.data[self.leader(a)]