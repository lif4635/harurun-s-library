"""Small-graph optimization and sparse-graph enumeration algorithms.

All searches use explicit stacks.  The graph arguments named ``graph`` are
undirected adjacency lists.  Triangle and C4 routines assume a loopless simple
graph, as do their reference-library counterparts.
"""


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


def graph_from_edges(n, edges):
    """Build an undirected adjacency list from pairs."""
    graph = [[] for _ in range(n)]
    for u, v in edges:
        if u != v:
            graph[u].append(v)
            graph[v].append(u)
    return graph


def _mask_vertices(mask):
    vertices = []
    while mask:
        bit = mask & -mask
        vertices.append(bit.bit_length() - 1)
        mask ^= bit
    return vertices


def chromatic_number(graph, exact=False):
    """Return the chromatic number in O(n 2^n) time and O(2^n) memory.

    The fast default evaluates the inclusion-exclusion formula modulo two
    primes, as common competitive-programming implementations do.  Set
    ``exact=True`` to use arbitrary-precision integer sums with no possibility
    of a modular collision.
    """
    n = len(graph)
    if n == 0:
        return 0
    adj = _adjacency_masks(graph)
    size = 1 << n
    independent = [0] * size
    independent[0] = 1
    for mask in range(1, size):
        bit = mask & -mask
        v = bit.bit_length() - 1
        rest = mask ^ bit
        independent[mask] = independent[rest] + independent[rest & ~adj[v]]

    hist = {}
    parity = n & 1
    for mask, count in enumerate(independent):
        sign = -1 if ((mask.bit_count() & 1) ^ parity) else 1
        hist[count] = hist.get(count, 0) + sign
    terms = [(count, coefficient) for count, coefficient in hist.items()
             if coefficient]

    if exact:
        powers = [coefficient for _, coefficient in terms]
        for colors in range(1, n + 1):
            total = 0
            for i, (count, _) in enumerate(terms):
                value = powers[i] * count
                powers[i] = value
                total += value
            if total:
                return colors
        return n

    mod0 = 1_000_000_021
    mod1 = 1_000_000_033
    power0 = [coefficient % mod0 for _, coefficient in terms]
    power1 = [coefficient % mod1 for _, coefficient in terms]
    for colors in range(1, n + 1):
        total0 = total1 = 0
        for i, (count, _) in enumerate(terms):
            value0 = power0[i] * count % mod0
            value1 = power1[i] * count % mod1
            power0[i] = value0
            power1[i] = value1
            total0 += value0
            total1 += value1
        if total0 % mod0 or total1 % mod1:
            return colors
    return n


def chromatic_number_from_edges(n, edges, exact=False):
    return chromatic_number(graph_from_edges(n, edges), exact)


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


def enumerate_triangles(n, edges, callback=None):
    """Enumerate triangles in O(n + m sqrt(m)) time.

    Each item is ``(u, v, w, uv_edge, uw_edge, vw_edge)``.  If ``callback`` is
    given it is invoked for each item and the count is returned; otherwise a
    list is returned.
    """
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    high = [[] for _ in range(n)]
    for edge_id, (u, v) in enumerate(edges):
        if (degree[u], u) < (degree[v], v):
            high[u].append((v, edge_id))
        else:
            high[v].append((u, edge_id))
    marked = [-1] * n
    result = [] if callback is None else None
    count = 0
    for u in range(n):
        for v, edge_id in high[u]:
            marked[v] = edge_id
        for v, uv_edge in high[u]:
            for w, vw_edge in high[v]:
                uw_edge = marked[w]
                if uw_edge != -1:
                    item = (u, v, w, uv_edge, uw_edge, vw_edge)
                    if callback is None:
                        result.append(item)
                    else:
                        callback(*item)
                    count += 1
        for v, _ in high[u]:
            marked[v] = -1
    return result if callback is None else count


def enumerate_cliques(graph, callback=None, include_empty=False):
    """Enumerate every clique once without recursion.

    Cliques are returned as vertex lists.  Supplying a callback avoids storing
    the potentially exponential output; in that mode the number of cliques is
    returned.
    """
    n = len(graph)
    adj = _adjacency_masks(graph)
    result = [] if callback is None else None
    count = 0
    if include_empty:
        if callback is None:
            result.append([])
        else:
            callback([])
        count = 1
    universe = (1 << n) - 1
    for first in range(n):
        bit = 1 << first
        stack = [(bit, adj[first] & (universe ^ ((bit << 1) - 1)))]
        while stack:
            clique, candidates = stack.pop()
            vertices = _mask_vertices(clique)
            if callback is None:
                result.append(vertices)
            else:
                callback(vertices)
            count += 1
            rest = candidates
            while rest:
                nxt_bit = rest & -rest
                nxt = nxt_bit.bit_length() - 1
                rest ^= nxt_bit
                stack.append((clique | nxt_bit, rest & adj[nxt]))
    return result if callback is None else count


def count_c4_per_edge(n, edges, weight=None):
    """For each edge, sum products of the other three edges over all C4s.

    With omitted weights this is simply the number of (not necessarily induced)
    4-cycles containing each edge.  Runs in O(n + m sqrt(m)) on a simple graph.
    """
    m = len(edges)
    if weight is None:
        weight = [1] * m
    elif len(weight) != m:
        raise ValueError("weight length must equal the number of edges")
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    order = sorted(range(n), key=lambda v: degree[v])
    rank = [0] * n
    for i, v in enumerate(order):
        rank[v] = i
    transformed = []
    for u, v in edges:
        u = rank[u]
        v = rank[v]
        if u < v:
            u, v = v, u
        transformed.append((u, v))

    start = [0] * n
    for v in range(n - 1):
        start[v + 1] = start[v] + degree[order[v]]
    end = start[:]
    edge_id = [0] * (m << 1)
    to = [0] * (m << 1)
    for e, (v, w) in enumerate(transformed):
        i = end[v]
        edge_id[i] = e
        to[i] = w
        end[v] = i + 1
    directed_end = end[:]
    for v in range(n):
        for i in range(start[v], directed_end[v]):
            e = edge_id[i]
            w = to[i]
            j = end[w]
            edge_id[j] = e
            to[j] = v
            end[w] = j + 1

    path_sum = [0] * n
    answer = [0] * m
    for v in range(n - 1, -1, -1):
        for i in range(start[v], end[v]):
            evw = edge_id[i]
            w = to[i]
            end[w] -= 1
            for j in range(start[w], end[w]):
                ewx = edge_id[j]
                x = to[j]
                path_sum[x] += weight[evw] * weight[ewx]
        for i in range(start[v], end[v]):
            evw = edge_id[i]
            w = to[i]
            for j in range(start[w], end[w]):
                ewx = edge_id[j]
                x = to[j]
                value = path_sum[x] - weight[evw] * weight[ewx]
                answer[evw] += value * weight[ewx]
                answer[ewx] += value * weight[evw]
        for i in range(start[v], end[v]):
            w = to[i]
            for j in range(start[w], end[w]):
                path_sum[to[j]] = 0
    return answer
