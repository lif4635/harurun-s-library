def monge_shortest_path(n, cost):
    inf = 1001001001001001001
    dis = [inf] * n
    dis[0] = 0
    amin = [0]*n
    
    def update(i, k):
        if i <= k: return
        nd = dis[k] + cost(k, i)
        if nd < dis[i]:
            dis[i] = nd
            amin[i] = k
    
    que = [(0,n-1,-1)]
    while que:
        l,r,f = que.pop()
        if f == -1:
            m = l + r >> 1
            for k in range(amin[l], amin[r] + 1):
                update(m, k)
            que.append((l,r,m))
            if l + 1 != m: que.append((l,m,-1))
        else:
            m = f
            for k in range(l + 1, r + 1):
                update(r, k)
            if m + 1 != r: que.append((m,r,-1))
    return dis