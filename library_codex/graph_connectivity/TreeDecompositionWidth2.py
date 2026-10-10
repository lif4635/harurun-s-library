"""木幅2以下かを判定し、頂点集合と親配列で木分解を返す。"""


def tree_decomposition_width2(n, edges):
    """Return (bags, parent), or None when the treewidth exceeds two."""
    if n < 0:
        raise ValueError("number of vertices must be nonnegative")
    head = [-1] * n
    degree = [0] * n
    to = []
    following = []
    previous = []
    present = set()

    def add(a, b):
        for v, u in ((a, b), (b, a)):
            index = len(to)
            old = head[v]
            to.append(u)
            following.append(old)
            previous.append(-1)
            if old >= 0:
                previous[old] = index
            head[v] = index
            degree[v] += 1

    for a, b in edges:
        if not 0 <= a < n or not 0 <= b < n:
            raise IndexError("edge endpoint is outside the graph")
        if a == b:
            continue
        key = a * n + b if a < b else b * n + a
        if key not in present:
            present.add(key)
            add(a, b)

    queue = [v for v in range(n) if degree[v] <= 2]
    bags = []
    position = [-1] * n
    for v in queue:
        if degree[v] < 0:
            continue
        bag = [v]
        while head[v] >= 0:
            edge = head[v]
            u = to[edge]
            bag.append(u)
            present.remove(v * n + u if v < u else u * n + v)
            for index, vertex in ((edge, v), (edge ^ 1, u)):
                before, after = previous[index], following[index]
                if before < 0:
                    head[vertex] = after
                else:
                    following[before] = after
                if after >= 0:
                    previous[after] = before
                degree[vertex] -= 1
        degree[v] = -1
        position[v] = len(bags)
        bags.append(bag)
        if len(bag) == 3:
            a, b = bag[1], bag[2]
            key = a * n + b if a < b else b * n + a
            if key not in present:
                present.add(key)
                add(a, b)
        for u in bag[1:]:
            if degree[u] <= 2:
                queue.append(u)
    if len(bags) != n:
        return None
    parent = [-1] * n
    for i, bag in enumerate(bags):
        if len(bag) == 1:
            if i + 1 < n:
                parent[i] = n - 1
        elif len(bag) == 2:
            parent[i] = position[bag[1]]
        else:
            parent[i] = min(position[bag[1]], position[bag[2]])
    return bags, parent
