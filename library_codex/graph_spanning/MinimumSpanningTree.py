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


def second_spanning_tree(n, edges, strict=False):
    """MSTと辺集合が異なる最小costの全域木を1本求める。"""
    edges = list(edges)
    result = minimum_spanning_tree(n, edges)
    if result is None or n <= 1:
        return None
    mst_cost, selected = result
    selected_set = set(selected)
    tree = [[] for _ in range(n)]
    for edge_id in selected:
        first, second, weight = edges[edge_id]
        tree[first].append((second, weight, edge_id))
        tree[second].append((first, weight, edge_id))

    levels = max(1, n.bit_length())
    parent = [[-1] * n for _ in range(levels)]
    largest = [[()] * n for _ in range(levels)]
    depth = [0] * n
    order = [0]
    for vertex in order:
        for other, weight, edge_id in tree[vertex]:
            if other == parent[0][vertex]:
                continue
            parent[0][other] = vertex
            largest[0][other] = ((weight, edge_id),)
            depth[other] = depth[vertex] + 1
            order.append(other)

    def merge(first, second):
        by_weight = {}
        for weight, edge_id in first + second:
            old = by_weight.get(weight)
            if old is None or edge_id < old:
                by_weight[weight] = edge_id
        return tuple(sorted(
            ((weight, edge_id) for weight, edge_id in by_weight.items()),
            reverse=True,
        )[:2])

    for level in range(1, levels):
        old_parent = parent[level - 1]
        current_parent = parent[level]
        for vertex in range(n):
            middle = old_parent[vertex]
            if middle >= 0:
                current_parent[vertex] = old_parent[middle]
                largest[level][vertex] = merge(
                    largest[level - 1][vertex], largest[level - 1][middle]
                )

    def path_largest(first, second):
        values = ()
        if depth[first] < depth[second]:
            first, second = second, first
        difference = depth[first] - depth[second]
        level = 0
        while difference:
            if difference & 1:
                values = merge(values, largest[level][first])
                first = parent[level][first]
            difference >>= 1
            level += 1
        if first == second:
            return values
        for level in range(levels - 1, -1, -1):
            if parent[level][first] != parent[level][second]:
                values = merge(values, largest[level][first])
                values = merge(values, largest[level][second])
                first = parent[level][first]
                second = parent[level][second]
        values = merge(values, largest[0][first])
        return merge(values, largest[0][second])

    best = None
    for edge_id, (first, second, weight) in enumerate(edges):
        if edge_id in selected_set or first == second:
            continue
        candidates = path_largest(first, second)
        removed = None
        for old_weight, old_edge_id in candidates:
            candidate_cost = mst_cost + weight - old_weight
            if not strict or candidate_cost > mst_cost:
                removed = old_edge_id
                candidate = (candidate_cost, edge_id, old_edge_id)
                break
        if removed is not None and (best is None or candidate < best):
            best = candidate
    if best is None:
        return None
    second_cost, added, removed = best
    second_edges = [edge_id for edge_id in selected if edge_id != removed]
    second_edges.append(added)
    second_edges.sort()
    return mst_cost, second_cost, selected, second_edges, added, removed


def manhattan_mst(points):
    """Return ``(cost, vertex_pairs)`` of a Manhattan MST in O(N log N)."""
    from library_codex.ordered_set.TreapSet import TreapSet

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
