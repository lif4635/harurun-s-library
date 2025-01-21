class WeightedUnionFind:
    def __init__(self, n):
        self.n = n
        self.p = [*range(n)]
        self.w = [0] * n

    def leader(self, a):
        potential = 0
        while self.p[a] != a:
            self.w[a] += self.w[self.p[a]]
            potential += self.w[a]
            self.p[a] = a = self.p[self.p[a]]
        return a, potential

    def merge(self, a, b, d):
        """
        w[a] - w[b] = d
        """
        a,wa = self.leader(a)
        b,wb = self.leader(b)
        
        w = d + wa - wb
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
            return wb - wa
        else:
            return -1
