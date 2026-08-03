"""全頂点を一度ずつ通る最短Hamilton pathまたはcycleをbit DPで求める。"""

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

