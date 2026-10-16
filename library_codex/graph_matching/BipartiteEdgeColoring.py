"""二部多重グラフの辺を、同じ頂点に接する辺が異色になるよう最小色数で彩色する。"""


def _pack_vertices(degrees, limit):
    group = [-1] * len(degrees)
    totals = []
    for vertex, degree in enumerate(degrees):
        if not degree:
            continue
        if not totals or totals[-1] + degree > limit:
            totals.append(0)
        group[vertex] = len(totals) - 1
        totals[-1] += degree
    return group, totals


def _perfect_matching(size, ids, left, right):
    graph = [[] for _ in range(size)]
    for eid in ids:
        graph[left[eid]].append(eid)
    match_left = [-1] * size
    match_right = [-1] * size
    remaining = size
    for u in range(size):
        for eid in graph[u]:
            v = right[eid]
            if match_right[v] < 0:
                match_left[u] = eid
                match_right[v] = u
                remaining -= 1
                break
    while remaining:
        distance = [-1] * size
        queue = []
        for u in range(size):
            if match_left[u] < 0:
                distance[u] = 0
                queue.append(u)
        shortest = size + 1
        for u in queue:
            if distance[u] >= shortest:
                continue
            for eid in graph[u]:
                v = match_right[right[eid]]
                if v < 0:
                    shortest = distance[u] + 1
                elif distance[v] < 0:
                    distance[v] = distance[u] + 1
                    queue.append(v)
        if shortest == size + 1:
            raise ArithmeticError("regular graph has no perfect matching")
        current = [0] * size
        for root in queue:
            if match_left[root] >= 0:
                continue
            stack = [root]
            path = []
            found = -1
            while stack:
                u = stack[-1]
                choices = graph[u]
                while current[u] < len(choices):
                    eid = choices[current[u]]
                    current[u] += 1
                    v = match_right[right[eid]]
                    if v < 0:
                        if distance[u] + 1 == shortest:
                            found = eid
                            break
                    elif distance[v] == distance[u] + 1:
                        stack.append(v)
                        path.append(eid)
                        break
                else:
                    distance[u] = -1
                    stack.pop()
                    if path:
                        path.pop()
                    continue
                if found >= 0:
                    path.append(found)
                    for u, eid in zip(stack, path):
                        match_left[u] = eid
                        match_right[right[eid]] = u
                    remaining -= 1
                    break
    return match_left


def _split_edges(size, ids, left, right):
    graph = [[] for _ in range(2 * size)]
    for i, eid in enumerate(ids):
        graph[left[eid]].append(i)
        graph[size + right[eid]].append(i)
    used = bytearray(len(ids))
    halves = ([], [])
    for root in range(size):
        vertex = root
        parity = 0
        while graph[vertex]:
            i = graph[vertex].pop()
            if used[i]:
                continue
            used[i] = 1
            eid = ids[i]
            halves[parity].append(eid)
            parity ^= 1
            vertex = left[eid] + size + right[eid] - vertex
    return halves


def bipartite_edge_coloring(left_size, right_size, edges):
    """入力辺と同じ順に最小色数の色番号listを返す。多重辺も個別に彩色する。"""
    if left_size < 0 or right_size < 0:
        raise ValueError("part sizes must be nonnegative")
    edges = list(edges)
    degree_left = [0] * left_size
    degree_right = [0] * right_size
    for u, v in edges:
        if not 0 <= u < left_size or not 0 <= v < right_size:
            raise IndexError("edge endpoint is out of range")
        degree_left[u] += 1
        degree_right[v] += 1
    delta = max(max(degree_left, default=0), max(degree_right, default=0))
    if not delta:
        return []
    left_group, degree_left = _pack_vertices(degree_left, delta)
    right_group, degree_right = _pack_vertices(degree_right, delta)
    size = max(len(degree_left), len(degree_right))
    if size == 1:
        return list(range(len(edges)))
    degree_left.extend([0] * (size - len(degree_left)))
    degree_right.extend([0] * (size - len(degree_right)))
    left = [left_group[u] for u, _ in edges]
    right = [right_group[v] for _, v in edges]
    u = v = 0
    while u < size and v < size:
        if degree_left[u] == delta:
            u += 1
        elif degree_right[v] == delta:
            v += 1
        else:
            amount = min(delta - degree_left[u], delta - degree_right[v])
            left.extend([u] * amount)
            right.extend([v] * amount)
            degree_left[u] += amount
            degree_right[v] += amount
    colors = [-1] * len(edges)
    chosen = bytearray(len(left))
    stack = [(delta, list(range(len(left))), 0)]
    while stack:
        degree, ids, offset = stack.pop()
        if degree == 1:
            for eid in ids:
                if eid < len(colors):
                    colors[eid] = offset
        elif degree & 1:
            matching = _perfect_matching(size, ids, left, right)
            for eid in matching:
                chosen[eid] = 1
                if eid < len(colors):
                    colors[eid] = offset
            rest = [eid for eid in ids if not chosen[eid]]
            stack.append((degree - 1, rest, offset + 1))
        else:
            first, second = _split_edges(size, ids, left, right)
            degree //= 2
            stack.append((degree, second, offset + degree))
            stack.append((degree, first, offset))
    return colors
