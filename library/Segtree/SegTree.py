class SegTree:
    def __init__(self, op, e, lst):
        self.n = len(lst)
        self.N0 = 1 << (self.n - 1).bit_length()
        self.op = op
        self.e = e
        self.data = [e] * (2 * self.N0)
        for i in range(self.n):
            self.data[self.N0 + i] = lst[i]
        for i in range(self.N0 - 1, 0, -1):
            self.data[i] = self.op(self.data[2*i], self.data[2*i+1])
    
    def get(self, i):
        return self.data[self.N0+i]
    
    def add(self, i, x):
        i += self.N0
        self.data[i] = self.op(x, self.data[i])
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[2*i], self.data[2*i+1])
    
    def set(self, i, x):
        i += self.N0
        self.data[i] = x
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[2*i], self.data[2*i+1])
    
    def prod(self, l, r):
        if r <= l:
            return self.e
        lres = self.e
        rres = self.e
        l += self.N0
        r += self.N0
        while l < r:
            if l & 1:
                lres = self.op(lres, self.data[l])
                l += 1
            if r & 1:
                r -= 1
                rres = self.op(self.data[r], rres)
            l >>= 1
            r >>= 1
        return self.op(lres, rres)
    
    def all_prod(self):
        return self.data[1]
    
    def __str__(self):
        return str(self.data[self.N0:self.N0+self.n])
