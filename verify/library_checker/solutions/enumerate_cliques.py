"""小規模無向グラフのcliqueを列挙する。"""

def _graph_enumeration_enumerate_cliques_adjacency_masks(graph):
    n = len(graph)
    adj = [0] * n
    for v in range(n):
        a = 0
        for u in graph[v]:
            if u != v:
                a |= 1 << u
        adj[v] = a
    return adj

def _graph_enumeration_enumerate_cliques_mask_vertices(mask):
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
    adj = _graph_enumeration_enumerate_cliques_adjacency_masks(graph)
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
        stack = [(bit, adj[first] & (universe ^ (bit << 1) - 1))]
        while stack:
            (clique, candidates) = stack.pop()
            vertices = _graph_enumeration_enumerate_cliques_mask_vertices(clique)
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
import sys

def main():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    (n, m) = (next(data), next(data))
    values = [next(data) for _ in range(n)]
    graph = [[] for _ in range(n)]
    for _ in range(m):
        (u, v) = (next(data), next(data))
        graph[u].append(v)
        graph[v].append(u)
    answer = 0

    def collect(vertices):
        nonlocal answer
        value = 1
        for vertex in vertices:
            value = value * values[vertex] % 998244353
        answer = (answer + value) % 998244353
    enumerate_cliques(graph, collect)
    print(answer)
main()
