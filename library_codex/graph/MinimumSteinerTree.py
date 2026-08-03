"""少数のterminalをすべて結ぶ最小Steiner tree費用を求める。"""

from heapq import heappop, heappush

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

