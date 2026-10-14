"""有向グラフの全辺を一度ずつ使う閉路を、巡回シフトを同一視して数える。"""

def count_eulerian_circuits(n, edges, mod=998244353):
    if n < 0 or mod < 2:
        raise ValueError("n must be nonnegative and mod must be at least 2")
    edges = list(edges)
    incoming = [0] * n
    outgoing = [0] * n
    for u, v in edges:
        if not 0 <= u < n or not 0 <= v < n:
            raise IndexError("vertex out of range")
        outgoing[u] += 1
        incoming[v] += 1
    if not edges or incoming != outgoing:
        return 0
    index = [-1] * n
    active = 0
    factor = 1
    for vertex, degree in enumerate(outgoing):
        if degree:
            index[vertex] = active
            active += 1
            if degree > mod:
                return 0
            for value in range(2, degree):
                factor = factor * value % mod
    size = active - 1
    laplacian = [[0] * size for _ in range(size)]
    for u, v in edges:
        a, b = index[u], index[v]
        if a < size:
            laplacian[a][a] += 1
            if b < size:
                laplacian[a][b] -= 1
    for column in range(size):
        pivot = column
        while pivot < size and laplacian[pivot][column] % mod == 0:
            pivot += 1
        if pivot == size:
            return 0
        if pivot != column:
            laplacian[pivot], laplacian[column] = laplacian[column], laplacian[pivot]
            factor = -factor
        source = laplacian[column]
        value = source[column] % mod
        factor = factor * value % mod
        inverse = pow(value, -1, mod)
        for row in range(column + 1, size):
            target = laplacian[row]
            coefficient = target[column] * inverse % mod
            if coefficient:
                for j in range(column + 1, size):
                    target[j] = (target[j] - coefficient * source[j]) % mod
    return factor % mod
