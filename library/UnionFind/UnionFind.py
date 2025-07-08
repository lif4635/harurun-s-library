class DSU:
    __slots__ = ["n", "par", "siz", "fix_leader"]
    
    def __init__(self, n, fix_leader = False):
        self.n = n
        self.par = [*range(n)]
        self.siz = [1] * n
        self.fix_leader = fix_leader

    def leader(self, a):
        while self.par[a] != a:
            self.par[a] = a = self.par[self.par[a]]
        return a

    def merge(self, a, b):
        a = self.leader(a)
        b = self.leader(b)
        if a == b: return a
        if self.fix_leader or self.siz[a] > self.siz[b]:
            self.siz[a] += self.siz[b]
            self.par[b] = a
            return a
        else:
            self.siz[b] += self.siz[a]
            self.par[a] = b
            return b

    def same(self, a, b):
        return self.leader(a) == self.leader(b)
    
    def size(self, a):
        return self.siz[self.leader(a)]
    
    def groups(self):
        res = [[] for i in range(self.n)]
        for i in range(self.n):
            res[self.leader(i)].append(i)
        res2 = []
        for i in range(self.n):
            if len(res[i]) > 0:
                res2.append(res[i])
        return res2
