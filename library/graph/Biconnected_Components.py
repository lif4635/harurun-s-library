def Biconnected_Components(edge):
    """
    二重連結成分：関節点で分割する
    孤立点もふくむ
    単純・連結を要求しない
    """
    n = len(edge)
    dfn = [-1] * n
    low = [-1] * n
    e_st = []
    bccs = []
    t = 0
    
    for i in range(n):
        if dfn[i] != -1:
            continue
        
        dfn[i] = low[i] = t
        t += 1
        
        if len(edge[i]) == 0:
            bccs.append([i])
            continue
        
        st = [(i, -1, 0)]
        
        while st:
            u, pe, ptr = st[-1]
            
            if ptr == len(edge[u]):
                st.pop()
                if st:
                    p = st[-1][0]
                    low[p] = min(low[p], low[u])
                    if low[u] >= dfn[p]:
                        bcc = set()
                        while True:
                            e = e_st.pop()
                            bcc.add(e[0])
                            bcc.add(e[1])
                            if e == (p, u):
                                break
                        bccs.append(list(bcc))
                continue
                
            v, idx = edge[u][ptr]
            st[-1] = (u, pe, ptr + 1)
            
            if idx == pe:
                continue
                
            if dfn[v] == -1:
                e_st.append((u, v))
                dfn[v] = low[v] = t
                t += 1
                st.append((v, idx, 0))
            elif dfn[v] < dfn[u]:
                e_st.append((u, v))
                low[u] = min(low[u], dfn[v])
                
    return bccs