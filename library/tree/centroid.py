def centroid(e):
    n = len(e) 
    par = [-1] * n
    st = [0]
    order = []
    while st:
        u = st.pop()
        order.append(u)
        for v in e[u]:
            if v != par[u]:
                par[v] = u
                st.append(v)
    
    siz = [1] * n
    
    centroids = []
    for u in reversed(order):
        f = 1
        if v != par[u]:
            siz[u] += siz[v]
            if siz[v] > n // 2:
                f = 0
        if n - siz[u] > n // 2:
            f = 0
        if f:
            centroids.append(u)
    
    return centroids