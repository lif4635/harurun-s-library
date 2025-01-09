class BIT:
    def __init__(self, n):
        self.n = n
        self.data = [0]*(n+1)
    
    def add(self, p, x):
        p += 1
        while p < self.n:
            self.data[p] += x
            p += p& -p
    
    def sum0(self, r):
        s = 0
        while r > 0:
            s += self.data[r]
            r -= r& -r
        return s
    
    def sum(self, l, r):
        return self.sum0(r) - self.sum0(l)
    
    def get(self, p):
        return self.sum0(p+1) - self.sum0(p)
    
    def __str__(self):
        return str([self.get(i) for i in range(self.n)])
