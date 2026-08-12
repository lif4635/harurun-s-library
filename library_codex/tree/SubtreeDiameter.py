"""Diameters of every rooted subtree."""


def _edge(entry):
    if isinstance(entry, int):
        return entry, 1
    return entry[0], entry[1]


def subtree_diameters(tree, root=0):
    """Return ``(distance, endpoint1, endpoint2)`` for every rooted subtree."""
    n = len(tree)
    if n == 0:
        return []
    if not 0 <= root < n:
        raise IndexError("root is out of range")
    parent = [-2] * n
    parent[root] = -1
    order = [root]
    parent_weight = [0] * n
    for vertex in order:
        for entry in tree[vertex]:
            other, weight = _edge(entry)
            if weight < 0:
                raise ValueError("edge weights must be nonnegative")
            if other == parent[vertex]:
                continue
            if parent[other] != -2:
                raise ValueError("graph must be a tree")
            parent[other] = vertex
            parent_weight[other] = weight
            order.append(other)
    if len(order) != n:
        raise ValueError("graph must be connected")

    down_distance = [0] * n
    down_endpoint = list(range(n))
    answer = [(0, vertex, vertex) for vertex in range(n)]
    for vertex in reversed(order):
        best_first = (0, vertex)
        best_second = (0, vertex)
        best_diameter = answer[vertex]
        for entry in tree[vertex]:
            child, weight = _edge(entry)
            if parent[child] != vertex:
                continue
            child_diameter = answer[child]
            if child_diameter[0] > best_diameter[0]:
                best_diameter = child_diameter
            candidate = (down_distance[child] + weight, down_endpoint[child])
            if candidate[0] > best_first[0]:
                best_second = best_first
                best_first = candidate
            elif candidate[0] > best_second[0]:
                best_second = candidate
        through = best_first[0] + best_second[0]
        if through > best_diameter[0]:
            best_diameter = (through, best_first[1], best_second[1])
        down_distance[vertex], down_endpoint[vertex] = best_first
        answer[vertex] = best_diameter
    return answer
