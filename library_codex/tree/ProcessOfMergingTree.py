"""辺が追加される過程を表すmerge treeを構築する。"""

def process_of_merging_tree(edges, size=None, sort_edges=False):
    edges = list(edges)
    if size is None:
        size = 1
        for edge in edges:
            size = max(size, edge[0] + 1, edge[1] + 1)
    if sort_edges:
        edges.sort(key=lambda edge: edge[2])
    parent = list(range(size))
    component_size = [1] * size
    roots = list(range(size))
    graph = [[] for _ in range(max(1, size * 2 - 1))]
    weights = []

    def find(node):
        root = node
        while parent[root] != root:
            root = parent[root]
        while parent[node] != node:
            next_node = parent[node]
            parent[node] = root
            node = next_node
        return root

    auxiliary = size
    for first, second, weight, *_ in edges:
        first = find(first)
        second = find(second)
        if first == second:
            continue
        graph[auxiliary].append((roots[first], weight))
        graph[auxiliary].append((roots[second], weight))
        weights.append(weight)
        if component_size[first] < component_size[second]:
            first, second = second, first
        parent[second] = first
        component_size[first] += component_size[second]
        roots[first] = auxiliary
        auxiliary += 1
    if size and auxiliary != size * 2 - 1:
        raise ValueError("edges do not connect all vertices")
    return graph[:auxiliary], weights, auxiliary - 1

