"""深さ優先探索forestの親・順序・終了順を求める。"""

def dfs_forest(graph, root=0, postorder=False):
    """Return ``(DFS order, parent)`` for all components without recursion."""
    n = len(graph)
    if n == 0:
        return [], []
    parent = [-2] * n
    order = []
    starts = list(range(root, n)) + list(range(root))
    for start in starts:
        if parent[start] != -2:
            continue
        parent[start] = -1
        if not postorder:
            order.append(start)
        stack = [(start, 0)]
        while stack:
            vertex, index = stack[-1]
            if index == len(graph[vertex]):
                stack.pop()
                if postorder:
                    order.append(vertex)
                continue
            entry = graph[vertex][index]
            stack[-1] = (vertex, index + 1)
            to = entry if isinstance(entry, int) else entry[0]
            if parent[to] == -2:
                parent[to] = vertex
                if not postorder:
                    order.append(to)
                stack.append((to, 0))
    return order, parent

