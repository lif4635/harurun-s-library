class DualSegTree:
    __slots__ = ("n", "log", "size", "op", "e", "data")
    
    def __init__(self, op, e, lst):
        self.n = len(lst)
        self.log = (self.n - 1).bit_length()
        self.size = 1 << self.log 
        self.op = op
        self.e = e
        self.data = [e] * (2 * self.size)
        for i in range(self.n):
            self.data[self.size + i] = lst[i]
            
    def propagate(self, k):
        if self.data[k] != self.e:
            self.data[2*k] = self.op(self.data[2*k], self.data[k])
            self.data[2*k+1] = self.op(self.data[2*k+1], self.data[k])
            self.data[k] = self.e
    
    def get(self, i):
        i += self.size
        for d in range(1, self.log + 1):
            self.propagate(i >> d)
        return self.data[i]
        
    def apply(self, l, r, f):
        l += self.size
        r += self.size
        for d in range(1, self.log + 1):
            self.propagate(l >> d)
            self.propagate(r >> d)
        while l < r:
            if l & 1:
                self.data[l] = self.op(self.data[l], f)
                l += 1
            if r & 1:
                r -= 1
                self.data[r] = self.op(self.data[r], f)
            l >>= 1
            r >>= 1
    
    def __str__(self):
        for i in range(1, self.size):
            self.propagate(i)
        return str(self.data[self.size:self.size+self.n])