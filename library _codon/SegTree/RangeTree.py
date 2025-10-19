class RangeTree:
    """
    offline query 先読み
    -> add_point
    -> bulid (pointを確定)
    (-> add_init (要素の初期化))
    -> update,prod
    library依存なし
    """
    def __init__(self, e, op, inf = 1<<32):
        self.e = e
        self.op = op
        self.points = set()
        self.inf = inf
        self.log = (inf-1).bit_length()
        self.mask = (1<<self.log) - 1

    def add_point(self, x, y):
        self.points.add((x << self.log) | y)
    
    def _merge(self, A, B):
        res = []
        al,bl = len(A),len(B)
        ap,bp = 0,0
        while ap < al and bp < bl:
            if A[ap] < B[bp]:
                res.append(A[ap])
                ap += 1
            elif A[ap] == B[bp]:
                res.append(A[ap])
                ap += 1
                bp += 1
            else:
                res.append(B[bp])
                bp += 1
        
        res += B[bp:]
        res += A[ap:]
        return res
    
    def build(self):
        self.points = sorted(self.points)
        self.pn = len(self.points)
        self.ys = [[] for _ in [0]*(self.pn*2)]
        for i in range(self.pn):
            self.ys[i + self.pn].append(self.points[i] & self.mask)
        for i in range(self.pn-1, -1, -1):
            self.ys[i] = self._merge(self.ys[i<<1], self.ys[(i<<1)|1])            
        self.len = [0] * (2*self.pn+1)
        for i in range(1, 2*self.pn+1):
            self.len[i] = self.len[i-1] + len(self.ys[i-1])
        
        self.n = self.len[-1]
        self.N0 = 2 ** (self.n - 1).bit_length()
        self.data = [self.e] * (2 * self.N0)
    
    def _bisect_left(self, lst, x):
        lo,hi = 0, len(lst)
        while lo < hi:
            mid = (lo+hi)//2
            if lst[mid] < x:
                lo = mid+1
            else:
                hi = mid
        return lo    

    def add_init(self, xyw):
        for x, y, w in xyw:
            i = self._bisect_left(self.points, (x<<self.inflog)|y) + self.pn
            while i > 0:
                self.data[self._bisect_left(self.ys[i], y) + self.le[i] + self.N0] += w
                i >>= 1
                
        for i in range(self.N0-1,0,-1):
            self.data[i] = self.op(self.data[2*i], self.data[2*i+1])
    
    def update(self, x, y, w):
        i = self._bisect_left(self.points, (x << self.log) | y)
        i += self.pn
        while i > 0:
            point = self._bisect_left(self.ys[i], y) + self.len[i]
            val = self.op(w, self.data[self.N0+point])
            point += self.N0
            self.data[point] = val
            while point > 1:
                point >>= 1
                self.data[point] = self.op(self.data[2*point], self.data[2*point+1])
            i >>= 1
    
    def prod(self, l, d, r, u):
        lres = self.e
        rres = self.e
        a = self._bisect_left(self.points, l << self.log) + self.pn
        b = self._bisect_left(self.points, r << self.log) + self.pn
        while a < b:
            if a & 1:
                al = self._bisect_left(self.ys[a], d) + self.len[a]
                ar = self._bisect_left(self.ys[a], u) + self.len[a]
                
                alres = self.e
                arres = self.e
                al += self.N0
                ar += self.N0
                while al < ar:
                    if al & 1:
                        alres = self.op(alres, self.data[al])
                        al += 1
                    if ar & 1:
                        ar -= 1
                        arres = self.op(self.data[ar], arres)
                    al >>= 1
                    ar >>= 1
                lres = self.op(lres,self.op(alres,arres))
                a += 1
            if b & 1:
                b -= 1
                bl = self._bisect_left(self.ys[b], d) + self.len[b]
                br = self._bisect_left(self.ys[b], u) + self.len[b]
                
                blres = self.e
                brres = self.e
                bl += self.N0
                br += self.N0
                while bl < br:
                    if bl & 1:
                        blres = self.op(blres, self.data[bl])
                        bl += 1
                    if br & 1:
                        br -= 1
                        brres = self.op(self.data[br], brres)
                    bl >>= 1
                    br >>= 1
                rres = self.op(self.op(blres,brres),rres)
            a >>= 1
            b >>= 1
        return self.op(lres, rres)