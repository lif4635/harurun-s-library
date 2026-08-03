"""列のCartesian treeをparent列または隣接listとして構築する。"""

def cartesian_tree(values, minimum=True):
    values = list(values)
    n = len(values)
    parent = [-1] * n
    left = [-1] * n
    right = [-1] * n
    stack = []
    if minimum:
        for index, value in enumerate(values):
            previous = -1
            while stack and value < values[stack[-1]]:
                previous = stack.pop()
            if previous >= 0:
                parent[previous] = index
                left[index] = previous
            if stack:
                parent[index] = stack[-1]
                right[stack[-1]] = index
            stack.append(index)
    else:
        for index, value in enumerate(values):
            previous = -1
            while stack and value > values[stack[-1]]:
                previous = stack.pop()
            if previous >= 0:
                parent[previous] = index
                left[index] = previous
            if stack:
                parent[index] = stack[-1]
                right[stack[-1]] = index
            stack.append(index)
    root = stack[0] if stack else -1
    return parent, left, right, root

def cartesian_tree_graph(values, minimum=True, directed=True):
    parent, left, right, root = cartesian_tree(values, minimum)
    graph = [[] for _ in parent]
    for node, par in enumerate(parent):
        if par >= 0:
            graph[par].append(node)
            if not directed:
                graph[node].append(par)
    return graph, root

