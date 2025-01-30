class SparseTable:
    def __init__(self, op, lst):
        self.n = len(lst)
        self.h = self.n.bit_length()
        self.op = op
        self.data = [0]*(self.n*self.h)
        for i in range(self.n):
            self.data[i] = lst[i]
        for i in range(1,self.h):
            for j in range(self.n - (1<<i) + 1):
                self.data[i*self.n + j] = op(self.data[(i-1)*self.n + j], self.data[(i-1)*self.n + j+(1<<(i-1))])
    
    def prod(self, l ,r):
        level = (r - l).bit_length() - 1
        return self.op(self.data[level*self.n + l], self.data[level*self.n + r-(1<<level)])