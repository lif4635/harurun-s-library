class SWAG:
    """
    Sliding Window Aggregation
    """
    def __init__(self,op):
        self.op = op
        self.front = []
        self.frontprod = []
        self.back = []
        self.backprod = []
        
    def prod(self):
        if self.frontprod == [] and self.backprod == []:
            return None
        elif self.frontprod == []:
            return self.backprod[-1]
        elif self.backprod == []:
            return self.frontprod[-1]
        else:
            return self.op(self.frontprod[-1], self.backprod[-1])
        
    def pop(self):
        if self.front == []:
            val = self.back.pop()
            self.backprod.pop()
            self.frontprod.append(val)
            self.front.append(val)
            while self.back != []:
                val = self.back.pop()
                self.backprod.pop()
                self.frontprod.append(self.op(val,self.frontprod[-1]))
                self.front.append(val)
        self.front.pop()
        self.frontprod.pop()
        
    def push(self,x):
        if self.back == []:
            self.backprod.append(x)
            self.back.append(x)
        else:
            self.backprod.append(self.op(self.backprod[-1],x))
            self.back.append(x)
