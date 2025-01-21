from array import array
class WeightedUnionFind:
    def __init__(self, n):
        self.n = n
        self.par = array("I",range(n))
        self.size = array("I",[1] * n)
        self.weight = array("l",[0] * n)

    def leader(self, a):
        potential = 0
        while self.par[a] != a:
            self.weight[a] += self.weight[self.par[a]]
            potential += self.weight[a]
            self.par[a] = a = self.par[self.par[a]]
        return a, potential

    def merge(self, a, b, d):
        '''
        weight[a] - weight[b] = d
        '''
        a,wa = self.leader(a)
        b,wb = self.leader(b)
        
        w = d + wa - wb
        if a == b:
            if w == 0: return 1
            else: return 0
        
        if self.size[a] < self.size[b]:
            self.par[b] = a
            self.size[a] += self.size[b]
            self.weight[b] = w
        else:
            self.par[a] = b
            self.size[b] += self.size[a]
            self.weight[a] = -w
        return 1

    def same(self, a, b):
        return self.leader(a) == self.leader(b)
    
    def size(self, a):
        return self.size[self.leader(a)]
    
    def diff(self, a, b):
        a,wa = self.leader(a)
        b,wb = self.leader(b)
        if a == b:
            return wb - wa
        else:
            return -1
