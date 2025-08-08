def rerooted(edge, id, up, add, merge):
    """
    edge : adj_list
    up : treelist * vertex -> tree
    add : treelist * tree -> treelist
    merge : treelist * treelist -> treelist
    
    low : treelist ( sub[u] \ { u } )
    hi : tree ( S \ sub[u] )
    sub : tree ( sub[u] )
    """
    
    par = [-1] * n
    chi = [[] for i in range(n)]
    topo = []
    st = [0]
    while st:
        u = st.pop()
        topo.append(u)
        for v in edge[u]:
            if par[u] == v: continue
            par[v] = u
            chi[u].append(v)
            st.append(v)
    
    low = [id] * n
    hi = [id] * n
    sub = [id] * n
    
    for u in reversed(topo):
        for v in chi[u]:
            low[u] = add(low[u], sub[v])
        sub[u] = up(low[u], u)

    for u in topo:
        suf = add(id, hi[u]) # treelist
        for v in reversed(chi[u]):
            hi[v] = suf
            suf = add(suf, sub[v])
        pre = id # treelist
        for v in chi[u]:
            hi[v] = up(merge(hi[v], pre), u)
            pre = add(pre, sub[v])
    
    ans = [up(add(low[u], hi[u]), u) for u in range(n)]
    return ans