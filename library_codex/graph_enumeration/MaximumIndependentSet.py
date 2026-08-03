"""小規模グラフの最大独立集合と最大重み独立集合を求める。"""

def _adjacency_masks(graph):
    n = len(graph)
    adj = [0] * n
    for v in range(n):
        a = 0
        for u in graph[v]:
            if u != v:
                a |= 1 << u
        adj[v] = a
    return adj

def _mask_vertices(mask):
    vertices = []
    while mask:
        bit = mask & -mask
        vertices.append(bit.bit_length() - 1)
        mask ^= bit
    return vertices

def _color_sort(candidates, adjacency):
    """Greedy coloring bound for a maximum-clique search."""
    order = []
    bound = []
    rest = candidates
    color = 0
    while rest:
        color += 1
        available = rest
        while available:
            bit = available & -available
            v = bit.bit_length() - 1
            order.append(v)
            bound.append(color)
            rest ^= bit
            available ^= bit
            available &= ~adjacency[v]
    return order, bound

def maximum_independent_set_mask(graph):
    """Return ``(cardinality, vertex_mask)`` of an exact maximum IS.

    This is an iterative maximum-clique search in the complement graph with a
    greedy-coloring upper bound.  It is intended for small or moderately sparse
    exponential instances.
    """
    n = len(graph)
    if n == 0:
        return 0, 0
    original = _adjacency_masks(graph)
    universe = (1 << n) - 1
    adjacency = [universe ^ (1 << v) ^ original[v] for v in range(n)]

    # A cheap lower bound improves pruning before the first leaf is visited.
    candidates = universe
    best_mask = 0
    while candidates:
        bit = candidates & -candidates
        v = bit.bit_length() - 1
        best_mask |= bit
        candidates &= adjacency[v]
    best = best_mask.bit_count()

    order, bound = _color_sort(universe, adjacency)
    # frame: [remaining candidates, size, chosen mask, order, bounds, index]
    stack = [[universe, 0, 0, order, bound, len(order) - 1]]
    while stack:
        frame = stack[-1]
        i = frame[5]
        if i < 0 or frame[1] + frame[4][i] <= best:
            stack.pop()
            continue
        v = frame[3][i]
        bit = 1 << v
        frame[5] = i - 1
        frame[0] &= ~bit
        chosen = frame[2] | bit
        size = frame[1] + 1
        nxt = frame[0] & adjacency[v]
        if not nxt:
            if size > best:
                best = size
                best_mask = chosen
            continue
        child_order, child_bound = _color_sort(nxt, adjacency)
        if size + child_bound[-1] > best:
            stack.append([nxt, size, chosen, child_order, child_bound,
                          len(child_order) - 1])
    return best, best_mask

def maximum_independent_set(graph):
    """Return the vertices of an exact maximum independent set."""
    _, mask = maximum_independent_set_mask(graph)
    return _mask_vertices(mask)

def maximum_weight_independent_set(graph, weight):
    """Return ``(maximum_weight, vertex_mask)`` by iterative branch-and-bound.

    Empty selection is allowed, so vertices with nonpositive weight can be
    discarded immediately.  This routine is exact but exponential.
    """
    n = len(graph)
    if len(weight) != n:
        raise ValueError("weight length must equal the number of vertices")
    adj = _adjacency_masks(graph)
    candidates = 0
    for v, w in enumerate(weight):
        if w > 0:
            candidates |= 1 << v
    best_weight = 0
    best_mask = 0
    stack = [(candidates, 0, 0)]
    while stack:
        p, current, chosen = stack.pop()
        upper = current
        bits = p
        while bits:
            bit = bits & -bits
            upper += weight[bit.bit_length() - 1]
            bits ^= bit
        if upper <= best_weight:
            continue
        if not p:
            best_weight = current
            best_mask = chosen
            continue
        # A high induced degree tends to shrink the include branch quickly.
        bits = p
        vertex = -1
        degree = -1
        while bits:
            bit = bits & -bits
            v = bit.bit_length() - 1
            d = (adj[v] & p).bit_count()
            if d > degree:
                degree = d
                vertex = v
            bits ^= bit
        bit = 1 << vertex
        rest = p ^ bit
        stack.append((rest, current, chosen))
        stack.append((rest & ~adj[vertex], current + weight[vertex],
                      chosen | bit))
    return best_weight, best_mask

