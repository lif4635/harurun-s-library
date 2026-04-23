class eertree:
    def __init__(self, s):
        # even : 0, odd : 1
        n = len(s) + 2
        self.s = [None] * n
        self.l = [0] * n
        self.par = [-1] * n
        self.ch = [dict() for i in range(n)] 
        self.link = [0] * n
        self.suf = [0] * n
        
        self.link[0] = 1 
        self.l[1] = -1
        self.n = 1
        self.last = 0
        self.node = 2
        for c in s:
            self.s[self.n] = c
            self.n += 1
            self.last = self.get_link(self.last)
            if not c in self.ch[self.last]:
                u = self.ch[self.get_link(self.link[self.last])].get(c, 0)
                self.link[self.node] = u
                self.par[self.node] = self.last 
                self.l[self.node] = self.l[self.last] + 2
                self.ch[self.last][c] = self.node
                self.node += 1
            self.last = self.ch[self.last][c]
            self.suf[self.n] = self.last
    
    def get_link(self, v):
        while self.s[self.n-1] != self.s[self.n - self.l[v] - 2]:
            v = self.link[v]
        return v