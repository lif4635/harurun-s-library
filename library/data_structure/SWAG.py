class SWAG:
    """
    Sliding Window Aggregation
    """
    
    __slots__ = ["op", "e", "front", "frontprod", "back", "backprod"]
    
    def __init__(self, op, e = None):
        self.op = op
        self.e = e
        self.front = []
        self.frontprod = []
        self.back = []
        self.backprod = []
        
    def prod(self):
        if (not self.frontprod) and (not self.backprod):
            return self.e
        elif not self.frontprod:
            return self.backprod[-1]
        elif not self.backprod:
            return self.frontprod[-1]
        else:
            return self.op(self.frontprod[-1], self.backprod[-1])
        
    def pop(self):
        if not self.front:
            self.front = self.back[::-1]
            self.frontprod = self.front.copy()
            for i in range(1, len(self.front)):
                self.frontprod[i] = self.op(self.front[i], self.frontprod[i-1])
            self.back.clear()
            self.backprod.clear()
        self.front.pop()
        self.frontprod.pop()
        
    def push(self, x):
        if self.back:
            self.backprod.append(self.op(self.backprod[-1], x))
            self.back.append(x)
        else:
            self.backprod.append(x)
            self.back.append(x)
    
    def __len__(self):
        return len(self.front) + len(self.back)
    
    def __str__(self):
        return str(self.front[::-1] + self.back)