class BIT:
    def __init__(self, n):
        self.n = n
        self.data = [0]*(n+1)
    
    def build(self, arr):
        for i,a in enumerate(arr):
            self.data[i+1] = a
        for i in range(1, self.n+1):
            if i + (i&-i) <= self.n:
                self.data[i + (i&-i)] += self.data[i]
    
    def add(self, p, x):
        p += 1
        while p <= self.n:
            self.data[p] += x
            p += p& -p
    
    def sum0(self, r):
        s = 0
        while r:
            s += self.data[r]
            r -= r& -r
        return s
    
    def sum(self, l, r):
        s = 0
        while r:
            s += self.data[r]
            r -= r& -r
        while l:
            s -= self.data[l]
            l -= l& -l
        return s
    
    def get(self, p):
        return self.sum0(p+1) - self.sum0(p)
    
    def __str__(self):
        return str([self.get(i) for i in range(self.n)])
