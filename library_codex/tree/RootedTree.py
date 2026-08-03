"""無根木を指定rootから向き付け、親子関係を反転変換する。"""

def _edge(entry):
    if isinstance(entry, int):
        return entry, 1
    return entry[0], entry[1]

def rooted_tree(tree, root=0):
    n = len(tree)
    if n == 0:
        return []
    parent = [-2] * n
    parent[root] = -1
    order = [root]
    result = [[] for _ in range(n)]
    for node in order:
        for entry in tree[node]:
            other, _ = _edge(entry)
            if other == parent[node]:
                continue
            if parent[other] != -2:
                raise ValueError("graph must be a tree")
            parent[other] = node
            result[node].append(entry)
            order.append(other)
    if len(order) != n:
        raise ValueError("graph must be connected")
    return result

def inverse_tree(tree):
    result = [[] for _ in tree]
    for node, row in enumerate(tree):
        for entry in row:
            if isinstance(entry, int):
                result[entry].append(node)
            else:
                result[entry[0]].append((node, *entry[1:]))
    return result

