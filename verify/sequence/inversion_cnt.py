# https://atcoder.jp/contests/chokudai_S001/submissions/61959984

class BIT:
    def __init__(self, n):
        self.n = n
        self.data = [0]*(n+1)
    
    def build(self, arr):
        for i,a in enumerate(arr):
            self.data[i+1] = a
        for i in range(1, self.n+1):
            if i + (i&-i) <= self.n:
                self.data[i + (i&-i)] += self.data[i]
    
    def add(self, p, x):
        p += 1
        while p <= self.n:
            self.data[p] += x
            p += p& -p
    
    def sum0(self, r):
        s = 0
        while r:
            s += self.data[r]
            r -= r& -r
        return s
    
    def sum(self, l, r):
        s = 0
        while r:
            s += self.data[r]
            r -= r& -r
        while l:
            s -= self.data[l]
            l -= l& -l
        return s
    
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
        ans[i] = ft.sum(lst[i],n+10)
        ft.add(lst[i], 1)
    
    return ans

import sys
input = sys.stdin.readline
LI = lambda : list(map(int, input().split()))
n = int(input())
a = LI()
print(sum(inversion_cnt(a)))