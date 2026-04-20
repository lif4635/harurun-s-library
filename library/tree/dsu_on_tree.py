def dsu_on_tree(e, add, qry):
    s = [1] * n
    par = [-1] * n
    heavy = [-1] * n
    st = [~0, 0]
    while st:
        u = st.pop()
        if u >= 0:
            if par[u] in e[u]: e[u].remove(par[u])
            for v in e[u]:
                par[v] = u
                st.append(~v)
                st.append(v)
        else:
            u = ~u
            for v in e[u]:
                if heavy[u] == -1 or s[v] > s[heavy[u]]:
                    heavy[u] = v 
            
            if par[u] != -1: s[par[u]] += s[u]
            
    in_t, out_t, vs = [0] * n, [0] * n, [0] * n
    ti = 0
    st = [0]
    while st:
        u = st.pop()
        if u >= 0:
            vs[ti] = u
            in_t[u] = ti
            ti += 1
            for v in e[u]:
                st.append(~v)
                st.append(v) 
        else:
            out_t[~u] = ti
    
    st = [(~0, 1), (0, 1)]
    while st:
        u, keep = st.pop()
        if u >= 0:
            if heavy[u] != -1:
                st.append((~heavy[u], 1))
                st.append((heavy[u], 1))
            for v in e[u]:
                if v != heavy[u]:
                    st.append((~v, 0))
                    st.append((v, 0))
        else:
            u = ~u
            add(u, 1)
            for v in e[u]:
                if v != heavy[u]:
                    for i in range(in_t[v], out_t[v]):
                        add(vs[i], 1)
        
            qry(u)
            
            if not keep:
                for i in range(in_t[u], out_t[u]):
                    add(vs[i], -1)