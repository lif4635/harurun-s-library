# 参考 : https://maspypy.com/slope-trick-1-%E8%A7%A3%E8%AA%AC%E7%B7%A8

from heapq import heappop,heappush
class slope_trick:
    def __init__(self):
        self.l = []
        self.r = []
        self.addl = 0
        self.addr = 0
        self.miny = 0
    
    def get(self):
        """
        min(f(x))
        """
        return self.miny
    
    def add_const(self, a):
        """
        f(x) <- f(x) + a
        """
        self.miny += a
    
    def add_xma(self, a):
        """
        f(x) <- f(x) + (x-a)_plus
        """
        if len(self.l) != 0:
            self.miny += max(0, -self.l[0]+self.addl - a)
        heappush(self.l, -a+self.addl)
        heappush(self.r, -heappop(self.l)+self.addl - self.addr)
    
    def add_amx(self, a):
        """
        f(x) <- f(x) + (x-a)_minus
        """
        if len(self.r) != 0:
            self.miny += max(0, a - (self.r[0]+self.addr))
        heappush(self.r, a-self.addr)
        heappush(self.l, -(heappop(self.r)+self.addr) + self.addl)
    
    def add_absxa(self, a):
        """
        f(x) <- f(x) + abs(x-a)
        """
        self.add_xma(a)
        self.add_amx(a)
    
    def cum_min(self):
        """
        g(x) = min(y<=x) f(y)
        """
        self.r = []
    
    def cum_min_right(self):
        """
        g(x) = min(x<=y) f(y)
        """
        self.l = []
    
    def shift(self, a):
        """
        g(x) = f(x-a)
        """
        self.addl += a
        self.addr += a
    
    def slide(self, a, b):
        """
        a <= b
        g(x) = min(x-b<=y<=x-a) f(y)
        """
        self.addl += a
        self.addr += b