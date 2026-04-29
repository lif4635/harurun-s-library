from array import array

class RangeParallelUnionFind:
    __slots__ = ['offset', 'par', 'sz', 'sd', 'sx', 'sy']

    def __init__(self, n):
        self.offset = n + 1
        max_lg = n.bit_length() - 1 if n > 0 else 0
        size = (max_lg + 1) * self.offset
        self.par = array('i', range(size))
        self.sz = array('i', [1] * size)
        self.sd = array('i', [0] * 64)
        self.sx = array('i', [0] * 64)
        self.sy = array('i', [0] * 64)

    def merge_range(self, k, u, v):
        res = []
        if k <= 0:
            return res
        
        o = k.bit_length() - 1
        sd = self.sd
        sx = self.sx
        sy = self.sy
        
        p = 0
        sd[0] = o; sx[0] = u; sy[0] = v
        if k != (1 << o):
            p += 1
            rem = k - (1 << o)
            sd[1] = o; sx[1] = u + rem; sy[1] = v + rem

        par = self.par
        sz = self.sz
        offset = self.offset
        
        while p >= 0:
            d = sd[p]; x = sx[p]; y = sy[p]
            p -= 1
            
            if d == 0:
                while par[x] != x:
                    par[x] = par[par[x]]
                    x = par[x]
                while par[y] != y:
                    par[y] = par[par[y]]
                    y = par[y]
                
                if x != y:
                    if sz[x] < sz[y]:
                        x, y = y, x
                    sz[x] += sz[y]
                    par[y] = x
                    res.append(x)
                    res.append(y)
            else:
                r1 = d * offset + x
                r2 = d * offset + y
                while par[r1] != r1:
                    par[r1] = par[par[r1]]
                    r1 = par[r1]
                while par[r2] != r2:
                    par[r2] = par[par[r2]]
                    r2 = par[r2]
                
                if r1 != r2:
                    if sz[r1] < sz[r2]:
                        r1, r2 = r2, r1
                    sz[r1] += sz[r2]
                    par[r2] = r1
                    
                    half = 1 << (d - 1)
                    p += 1
                    sd[p] = d - 1; sx[p] = x + half; sy[p] = y + half
                    p += 1
                    sd[p] = d - 1; sx[p] = x; sy[p] = y
                    
        return res