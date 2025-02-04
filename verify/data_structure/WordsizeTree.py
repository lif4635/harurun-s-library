# https://judge.yosupo.jp/submission/265512

class WordsizeTree:
    """
    0 <= x < 1 << 24
    """
    def __init__(self):
        self.A = 0
        self.B = [0] * (1 << 6)
        self.C = [0] * (1 << 12)
        self.D = [0] * (1 << 18)
    
    def add(self, x):
        self.A |= 1 << (x >> 18)
        self.B[x >> 18] |= 1 << (x >> 12 & 63)
        self.C[x >> 12] |= 1 << (x >> 6 & 63) 
        self.D[x >> 6] |= 1 << (x & 63) 
    
    def discard(self, x):
        if self.D[x >> 6] & (1 << (x & 63)):
            self.D[x >> 6] &= ~(1 << (x & 63))
            if not self.D[x >> 6]:
                self.C[x >> 12] &= ~(1 << ((x >> 6) & 63))
                if not self.C[x >> 12]:
                    self.B[x >> 18] &= ~(1 << ((x >> 12) & 63))
                    if not self.B[x >> 18]:
                        self.A &= ~(1 << (x >> 18))
    
    def _in(self, x):
        return bool(self.D[x >> 6] & (1 << (x & 63)))
    
    def gt(self, x):
        x6 = x >> 6
        if self.D[x6] >> 1 >> (x & 63):
            c = self.D[x6] >> 1 >> (x & 63)
            ctz = (x & 63) + (c & -c).bit_length()
            return (x6 << 6) | ctz
        x12 = x >> 12
        if self.C[x12] >> 1 >> (x6 & 63):
            c = self.C[x12] >> 1 >> (x6 & 63)
            ctz = (x6 & 63) + (c & -c).bit_length()
            c2 = self.D[(x12 << 6) | ctz]
            ctz2 = (c2 & -c2).bit_length() - 1
            return (x12 << 12) | (ctz << 6) | ctz2
        x18 = x >> 18
        if self.B[x18] >> 1 >> (x12 & 63):
            c = self.B[x18] >> 1 >> (x12 & 63)
            ctz = (x12 & 63) + (c & -c).bit_length()
            c2 = self.C[(x18 << 6) | ctz]
            ctz2 = (c2 & -c2).bit_length() - 1
            c3 = self.D[(x18 << 12) | (ctz << 6) | ctz2]
            ctz3 = (c3 & -c3).bit_length() - 1
            return (x18 << 18) | (ctz << 12) | (ctz2 << 6) | ctz3
        if self.A >> 1 >> x18:
            c = self.A >> 1 >> x18
            ctz = x18 + (c & -c).bit_length()
            c2 = self.B[ctz]
            ctz2 = (c2 & -c2).bit_length() - 1
            c3 = self.C[(ctz << 6) | ctz2]
            ctz3 = (c3 & -c3).bit_length() - 1
            c4 = self.D[(ctz << 12) | (ctz2 << 6) | ctz3]
            ctz4 = (c4 & -c4).bit_length() - 1
            return (ctz << 18) | (ctz2 << 12) | (ctz3 << 6) | ctz4
        return -1
    
    def lt(self, x):
        x6 = x >> 6
        if self.D[x6] & ((1 << (x & 63)) - 1):
            clz = (self.D[x6] & ((1 << (x & 63)) - 1)).bit_length() - 1
            return (x6 << 6) | clz
        x12 = x >> 12
        if self.C[x12] & ((1 << (x6 & 63)) - 1):
            clz = (self.C[x12] & ((1 << (x6 & 63)) - 1)).bit_length() - 1
            clz2 = (self.D[(x12 << 6) | clz]).bit_length() - 1
            return (x12 << 12) | (clz << 6) | clz2
        x18  = x >> 18
        if self.B[x18] & ((1 << (x12 & 63)) - 1):
            clz = (self.B[x18] & ((1 << (x12 & 63)) - 1)).bit_length() - 1
            clz2 = (self.C[(x18 << 6) | clz]).bit_length() - 1
            clz3 = (self.D[(x18 << 12) | (clz << 6) | clz2]).bit_length() - 1
            return (x18 << 18) | (clz << 12) | (clz2 << 6) | clz3
        if self.A & ((1 << x18) - 1):
            clz = (self.A & ((1 << x18) - 1)).bit_length() - 1
            clz2 = (self.B[clz]).bit_length() - 1 
            clz3 = (self.C[(clz << 6) | clz2]).bit_length() - 1
            clz4 = (self.D[(clz << 12) | (clz2 << 6) | clz3]).bit_length() - 1
            return (clz << 18) | (clz2 << 12) | (clz3 << 6) | clz4
        return -1
    
    def ge(self, x):
        if x == 0:
            if self._in(0): return 0
            else: return self.gt(0)
        return self.gt(x - 1)
    
    def le(self, x):
        return self.lt(x + 1)


import io,os,sys
# input = io.BytesIO(os.read(0,os.fstat(0).st_size)).readline
input = sys.stdin.readline
II = lambda : int(input())
MI = lambda : map(int, input().split())
LI = lambda : [int(a) for a in input().split()]
SI = lambda : input().rstrip()

n,q = MI()
s = SI()
wt = WordsizeTree()
for i in range(n):
    if s[i] == "1":
        wt.add(i)

ans = []
for _ in range(q):
    c,x = MI()
    if c == 0:
        wt.add(x)
    elif c == 1:
        wt.discard(x)
    elif c == 2:
        ans.append(int(wt._in(x)))
    elif c == 3:
        ans.append(wt.ge(x))
    else:
        ans.append(wt.le(x))

os.write(1," ".join(map(str,ans)).encode())