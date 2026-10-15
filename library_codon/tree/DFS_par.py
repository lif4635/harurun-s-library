st = [~0,0]
par = [-1] * n
while que:
    u = que.pop()
    if u >= 0:
        for v in edge[u]:
            if par[u] == v: continue
            st.append(~v)
            st.append(v)
            par[v] = u        
    else:
        u = ~u