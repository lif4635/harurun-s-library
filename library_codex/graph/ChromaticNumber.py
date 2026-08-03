"""小規模グラフの彩色数をbit DPで求める。"""

from library_codex.graph.GraphFromEdges import graph_from_edges

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

