class UnionFind:
    def __init__(self, n):
        self.n = n
        self.par = [*range(n)]
        self.size = [1] * n

    def leader(self, a):
        while self.par[a] != a:
            self.par[a] = a = self.par[self.par[a]]
        return a

    def merge(self, a, b):
        a = self.leader(a)
        b = self.leader(b)
        if a == b: return a
        if self.size[a] > self.size[b]:
            self.size[a] += self.size[b]
            self.par[b] = a
            return a
        else:
            self.size[b] += self.size[a]
            self.par[a] = b
            return b

    def same(self, a, b):
        return self.leader(a) == self.leader(b)
    
    def size(self, a):
        return self.size[self.leader(a)]
    
    def groups(self):
        res = [[] for i in range(self.n)]
        for i in range(self.n):
            res[leader(i)].append(i)
        res2 = []
        for i in range(self.n):
            if len(res[i]) > 0:
                res2.append(res[i])
        return res2