from library_codex.tree.TreeIsomorphism import _parent_order


def prufer_decode_edges(code, n=None):
    code = list(code)
    if n is None:
        n = len(code) + 2
    assert n >= 0 and len(code) == max(0, n - 2)
    assert all(0 <= vertex < n for vertex in code)
    if n <= 1:
        return []
    degree = [1] * n
    for vertex in code:
        degree[vertex] += 1
    extended = code + [n - 1]
    pointer = 0
    leaf = -1
    edges = []
    for vertex in extended:
        if leaf == -1:
            while degree[pointer] != 1:
                pointer += 1
            leaf = pointer
        edges.append((leaf, vertex))
        degree[leaf] -= 1
        degree[vertex] -= 1
        if vertex < pointer and degree[vertex] == 1:
            leaf = vertex
        else:
            leaf = -1
    return edges


def prufer_decode(code, n=None):
    if n is None:
        code = list(code)
        n = len(code) + 2
    else:
        code = list(code)
    tree = [[] for _ in range(n)]
    for u, v in prufer_decode_edges(code, n):
        tree[u].append(v)
        tree[v].append(u)
    return tree


def prufer_encode(tree):
    n = len(tree)
    if n <= 1:
        if n == 1 and tree[0]:
            raise ValueError("the graph must be a tree")
        return []
    parent, _ = _parent_order(tree, n - 1)
    degree = list(map(len, tree))
    pointer = 0
    leaf = -1
    code = []
    for _ in range(n - 2):
        if leaf == -1:
            while degree[pointer] != 1:
                pointer += 1
            leaf = pointer
        vertex = parent[leaf]
        code.append(vertex)
        degree[leaf] -= 1
        degree[vertex] -= 1
        if vertex < pointer and degree[vertex] == 1:
            leaf = vertex
        else:
            leaf = -1
    return code


def prufer_encode_extended(tree):
    n = len(tree)
    if n == 0:
        return []
    return prufer_encode(tree) + [n - 1]


def prufer_decode_extended(code):
    code = list(code)
    if not code:
        return []
    if code == [0]:
        return [[]]
    n = len(code) + 1
    assert code[-1] == n - 1
    return prufer_decode(code[:-1], n)


encode_prufer = prufer_encode
decode_prufer = prufer_decode
