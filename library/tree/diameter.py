def diameter(e):
    n = len(e) 
    def bfs(s):
        d = [-1] * n
        par = [-1] * n
        que = [s]
        d[s] = 0
        for u in que:
            for v in e[u]:
                if d[v] == -1:
                    d[v] = d[u] + 1
                    par[v] = u
                    que.append(v)
        return que[-1], d, par
        
    v1, _, _ = bfs(0)
    v2, d, par = bfs(v1)
    
    path = []
    while v2 != -1:
        path.append(v2)
        v2 = par[v2]
    
    return path