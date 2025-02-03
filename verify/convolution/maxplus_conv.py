# https://judge.yosupo.jp/submission/265239
# https://judge.yosupo.jp/submission/265240

"""
monotone : argmin f(k, *) <= argmin f(k+1, *)
各行の最小値が単調に右にずれる

convex : 下に凸
concave : 上に凸
"""

def monotone_minima(h, w, select):
    """
    monotone の 最小値indexの配列
    bool select : a_(i,j) < a_(i,k) (j < k)
    """
    min_col = [0] * h
    que = [(0, h, 0, w)]
    while que:
        x1, x2, y1, y2 = que.pop()
        if x1 == x2: continue
        x = x1 + x2 >> 1
        best_y = y1
        for y in range(y1 + 1, y2):
            if select(x, best_y, y): best_y = y
        min_col[x] = best_y
        que.append((x+1, x2, best_y, y2))
        que.append((x1, x, y1, best_y+1))
    return min_col

def maxplus_convolusion_concave_concave(a, b):
    n = len(a)
    m = len(b)
    c = [0] * (n + m - 1)
    i = j = 0
    c[0] = a[0] + b[0]
    for k in range(1, n+m-1):
        if j == m-1:
            i += 1
        elif i == n-1:
            j += 1
        elif a[i+1] + b[j] > a[i] + b[j+1]:
            i += 1
        else:
            j += 1
        c[k] = a[i] + b[j]
    return c

def maxplus_convolusion_arbitrary_concave(a, b):
    n = len(a)
    m = len(b)
    def select(i, j, k):
        if i < k: return False
        if i - j >= m: return True
        return a[j] + b[i-j] <= a[k] + b[i-k]
    idx = monotone_minima(n + m - 1, n, select)
    c = [0] * (n + m - 1)
    for i , j in enumerate(idx):
        c[i] = a[j] + b[i-j]
    return c

import sys
input = sys.stdin.buffer.readline

n,m = [int(x) for x in input().split()]
a = [-int(x) for x in input().split()]
b = [-int(x) for x in input().split()]
c = maxplus_convolusion_arbitrary_concave(b, a)
print(*[-x for x in c])