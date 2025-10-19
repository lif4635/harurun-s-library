class interval_base:
    """
    fix left 
    """
    def __init__(self, a):
        n = len(a)
        m = len(a[0])
        base = [(n, [0] * m)]
        self.basis = [[] for i in range(n)]
        for i in reversed(range(n)):
            ii = i
            x = a[i].copy()
            x = [xi%mod for xi in x]
            idx = 0
            while idx < len(base):         
                j, y = base[idx]
                flag = False
                
                """
                insert
                -> 上三角行列を満たすならOK
                """
                for b in range(m):
                    if x[b] != 0 and y[b] == 0:
                        base.insert(idx, (i, x))
                        flag = True
                        break
                    elif y[b] != 0:
                        break
                else:
                    break
                if flag: break
                
                """
                skip について
                -> 先ほどと逆の条件
                """
                for b in range(m):
                    if y[b] != 0 and x[b] == 0:
                        flag = True
                        idx += 1
                        break
                    elif x[b] != 0:
                        break
                if flag: continue
                
                if i < j:
                    i, j = j, i
                    x, y = y, x
                    base[idx] = (j, y)
                
                coef = 0
                for b in range(m):
                    if x[b] != 0 and coef == 0:
                        coef = -x[b] * pow(y[b], -1, mod) % mod
                    x[b] = (x[b] + y[b] * coef) % mod
                idx += 1
                
            self.basis[ii] = base.copy()