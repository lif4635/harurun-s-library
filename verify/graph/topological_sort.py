# https://atcoder.jp/contests/abc223/submissions/62699222

from heapq import heappop,heappush

def topological_sort(edge, in_deg=None):
    """
    if len(ans) != n -> not DAG
    """
    n = len(edge)
    
    if in_deg == None:
        in_deg = [0]*n
        for u in range(n):
            for v in edge[u]:
                in_deg[v] += 1
    
    que = [i for i in range(n) if in_deg[i] == 0]
    ans = []
    while que:
        # u = que.pop()
        u = heappop(que)
        ans.append(u)
        for v in edge[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                # que.append(v)
                heappush(que, v)
    return ans

import sys
input = sys.stdin.readline
II = lambda : int(input())
MI = lambda : map(int, input().split())
MI_1 = lambda : map(lambda x:int(x)-1, input().split())

n,m = MI()
edge = [set() for i in range(n)]
for i in range(m):
    a,b = MI_1()
    edge[a].add(b)

res = topological_sort(edge)
if len(res) == n:
    print(*[i+1 for i in res])
else:
    print(-1)