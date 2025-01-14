"""
いろいろな改善の余地があります
定数倍との兼ね合いで許容できるところは削るイメージで
"""
from math import isqrt
class Mo:
    # qryの数を与える
    def __init__(self, n, q):
        """
        1-index, [l:r]
        self.log = 20
        """
        size = 2*n//isqrt(q) + 1
        
        self.half = n>>1
        self.q = q
        self.qry = [[] for i in range(n//size + 1)]
        self.l = [0]*q
        self.r = [0]*q
        for i in range(q):
            l,r = map(int, input().split())
            #0-index, [l:r)
            self.l[i] = l-1
            self.r[i] = r
            self.qry[l//size].append(r<<20 | i)
    
    # add_x, del_x
    def answer(self, add_x, del_x):
        nl,nr = 0,0
        tmp = 0
        ans = [0]*q
        for qry_block in self.qry:
            if qry_block == []: continue
            qry_block.sort(reverse = (self.half - nr < 0))
            for i in qry_block:
                i &= 1048575
                l = self.l[i]
                r = self.r[i]
                while nl > l:
                    nl -= 1
                    tmp = add_x(nl,tmp)
                while nr < r:
                    tmp = add_x(nr,tmp)
                    nr += 1
                while nl < l:
                    tmp = del_x(nl,tmp)
                    nl += 1
                while nr > r:
                    nr -= 1
                    tmp = del_x(nr,tmp)
                ans[i] = tmp
        return ans
