class prefix_xor_base:
    __slots__ = ["prefix_xor"]
    
    def __init__(self, a):
        n = len(a)
        base = [(n, 0)]
        self.prefix_xor = [[] for i in range(n)]
        for i in reversed(range(n)):
            ii = i
            x = a[i]
            idx = 0
            while idx < len(base):         
                j, y = base[idx]
                if x & ~y > y:
                    base.insert(idx, (i, x))
                    break
                elif x <= x ^ y:
                    idx += 1
                    continue
                elif i < j:
                    i, j = j, i
                    x, y = y, x
                    base[idx] = (j, y)
                x ^= y
                idx += 1
            self.prefix_xor[ii] = base.copy()
    
    def get(self, l, r):
        res = []
        for i, x in self.prefix_xor[l]:
            if i < r:
                res.append(x)
        return res