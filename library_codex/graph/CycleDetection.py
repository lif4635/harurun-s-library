def find_cycle(n, edges, directed=True):
    edges = list(edges)
    adj = [[] for _ in range(n)]
    for eid, (u, v) in enumerate(edges):
        assert 0 <= u < n and 0 <= v < n
        adj[u].append((v, eid))
        if not directed:
            adj[v].append((u, eid))

    state = [0] * n
    parent = [-1] * n
    parent_edge = [-1] * n
    ptr = [0] * n
    for start in range(n):
        if state[start]:
            continue
        state[start] = 1
        stack = [start]
        while stack:
            u = stack[-1]
            if ptr[u] == len(adj[u]):
                state[u] = 2
                stack.pop()
                continue
            v, eid = adj[u][ptr[u]]
            ptr[u] += 1
            if not directed and eid == parent_edge[u]:
                continue
            if state[v] == 0:
                state[v] = 1
                parent[v] = u
                parent_edge[v] = eid
                stack.append(v)
                continue
            if state[v] != 1:
                continue

            vertices = [u]
            cycle_edges = []
            x = u
            while x != v:
                cycle_edges.append(parent_edge[x])
                x = parent[x]
                vertices.append(x)
            vertices.reverse()
            cycle_edges.reverse()
            cycle_edges.append(eid)
            return vertices, cycle_edges
    return [], []


def cycle_detection(n, edges, directed=True):
    return find_cycle(n, edges, directed)[1]
