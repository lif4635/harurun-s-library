class BIT:
    def __init__(self, n):
        self.n = n
        self.data = dict()
    
    def add(self, p, x):
        p += 1
        while p < self.n:
            if p in self.data:
                self.data[p] += x
            else:
                self.data[p] = x
            p += p& -p
    
    def sum0(self, r):
        s = 0
        while r > 0:
            if r-1 in self.data:
                s += self.data[r]
            r -= r& -r
        return s
    
    def sum(self, l, r):
        return self.sum0(r) - self.sum0(l)
    
    def get(self, p):
        return self.sum0(p+1) - self.sum0(p)
