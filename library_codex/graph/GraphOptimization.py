"""Nonrecursive graph optimization routines for small/special instances."""

from heapq import heappop, heappush


def hungarian(cost):
    """Minimum-cost injection from rows to columns.

    Returns ``(minimum_cost, assignment)`` where ``assignment[i]`` is the
    column matched to row ``i``.  Requires ``rows <= columns`` and supports
    negative integer or floating-point costs.  Complexity is O(R^2 C).
    """
    rows = len(cost)
    if rows == 0:
        return 0, []
    columns = len(cost[0])
    if columns < rows:
        raise ValueError("hungarian requires rows <= columns")
    if any(len(row) != columns for row in cost):
        raise ValueError("cost matrix must be rectangular")
    u = [0] * (rows + 1)
    v = [0] * (columns + 1)
    matching = [0] * (columns + 1)
    way = [0] * (columns + 1)
    for i in range(1, rows + 1):
        matching[0] = i
        min_value = [float("inf")] * (columns + 1)
        used = [False] * (columns + 1)
        column = 0
        while True:
            used[column] = True
            row = matching[column]
            delta = float("inf")
            next_column = 0
            row_cost = cost[row - 1]
            for j in range(1, columns + 1):
                if not used[j]:
                    current = row_cost[j - 1] - u[row] - v[j]
                    if current < min_value[j]:
                        min_value[j] = current
                        way[j] = column
                    if min_value[j] < delta:
                        delta = min_value[j]
                        next_column = j
            for j in range(columns + 1):
                if used[j]:
                    u[matching[j]] += delta
                    v[j] -= delta
                else:
                    min_value[j] -= delta
            column = next_column
            if matching[column] == 0:
                break
        while column:
            previous = way[column]
            matching[column] = matching[previous]
            column = previous
    assignment = [-1] * rows
    for column in range(1, columns + 1):
        row = matching[column]
        if row:
            assignment[row - 1] = column - 1
    return -v[0], assignment


def hungarian_max(cost):
    """Maximum-cost injection from rows to columns."""
    value, assignment = hungarian([[-x for x in row] for row in cost])
    return -value, assignment


def minimum_steiner_tree(n, edges, terminals):
    """Return ``(cost, edge_ids)`` of a minimum undirected Steiner tree.

    Edges are ``(u, v, nonnegative_weight)``.  Complexity is
    O(3^K N + 2^K (N+M) log N), where K is the number of distinct terminals.
    If the terminals cannot be connected, ``(inf, [])`` is returned.
    """
    terminals = list(dict.fromkeys(terminals))
    k = len(terminals)
    if k <= 1:
        return 0, []
    graph = [[] for _ in range(n)]
    for edge_id, (u, v, weight) in enumerate(edges):
        if weight < 0:
            raise ValueError("Steiner Dijkstra requires nonnegative weights")
        graph[u].append((v, weight, edge_id))
        graph[v].append((u, weight, edge_id))
    inf = float("inf")
    size = 1 << k
    dp = [[inf] * n for _ in range(size)]
    previous = [[None] * n for _ in range(size)]
    for i, terminal in enumerate(terminals):
        dp[1 << i][terminal] = 0

    for mask in range(1, size):
        sub = (mask - 1) & mask
        while sub:
            other = mask ^ sub
            if other and sub < other:
                left = dp[sub]
                right = dp[other]
                current = dp[mask]
                for v in range(n):
                    value = left[v] + right[v]
                    if value < current[v]:
                        current[v] = value
                        previous[mask][v] = (sub, -1)
            sub = (sub - 1) & mask
        distance = dp[mask]
        heap = [(value, v) for v, value in enumerate(distance) if value < inf]
        # heapify is faster than n pushes on dense states.
        if len(heap) > 1:
            from heapq import heapify
            heapify(heap)
        while heap:
            dist, v = heappop(heap)
            if distance[v] != dist:
                continue
            for to, weight, edge_id in graph[v]:
                nxt = dist + weight
                if nxt < distance[to]:
                    distance[to] = nxt
                    previous[mask][to] = (v, edge_id)
                    heappush(heap, (nxt, to))

    full = size - 1
    root = min(range(n), key=dp[full].__getitem__)
    answer = dp[full][root]
    if answer == inf:
        return inf, []
    selected = set()
    stack = [(full, root)]
    while stack:
        mask, v = stack.pop()
        state = previous[mask][v]
        if state is None:
            continue
        value, edge_id = state
        if edge_id == -1:
            stack.append((value, v))
            stack.append((mask ^ value, v))
        else:
            selected.add(edge_id)
            stack.append((mask, value))
    return answer, list(selected)


def steiner_tree_dp(n, edges, terminals):
    """Return only the standard subset DP table for Steiner tree costs."""
    terminals = list(dict.fromkeys(terminals))
    k = len(terminals)
    graph = [[] for _ in range(n)]
    for u, v, weight in edges:
        if weight < 0:
            raise ValueError("Steiner Dijkstra requires nonnegative weights")
        graph[u].append((v, weight))
        graph[v].append((u, weight))
    inf = float("inf")
    dp = [[inf] * n for _ in range(1 << k)]
    for i, terminal in enumerate(terminals):
        dp[1 << i][terminal] = 0
    for mask in range(1, 1 << k):
        sub = (mask - 1) & mask
        while sub:
            other = mask ^ sub
            if other and sub < other:
                a, b, c = dp[sub], dp[other], dp[mask]
                for v in range(n):
                    value = a[v] + b[v]
                    if value < c[v]:
                        c[v] = value
            sub = (sub - 1) & mask
        distance = dp[mask]
        heap = [(value, v) for v, value in enumerate(distance) if value < inf]
        if len(heap) > 1:
            from heapq import heapify
            heapify(heap)
        while heap:
            dist, v = heappop(heap)
            if distance[v] != dist:
                continue
            for to, weight in graph[v]:
                nxt = dist + weight
                if nxt < distance[to]:
                    distance[to] = nxt
                    heappush(heap, (nxt, to))
    return dp


def held_karp_path(distance, start=None, goal=None, restore=False):
    """Minimum Hamiltonian path cost, optionally fixing either endpoint.

    ``distance[u][v]`` is the direct transition cost; no metric closure is
    performed.  Returns the cost, or ``(cost, vertex_order)`` with
    ``restore=True``.  Complexity is O(N^2 2^N).
    """
    n = len(distance)
    if n == 0:
        return (0, []) if restore else 0
    if any(len(row) != n for row in distance):
        raise ValueError("distance matrix must be square")
    inf = float("inf")
    size = 1 << n
    dp = [[inf] * n for _ in range(size)]
    parent = [[-1] * n for _ in range(size)] if restore else None
    if start is None:
        for v in range(n):
            dp[1 << v][v] = 0
    else:
        dp[1 << start][start] = 0
    for mask in range(1, size):
        remaining = (size - 1) ^ mask
        bits = mask
        while bits:
            bit = bits & -bits
            v = bit.bit_length() - 1
            value = dp[mask][v]
            if value < inf:
                nxt_bits = remaining
                row = distance[v]
                while nxt_bits:
                    nxt_bit = nxt_bits & -nxt_bits
                    to = nxt_bit.bit_length() - 1
                    nxt_mask = mask | nxt_bit
                    candidate = value + row[to]
                    if candidate < dp[nxt_mask][to]:
                        dp[nxt_mask][to] = candidate
                        if restore:
                            parent[nxt_mask][to] = v
                    nxt_bits ^= nxt_bit
            bits ^= bit
    full = size - 1
    if goal is None:
        end = min(range(n), key=dp[full].__getitem__)
    else:
        end = goal
    answer = dp[full][end]
    if not restore:
        return answer
    if answer == inf:
        return inf, []
    order = []
    mask = full
    v = end
    while v != -1:
        order.append(v)
        previous = parent[mask][v]
        mask ^= 1 << v
        v = previous
    order.reverse()
    return answer, order


def held_karp_cycle(distance, start=0, restore=False):
    """Minimum Hamiltonian cycle through ``start``."""
    n = len(distance)
    if n <= 1:
        result = 0
        return (result, [start, start] if n else []) if restore else result
    inf = float("inf")
    size = 1 << n
    dp = [[inf] * n for _ in range(size)]
    parent = [[-1] * n for _ in range(size)] if restore else None
    dp[1 << start][start] = 0
    for mask in range(size):
        if not mask >> start & 1:
            continue
        bits = mask & ~(1 << start)
        if mask == 1 << start:
            bits = 1 << start
        remaining = (size - 1) ^ mask
        while bits:
            bit = bits & -bits
            v = bit.bit_length() - 1
            value = dp[mask][v]
            nxt_bits = remaining
            while value < inf and nxt_bits:
                nxt_bit = nxt_bits & -nxt_bits
                to = nxt_bit.bit_length() - 1
                nxt_mask = mask | nxt_bit
                candidate = value + distance[v][to]
                if candidate < dp[nxt_mask][to]:
                    dp[nxt_mask][to] = candidate
                    if restore:
                        parent[nxt_mask][to] = v
                nxt_bits ^= nxt_bit
            bits ^= bit
    full = size - 1
    end = min((v for v in range(n) if v != start),
              key=lambda v: dp[full][v] + distance[v][start])
    answer = dp[full][end] + distance[end][start]
    if not restore:
        return answer
    if answer == inf:
        return inf, []
    order = [start]
    reverse = []
    mask = full
    v = end
    while v != start:
        reverse.append(v)
        previous = parent[mask][v]
        mask ^= 1 << v
        v = previous
    order.extend(reversed(reverse))
    order.append(start)
    return answer, order


def dial_dijkstra(graph, starts, max_weight, restore=False):
    """Dijkstra with circular buckets for integer weights in [0,max_weight]."""
    n = len(graph)
    if isinstance(starts, int):
        starts = [starts]
    width = max_weight + 1
    if width <= 0:
        raise ValueError("max_weight must be nonnegative")
    buckets = [[] for _ in range(width)]
    inf = float("inf")
    distance = [inf] * n
    parent = [-1] * n
    active = 0
    for start in starts:
        if distance[start] != 0:
            distance[start] = 0
            buckets[0].append(start)
            active += 1
    current = 0
    while active:
        bucket = buckets[current % width]
        if not bucket:
            current += 1
            continue
        v = bucket.pop()
        active -= 1
        if distance[v] != current:
            continue
        for to, weight in graph[v]:
            if not 0 <= weight <= max_weight or int(weight) != weight:
                raise ValueError("edge weight must be an integer in range")
            nxt = current + weight
            if nxt < distance[to]:
                distance[to] = nxt
                parent[to] = v
                buckets[nxt % width].append(to)
                active += 1
    return (distance, parent) if restore else distance


def minimum_cost_arborescence(n, root, edges):
    """Return a minimum directed spanning arborescence rooted at ``root``.

    Edges are ``(source, target, cost)`` and may have negative costs or be
    parallel.  The result is ``(cost, original_edge_ids)``; ``None`` means some
    vertex is unreachable from the root.  This iterative Chu--Liu/Edmonds
    implementation runs in O(VE).
    """
    if n == 0:
        return 0, []
    if not 0 <= root < n:
        raise IndexError("root out of range")
    # Each current edge stores source, target, adjusted cost, original edge id.
    current_edges = [(u, v, cost, i) for i, (u, v, cost) in enumerate(edges)]
    current_n = n
    current_root = root
    # (old edges, old root, chosen incoming edge per old vertex,
    #  mapping from each next-level edge to its old-level edge)
    levels = []

    while True:
        incoming_cost = [float("inf")] * current_n
        incoming_edge = [-1] * current_n
        incoming_cost[current_root] = 0
        for edge_id, (u, v, cost, _) in enumerate(current_edges):
            if u != v and v != current_root and cost < incoming_cost[v]:
                incoming_cost[v] = cost
                incoming_edge[v] = edge_id
        if any(incoming_edge[v] == -1
               for v in range(current_n) if v != current_root):
            return None

        parent = [current_root] * current_n
        for v in range(current_n):
            if v != current_root:
                parent[v] = current_edges[incoming_edge[v]][0]
        component = [-1] * current_n
        visited = [-1] * current_n
        cycle_count = 0
        for start in range(current_n):
            v = start
            while (v != current_root and component[v] == -1
                   and visited[v] != start):
                visited[v] = start
                v = parent[v]
            if v != current_root and component[v] == -1:
                component[v] = cycle_count
                u = parent[v]
                while u != v:
                    component[u] = cycle_count
                    u = parent[u]
                cycle_count += 1

        if cycle_count == 0:
            selected = {incoming_edge[v] for v in range(current_n)
                        if v != current_root}
            break

        next_n = cycle_count
        for v in range(current_n):
            if component[v] == -1:
                component[v] = next_n
                next_n += 1
        next_edges = []
        next_to_old = []
        for old_edge, (u, v, cost, original) in enumerate(current_edges):
            a = component[u]
            b = component[v]
            if a != b:
                next_edges.append((a, b, cost - incoming_cost[v], original))
                next_to_old.append(old_edge)
        levels.append((current_edges, current_root, incoming_edge, next_to_old))
        current_edges = next_edges
        current_n = next_n
        current_root = component[current_root]

    while levels:
        old_edges, old_root, incoming_edge, next_to_old = levels.pop()
        selected_old = {incoming_edge[v] for v in range(len(incoming_edge))
                        if v != old_root}
        for edge_id in selected:
            old_edge = next_to_old[edge_id]
            target = old_edges[old_edge][1]
            if target != old_root:
                selected_old.discard(incoming_edge[target])
            selected_old.add(old_edge)
        selected = selected_old
        current_edges = old_edges

    original_ids = [current_edges[edge_id][3] for edge_id in selected]
    original_ids.sort()
    return sum(edges[edge_id][2] for edge_id in original_ids), original_ids
