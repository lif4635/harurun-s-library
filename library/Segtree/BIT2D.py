class BIT2D:
    def __init__(self, h, w, op):
        self.h = h
        self.w = w
        self.op = op
        self.data = dict()
    
    def update(self, i, j, x):
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
                    bit[k] = self.op(bit[k],x)
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
                        res = self.op(bit[k],res)
                    k -= k&-k
            i -= i&-i
        return res
