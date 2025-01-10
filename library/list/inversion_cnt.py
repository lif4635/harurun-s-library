class BIT:
    def __init__(self, n):
        self.n = n
        self.data = [0]*(n+1)
    
    def add(self, p, x):
        p += 1
        while p < self.n:
            self.data[p] += x
            p += p& -p
    
    def sum0(self, r):
        s = 0
        while r > 0:
            s += self.data[r]
            r -= r& -r
        return s
    
    def sum(self, l, r):
        return self.sum0(r) - self.sum0(l)
    
    def get(self, p):
        return self.sum0(p+1) - self.sum0(p)
    
    def __str__(self):
        return str([self.get(i) for i in range(self.n)])

def inversion_cnt(lst:list) -> int:
    """
    i > j && a_i < a_j
    """
    n = len(lst)
    maxlst = max(lst)
    
    if  maxlst >= n+10:
        order = {x:i for i,x in enumerate(sorted(set(lst)))}
        lst = [order[x] for x in lst]
    
    ft = BIT(n+10)
    ans = [0]*n
    for i in range(n):
        ans[i] = ft.sum(lst[i]+1,n)
        ft.add(lst[i], 1)
    
    return ans
