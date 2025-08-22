def twosat(n, clause):
    """
    n : vertex_size
    clause : list[int]
    if i >= 0: x_i = True
    else: x_{~i} = False
    """
    
    e = []
    for x in clause:
        e.append(max((x<<1)^1, ~x<<1))
    
    inf = 10 ** 9
    r = [0] * n
    st = [0] * (len(e) + n + 1) 
    pp = [0] * (len(e) + n + 1) 
    def dfs(t, u):
        p = 1
        st[p] = u
        pp[p] = u
        while p > 0:
            u = st[p]
            if u >= 0:
                if b[u]:
                    b[pp[p]] = min(b[pp[p]], b[u])
                    p -= 1
                    continue
                z[t] = u
                t += 1
                b[u] = t
                st[p] = ~st[p]
                for i in reversed(range(s[u], s[u+1])):
                    if not b[q[i]]:
                        p += 1
                        st[p] = q[i]
                        pp[p] = u
                    else:
                        b[u] = min(b[u], b[q[i]])
            else:
                u = ~u
                if u == z[b[u] - 1]:
                    while b[u] <= t:
                        t -= 1
                        b[z[t]] = inf + u
                        r[z[t]>>1] = z[t] & 1
                b[pp[p]] = min(b[pp[p]], b[u])
                p -= 1
        return t
    
    s = [0] * (2 * n + 1)
    b = [0] * (2 * n + 1)
    z = [0] * (2 * n + 1)
    q = e.copy()
    for x in e: s[x] += 1
    for i in range(2 * n): s[i+1] += s[i]
    for i in range(len(e)):
        s[e[i]] -= 1
        q[s[e[i]]] = e[i^1]^1
    t = 0
    for i in range(0, 2*n, 2):
        if not b[i]: t = dfs(t, i)
        if b[i] == b[i^1]:
            return None
    return r