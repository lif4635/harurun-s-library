class suffix_xor_base:
    def __init__(self, a):
        base = [(-1,0)]
        self.suffix_xor = [base]
        for i in range(n):
            x = a[i]
            idx = 0
            while idx < len(base):         
                j, y = base[idx]
                if x & ~y > y:
                    base.insert(idx, (i, x))
                    break
                if x <= x^y:
                    idx += 1
                    continue
                if i > j:
                    i,j = j,i
                    x,y = y,x
                    base[idx] = (j, y)
                x ^= y
                idx += 1
            self.suffix_xor.append(base.copy())
    
    def get(self, l, r):
        res = []
        for i, x in self.suffix_xor[r]:
            if l <= i:
                res.append(x)
        return res