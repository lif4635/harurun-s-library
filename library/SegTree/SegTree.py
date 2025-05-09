class SegTree:
    __slots__ = ["n", "size", "op", "e", "data"]
    
    def __init__(self, op, e, lst):
        self.n = len(lst)
        self.size = 1 << (self.n - 1).bit_length()
        self.op = op
        self.e = e
        self.data = [e] * (2 * self.size)
        for i in range(self.n):
            self.data[self.size + i] = lst[i]
        for i in range(self.size - 1, 0, -1):
            self.data[i] = self.op(self.data[2*i], self.data[2*i+1])
    
    def get(self, i):
        return self.data[self.size+i]
    
    def add(self, i, x):
        i += self.size
        self.data[i] = self.op(x, self.data[i])
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[2*i], self.data[2*i+1])
    
    def set(self, i, x):
        i += self.size
        self.data[i] = x
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[2*i], self.data[2*i+1])
    
    def prod(self, l, r):
        if r <= l:
            return self.e
        lres = self.e
        rres = self.e
        l += self.size
        r += self.size
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
    
    def max_right(self, l, g):
        assert 0<=l and l<=self.n
        assert g(self.e)
        if l == self.n: return self.n
        l += self.size
        sm = self.e
        while 1:
            while l&1 == 0:
                l >>= 1
            if not(g(self.op(sm, self.data[l]))):
                while l < self.size:
                    l = 2*l
                    nsm = self.op(sm, self.data[l])
                    if g(nsm):
                        sm = nsm
                        l += 1
                return l-self.size
            sm = self.op(sm, self.data[l])
            l += 1
            if (l&-l) == l: break
        return self.n
    
    def min_left(self, r, g):
        if r == -1: r = self.n
        assert 0<=r and r<=self.n
        assert g(self.e)
        if r == 0: return 0
        r += self.size
        sm = self.e
        while 1:
            r -= 1
            while (r>1 and r&1):
                r >>= 1
            if not(g(self.op(self.data[r], sm))):
                while r < self.size:
                    r = 2*r+1
                    nsm = self.op(self.data[r], sm)
                    if g(nsm):
                        sm = nsm
                        r -= 1
                return r + 1 -self.size
            sm = self.op(self.data[r], sm)
            if (r&-r) == r: break
        return 0
    
    def __str__(self):
        return str(self.data[self.size:self.size+self.n])