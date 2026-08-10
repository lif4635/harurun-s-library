"""有向グラフで始点から各頂点への全経路が必ず通る直前の支配頂点を求める。"""


def dominator_tree(graph, root=0):
    """各頂点のimmediate dominatorを頂点順のlistで返す。"""
    size = len(graph)
    if not 0 <= root < size:
        raise ValueError("root must be a vertex of graph")

    adjacency = [[] for _ in range(size)]
    reverse = [[] for _ in range(size)]
    for source, row in enumerate(graph):
        output = adjacency[source]
        for entry in row:
            target = entry if isinstance(entry, int) else entry[0]
            if not 0 <= target < size:
                raise ValueError("edge endpoint is outside graph")
            output.append(target)
            reverse[target].append(source)

    order_index = [-1] * size
    parent = [-1] * size
    order = [root]
    order_index[root] = 0
    stack = [(root, 0)]
    while stack:
        vertex, edge_index = stack[-1]
        if edge_index == len(adjacency[vertex]):
            stack.pop()
            continue
        target = adjacency[vertex][edge_index]
        stack[-1] = (vertex, edge_index + 1)
        if order_index[target] < 0:
            parent[target] = vertex
            order_index[target] = len(order)
            order.append(target)
            stack.append((target, 0))

    semi = list(range(size))
    label = list(range(size))
    ancestor = [-1] * size
    representative = list(range(size))
    buckets = [[] for _ in range(size)]

    def compress(vertex):
        path = []
        current = vertex
        while ancestor[current] >= 0:
            path.append(current)
            current = ancestor[current]
        while path:
            node = path.pop()
            upper = ancestor[node]
            if order_index[semi[label[upper]]] < order_index[semi[label[node]]]:
                label[node] = label[upper]
            ancestor[node] = current

    for position in range(len(order) - 1, 0, -1):
        vertex = order[position]
        for source in reverse[vertex]:
            if order_index[source] < 0:
                continue
            compress(source)
            candidate = semi[label[source]]
            if order_index[candidate] < order_index[semi[vertex]]:
                semi[vertex] = candidate
        buckets[semi[vertex]].append(vertex)

        tree_parent = parent[vertex]
        for pending in buckets[tree_parent]:
            compress(pending)
            representative[pending] = label[pending]
        buckets[tree_parent].clear()
        ancestor[vertex] = tree_parent

    immediate = [-1] * size
    immediate[root] = root
    for vertex in order[1:]:
        candidate = representative[vertex]
        if semi[vertex] == semi[candidate]:
            immediate[vertex] = semi[vertex]
        else:
            immediate[vertex] = immediate[candidate]
    return immediate
