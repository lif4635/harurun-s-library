from math import isqrt
class SqrtTree:
    __slots__ = ["n", "size", "log", "op", "e", "data", "block"]

    def __init__(self, op, e, n):
        self.n = n
        self.size = 512 # sqrt(2.5 * 10 ** 5)
        self.log = 9
        # self.size = isqrt(2 * self.n)
        self.op = op
        self.e = e
        self.data = [e] * n
        self.block = [e] * ((n >> self.log) + 1)

    def get(self, i):
        return self.data[i]
    
    def add(self, i, x):
        self.data[i] = self.op(self.data[i], x)
        self.block[i >> self.log] = self.op(self.block[i >> self.log], x)
    
    def prod(self, l, r):
        if r <= l:
            return self.e
        res = self.e
        while l < r and l % self.size:
            res = self.op(res, self.data[l])
            l += 1
        while l + self.size <= r:
            res = self.op(res, self.block[l >> self.log])
            l += self.size
        while l < r:
            res = self.op(res, self.data[l])
            l += 1
        return res
    
    def all_prod(self):
        return self.prod(0, self.n)
    
    def __str__(self):
        return str(self.data)
