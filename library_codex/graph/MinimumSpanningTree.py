def minimum_spanning_forest(n, edges):
    edges = list(edges)
    parent = [-1] * n
    order = sorted(range(len(edges)), key=lambda i: edges[i][2])
    selected = []
    cost = 0
    components = n

    for eid in order:
        u, v, w = edges[eid]
        x = u
        while parent[x] >= 0:
            if parent[parent[x]] >= 0:
                parent[x] = parent[parent[x]]
            x = parent[x]
        y = v
        while parent[y] >= 0:
            if parent[parent[y]] >= 0:
                parent[y] = parent[parent[y]]
            y = parent[y]
        if x == y:
            continue
        if parent[x] > parent[y]:
            x, y = y, x
        parent[x] += parent[y]
        parent[y] = x
        cost += w
        selected.append(eid)
        components -= 1
        if components == 1:
            break
    return cost, selected, components


def minimum_spanning_tree(n, edges):
    cost, selected, components = minimum_spanning_forest(n, edges)
    if components > 1:
        return None
    return cost, selected


def kruskal(n, edges):
    return minimum_spanning_forest(n, edges)[0]


def manhattan_mst(points):
    """Return ``(cost, vertex_pairs)`` of a Manhattan MST in O(N log N)."""
    from library_codex.data_structure.Collections import TreapSet

    n = len(points)
    if n <= 1:
        return 0, []
    x = [point[0] for point in points]
    y = [point[1] for point in points]
    order = list(range(n))
    candidates = []
    for outer in range(2):
        for _ in range(2):
            order.sort(key=lambda i: x[i] + y[i])
            sweep = TreapSet()
            at_key = {}
            for i in order:
                threshold = -y[i]
                key = sweep.ge(threshold)
                while key is not None:
                    j = at_key[key]
                    if x[i] - x[j] < y[i] - y[j]:
                        break
                    candidates.append((
                        abs(x[i] - x[j]) + abs(y[i] - y[j]), i, j
                    ))
                    sweep.discard(key)
                    key = sweep.ge(threshold)
                at_key[threshold] = i
                sweep.add(threshold)
            x, y = y, x
        x = [-value for value in x]
    parent = [-1] * n

    def find(v):
        root = v
        while parent[root] >= 0:
            root = parent[root]
        while v != root:
            to = parent[v]
            parent[v] = root
            v = to
        return root

    answer = []
    cost = 0
    for weight, first, second in sorted(candidates):
        u = find(first)
        v = find(second)
        if u == v:
            continue
        if parent[u] > parent[v]:
            u, v = v, u
        parent[u] += parent[v]
        parent[v] = u
        cost += weight
        answer.append((first, second))
        if len(answer) == n - 1:
            break
    return cost, answer
