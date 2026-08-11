"""重み付きまたは重みなし木の直径とpathを求める。"""

def _edge(entry):
    if isinstance(entry, int):
        return entry, 1
    return entry[0], entry[1]

def tree_diameter(tree):
    n = len(tree)
    if n == 0:
        return 0, []

    def farthest(start, keep_parent=False):
        parent = [-2] * n
        parent[start] = -1
        distance = [None] * n
        distance[start] = 0
        order = [start]
        best = start
        for node in order:
            value = distance[node]
            if value > distance[best]:
                best = node
            for entry in tree[node]:
                other, weight = _edge(entry)
                if other == parent[node]:
                    continue
                if parent[other] != -2:
                    raise ValueError("graph must be a tree")
                parent[other] = node
                distance[other] = value + weight
                order.append(other)
        if len(order) != n:
            raise ValueError("graph must be connected")
        return best, distance, parent if keep_parent else None

    first, _, _ = farthest(0)
    second, distance, parent = farthest(first, True)
    path = []
    node = second
    while node >= 0:
        path.append(node)
        if node == first:
            break
        node = parent[node]
    return distance[second], path

def diameter(tree):
    return tree_diameter(tree)[0]


def tree_metric_center(tree):
    """木を連続なmetric空間とみなした中心位置と半径を返す。"""
    diameter_value, path = tree_diameter(tree)
    if not path:
        return 0, (-1, -1, 0)
    if len(path) == 1:
        return 0, (path[0], path[0], 0)
    target = diameter_value / 2
    elapsed = 0
    for first, second in zip(path, path[1:]):
        weight = None
        for entry in tree[first]:
            other, current_weight = _edge(entry)
            if other == second:
                weight = current_weight
                break
        if elapsed + weight == target:
            return target, (second, second, 0)
        if elapsed + weight > target:
            return target, (first, second, target - elapsed)
        elapsed += weight
    return target, (path[-1], path[-1], 0)
