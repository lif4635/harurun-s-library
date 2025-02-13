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
        u = que.pop()
        # u = heappop(que)
        ans.append(u)
        for v in edge[u]:
            in_deg[v] -= 1
            if in_deg[v] == 0:
                que.append(v)
                # heappush(que, v)
    return ans