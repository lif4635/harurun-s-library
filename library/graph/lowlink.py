def lowlink(edge):
    n = len(edge)
    
    parent = [-1] * n
    visited = [False] * n
    idx = 0
    for s in range(n):
        if not visited[s]:
            que = [s]
            while que:
                now = que.pop()
                if visited[now]: continue
                visited[now] = True
                for nxt in edge[now]:
                    if not visited[nxt]:
                        parent[nxt] = now
                        que.append(nxt) 
    
    order = [-1] * n
    low = [-1] * n
    is_articulation = [False] * n
    articulation = []
    bridge = []
    def dfs(s):
        idx = 0
        cnt = 0
        que = [~s,s]
        while que:
            now = que.pop()
            if now >= 0:
                order[now] = low[now] = idx
                idx += 1
                for nxt in edge[now]:
                    if parent[nxt] == now:
                        que.append(~nxt)
                        que.append(nxt)
                    elif parent[now] != nxt and order[nxt] != -1:
                        low[now] = min(low[now], order[nxt])
            else:
                now = ~now
                par = parent[now]
                if par == s: cnt += 1
                
                if now == s:
                    is_articulation[now] |= (cnt >= 2)
                    if is_articulation[now]:
                        articulation.append(now)
                    return
                
                if is_articulation[now]:
                    articulation.append(now)
                if now != parent[par]:
                    low[par] = min(low[par], low[now])
                is_articulation[par] |= (par != s) and (order[par] <= low[now])
                if order[par] < low[now]:
                    bridge.append((par, now))
    
    for i in range(n):
        if parent[i] == -1:
            dfs(i)
    
    return articulation, bridge
