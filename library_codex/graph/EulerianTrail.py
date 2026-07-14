def eulerian_trail(n, edges, directed=False, start=None):
    edges = list(edges)
    m = len(edges)
    if start is not None:
        assert 0 <= start < n
    if m == 0:
        if start is not None:
            return [start], []
        return ([0], []) if n else ([], [])

    adj = [[] for _ in range(n)]
    if directed:
        indeg = [0] * n
        outdeg = [0] * n
        for eid, (u, v) in enumerate(edges):
            assert 0 <= u < n and 0 <= v < n
            adj[u].append((v, eid))
            outdeg[u] += 1
            indeg[v] += 1
        first = -1
        last = -1
        for v in range(n):
            diff = outdeg[v] - indeg[v]
            if diff == 1:
                if first != -1:
                    return None
                first = v
            elif diff == -1:
                if last != -1:
                    return None
                last = v
            elif diff != 0:
                return None
        if (first == -1) != (last == -1):
            return None
        if start is None:
            if first != -1:
                start = first
            else:
                start = next(v for v in range(n) if outdeg[v])
        elif first != -1 and start != first:
            return None
        elif first == -1 and outdeg[start] == 0:
            return None
    else:
        degree = [0] * n
        for eid, (u, v) in enumerate(edges):
            assert 0 <= u < n and 0 <= v < n
            adj[u].append((v, eid))
            adj[v].append((u, eid))
            degree[u] += 1
            degree[v] += 1
        odd = [v for v in range(n) if degree[v] & 1]
        if len(odd) not in (0, 2):
            return None
        if start is None:
            start = odd[0] if odd else next(v for v in range(n) if degree[v])
        elif odd and start not in odd:
            return None
        elif not odd and degree[start] == 0:
            return None

    ptr = [0] * n
    used = [False] * m
    stack_v = [start]
    stack_e = []
    vertices = []
    trail = []
    while stack_v:
        u = stack_v[-1]
        au = adj[u]
        i = ptr[u]
        while i < len(au) and used[au[i][1]]:
            i += 1
        ptr[u] = i
        if i == len(au):
            vertices.append(stack_v.pop())
            if stack_e:
                trail.append(stack_e.pop())
            continue
        v, eid = au[i]
        ptr[u] = i + 1
        used[eid] = True
        stack_v.append(v)
        stack_e.append(eid)

    if len(trail) != m:
        return None
    vertices.reverse()
    trail.reverse()
    return vertices, trail


def eulerian_cycle(n, edges, directed=False, start=None):
    result = eulerian_trail(n, edges, directed, start)
    if result is None:
        return None
    if result[0] and result[0][0] != result[0][-1]:
        return None
    return result


def eulerian_trails(n, edges, directed=False):
    edges = list(edges)
    if not edges:
        return []
    parent = [-1] * n
    for u, v in edges:
        assert 0 <= u < n and 0 <= v < n
        x = u
        while parent[x] >= 0:
            x = parent[x]
        y = v
        while parent[y] >= 0:
            y = parent[y]
        if x == y:
            continue
        if parent[x] > parent[y]:
            x, y = y, x
        parent[x] += parent[y]
        parent[y] = x

    groups = {}
    for eid, (u, _) in enumerate(edges):
        while parent[u] >= 0:
            if parent[parent[u]] >= 0:
                parent[u] = parent[parent[u]]
            u = parent[u]
        groups.setdefault(u, []).append(eid)

    result = []
    for edge_ids in groups.values():
        vertices = {}
        local_edges = []
        for eid in edge_ids:
            u, v = edges[eid]
            if u not in vertices:
                vertices[u] = len(vertices)
            if v not in vertices:
                vertices[v] = len(vertices)
            local_edges.append((vertices[u], vertices[v]))
        reverse_vertices = [0] * len(vertices)
        for v, i in vertices.items():
            reverse_vertices[i] = v
        trail = eulerian_trail(len(vertices), local_edges, directed)
        if trail is None:
            return None
        path, local_ids = trail
        result.append((
            [reverse_vertices[v] for v in path],
            [edge_ids[eid] for eid in local_ids],
        ))
    return result
