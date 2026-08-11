"""tournament graphのHamilton pathを構成する。"""


def tournament_hamiltonian_path(graph):
    """各隣接頂点へ向かう辺を並べた隣接listからpathを返す。"""
    n = len(graph)
    outgoing = [set(neighbors) for neighbors in graph]
    for vertex in range(n):
        if vertex in outgoing[vertex]:
            raise ValueError("self loops are not allowed")
    for first in range(n):
        for second in range(first + 1, n):
            if ((second in outgoing[first]) + (first in outgoing[second])) != 1:
                raise ValueError("graph must be a tournament")
    path = []
    for vertex in range(n):
        position = 0
        while position < len(path) and path[position] not in outgoing[vertex]:
            position += 1
        path.insert(position, vertex)
    return path
