"""無向グラフの極大独立集合を重複なく列挙する。"""


def maximal_independent_sets(graph):
    """すべての極大独立集合を頂点listとして順に生成する。"""
    n = len(graph)
    adjacency = [0] * n
    for vertex, row in enumerate(graph):
        mask = 0
        for entry in row:
            other = entry if isinstance(entry, int) else entry[0]
            if not 0 <= other < n:
                raise IndexError("an edge endpoint is outside the graph")
            if other != vertex:
                mask |= 1 << other
        adjacency[vertex] = mask
    full = (1 << n) - 1
    stack = [[0, full, None]]
    while stack:
        chosen, remaining, candidates = stack[-1]
        if remaining == 0:
            stack.pop()
            result = []
            bits = chosen
            while bits:
                bit = bits & -bits
                result.append(bit.bit_length() - 1)
                bits ^= bit
            yield result
            continue
        if candidates is None:
            bits = remaining
            pivot = -1
            degree = n + 1
            while bits:
                bit = bits & -bits
                vertex = bit.bit_length() - 1
                current = (remaining & adjacency[vertex]).bit_count()
                if current < degree:
                    pivot = vertex
                    degree = current
                bits ^= bit
            candidates = remaining & (adjacency[pivot] | 1 << pivot)
            stack[-1][2] = candidates
        if candidates == 0:
            stack.pop()
            continue
        bit = candidates & -candidates
        stack[-1][2] ^= bit
        vertex = bit.bit_length() - 1
        stack.append([chosen | bit, remaining & ~bit & ~adjacency[vertex], None])
