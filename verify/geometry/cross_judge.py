# https://atcoder.jp/contests/past16-open/tasks/past202309_m

def cross_judge(a, b, c, d, touch = True):
    """
    ab と cd の交差判定
    """
    ax,ay = a
    bx,by = b
    cx,cy = c
    dx,dy = d
    
    if touch:
        if min(ax,bx) > max(cx,dx): return False
        if min(cx,dx) > max(ax,bx): return False
        if min(ay,by) > max(cy,dy): return False
        if min(cy,dy) > max(ay,by): return False
        t1 = (ax-bx)*(cy-ay) + (ay-by)*(ax-cx)
        t2 = (ax-bx)*(dy-ay) + (ay-by)*(ax-dx)
        s1 = (cx-dx)*(ay-cy) + (cy-dy)*(cx-ax)
        s2 = (cx-dx)*(by-cy) + (cy-dy)*(cx-bx)
        return t1*t2 <= 0 and s1*s2 <= 0
    else:
        if min(ax,bx) >= max(cx,dx): return False
        if min(cx,dx) >= max(ax,bx): return False
        if min(ay,by) >= max(cy,dy): return False
        if min(cy,dy) >= max(ay,by): return False
        t1 = (ax-bx)*(cy-ay) + (ay-by)*(ax-cx)
        t2 = (ax-bx)*(dy-ay) + (ay-by)*(ax-dx)
        s1 = (cx-dx)*(ay-cy) + (cy-dy)*(cx-ax)
        s2 = (cx-dx)*(by-cy) + (cy-dy)*(cx-bx)
        return t1*t2 < 0 and s1*s2 < 0

import sys
input = sys.stdin.readline
MI = lambda : map(int, input().split())
a,b,c,d = MI()
p,q = (a,b),(c,d)
a,b,c,d = MI()
r,s = (a,b),(c,d)
print("Yes" if cross_judge(p,q,r,s) else "No")