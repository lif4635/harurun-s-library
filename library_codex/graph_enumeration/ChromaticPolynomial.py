"""無向グラフをk色で正しく塗り分ける方法の個数を、kの多項式として返す。"""

from library_codex.bitwise_convolution.SetFunction import SubsetConvolution


def _component_polynomial(adjacency, mod):
    n = len(adjacency)
    edges = sum(mask.bit_count() for mask in adjacency) // 2
    if edges == n - 1 or edges == n * (n - 1) // 2:
        polynomial = [0, 1]
        for i in range(1, n):
            root = 1 if edges == n - 1 else i
            polynomial.append(0)
            for degree in range(len(polynomial) - 1, 0, -1):
                polynomial[degree] = (polynomial[degree - 1] - root * polynomial[degree]) % mod
        return polynomial
    size = 1 << n
    independent = [0] * size
    independent[0] = 1
    for mask in range(1, size):
        bit = mask & -mask
        rest = mask ^ bit
        independent[mask] = independent[rest] if rest & adjacency[bit.bit_length() - 1] == 0 else 0
    independent[0] = 0
    weights = [0] * size
    weights[-1] = 1
    partitions = SubsetConvolution(mod).transpose_compose_egf(independent, weights)
    polynomial = [0] * (n + 1)
    falling = [1]
    for blocks in range(1, n + 1):
        falling.append(0)
        for degree in range(blocks, 0, -1):
            falling[degree] = (falling[degree - 1] - (blocks - 1) * falling[degree]) % mod
        falling[0] = 0
        coefficient = partitions[blocks]
        for degree in range(1, blocks + 1):
            polynomial[degree] = (polynomial[degree] + coefficient * falling[degree]) % mod
    return polynomial


def chromatic_polynomial(graph, mod=998244353):
    """k色での適正彩色数P(k)の係数を、定数項から順に長さN+1のlistで返す。"""
    if mod < 2:
        raise ValueError("mod must be at least 2")
    n = len(graph)
    adjacency = [0] * n
    loop = False
    for vertex in range(n):
        for neighbor in graph[vertex]:
            if not 0 <= neighbor < n:
                raise ValueError("neighbor index out of range")
            if vertex == neighbor:
                loop = True
            adjacency[vertex] |= 1 << neighbor
            adjacency[neighbor] |= 1 << vertex
    if loop:
        return [0] * (n + 1)
    result = [1]
    unseen = (1 << n) - 1
    while unseen:
        bit = unseen & -unseen
        unseen ^= bit
        component = []
        frontier = bit
        while frontier:
            bit = frontier & -frontier
            frontier ^= bit
            vertex = bit.bit_length() - 1
            component.append(vertex)
            neighbors = adjacency[vertex] & unseen
            unseen ^= neighbors
            frontier |= neighbors
        positions = {vertex: i for i, vertex in enumerate(component)}
        local = []
        for vertex in component:
            mask = adjacency[vertex]
            remapped = 0
            while mask:
                bit = mask & -mask
                mask ^= bit
                remapped |= 1 << positions[bit.bit_length() - 1]
            local.append(remapped)
        factor = _component_polynomial(local, mod)
        product = [0] * (len(result) + len(factor) - 1)
        for i, a in enumerate(result):
            for j, b in enumerate(factor):
                product[i + j] = (product[i + j] + a * b) % mod
        result = product
    return result
