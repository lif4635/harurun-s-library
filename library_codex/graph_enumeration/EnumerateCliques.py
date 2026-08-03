"""小規模無向グラフのcliqueを列挙する。"""

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

