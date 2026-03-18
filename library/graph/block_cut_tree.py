def bccs(adj):
    n = len(adj)
    dfn = [-1] * n
    low = [-1] * n
    edge_stack = []
    bccs = []
    timer = 0
    
    dfn[0] = low[0] = timer
    timer += 1
    stack = [(0, -1, iter(adj[0]))]
    
    while stack:
        u, p, it = stack[-1]
        try:
            v = next(it)
            if v == p:
                continue
            if dfn[v] == -1:
                edge_stack.append((u, v))
                dfn[v] = low[v] = timer
                timer += 1
                stack.append((v, u, iter(adj[v])))
            elif dfn[v] < dfn[u]:
                edge_stack.append((u, v))
                low[u] = min(low[u], dfn[v])
        except StopIteration:
            stack.pop()
            if stack:
                parent = stack[-1][0]
                low[parent] = min(low[parent], low[u])
                if low[u] >= dfn[parent]:
                    bcc = set()
                    while True:
                        e = edge_stack.pop()
                        bcc.add(e[0])
                        bcc.add(e[1])
                        if e == (parent, u):
                            break
                    bccs.append(list(bcc))
                    
    return bccs