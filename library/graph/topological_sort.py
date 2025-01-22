def topological_sort(edge, inedge=None):
    """
    if len(ans) != n -> not DAG
    """
    n = len(edge)
    
    if inedge == None:
        inedge = [0]*n
        for v in range(n):
            for adj in edge[v]:
                inedge[adj] += 1
    
    ans = [i for i in range(n) if inedge[i] == 0]
    que = deque(ans)
    while que:
        q = que.popleft()
        for e in edge[q]:
            inedge[e] -= 1
            if inedge[e] == 0:
                que.append(e)
                ans.append(e)
    return ans
