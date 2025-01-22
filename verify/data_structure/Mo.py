# https://atcoder.jp/contests/abc293/submissions/61959531

from math import sqrt,ceil
class Mo:
    # qryの数を与える
    def __init__(self, n, q):
        """
        1-index, [l:r]
        self.log = 20
        size なんもわから～ん
        """
        size = ceil(2*n/sqrt(q))
        mask = 1048575
        
        self.q = q
        self.qry = [0]*q
        self.l = [0]*q
        self.r = [0]*q
        for i in range(q):
            l,r = map(int, input().split())
            #0-index, [l:r)
            self.l[i] = l-1
            self.r[i] = r
            b = l//size
            if b&1:
                self.qry[i] = b<<40 | (mask^r)<<20 | i
            else:
                self.qry[i] = b<<40 | r<<20 | i
        self.qry.sort()
        self.qry = [i&mask for i in self.qry]
    
    # add_x, del_x
    def answer(self, add_x, del_x):
        nl,nr = 0,0
        tmp = 0
        ans = [0]*self.q
        for i in self.qry:
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


import sys
MI = lambda : map(int, input().split())
LI = lambda : list(map(int, input().split()))

n,q = MI()
a = LI()
mo = Mo(n,q)

cnt = [0]*(2*10**5+1)
def add_x(x,tmp):
    c = cnt[a[x]]
    cnt[a[x]] += 1
    tmp += c*(c-1)>>1
    return tmp

def del_x(x,tmp):
    c = cnt[a[x]]
    cnt[a[x]] -= 1
    tmp -= (c-1)*(c-2)>>1
    return tmp

ans = mo.answer(add_x,del_x)

print(*ans, sep = "\n")