"""
正直使い物になりませんね。
基本的にcppに書き直さなきゃいけなくなると思います。
(TLEによりverifyできませんでした)
"""

class BIT2D:
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self.data = dict()
    
    def add(self, i, j, x):
        i += 1
        while i <= self.h:
            if not i in self.data:
                self.data[i] = dict()
            bit = self.data[i]
            k = j+1
            while k <= self.w:
                if not k in bit:
                    bit[k] = x
                else:
                    bit[k] += x
                k += k&-k
            i += i&-i
    
    def prod(self, i, j):
        res = self.id
        while i > 0:
            if i in self.data:
                bit = self.data[i]
                k = j
                while k > 0:
                    if k in bit:
                        res += bit[k]
                    k -= k&-k
            i -= i&-i
        return res
    
    def rectangle(self, l, d, r, u):
        res = self.prod(r, u) + self.prod(l, d) - self.prod(l, u) - self.prod(r, d)
        return res