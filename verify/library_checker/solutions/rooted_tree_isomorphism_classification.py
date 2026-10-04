"""重み付きまたは重みなし木の直径とpathを求める。"""

def _tree_tree_diameter_edge(entry):
    if isinstance(entry, int):
        return (entry, 1)
    return (entry[0], entry[1])

def tree_diameter(tree):
    n = len(tree)
    if n == 0:
        return (0, [])

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
                (other, weight) = _tree_tree_diameter_edge(entry)
                if other == parent[node]:
                    continue
                if parent[other] != -2:
                    raise ValueError('graph must be a tree')
                parent[other] = node
                distance[other] = value + weight
                order.append(other)
        if len(order) != n:
            raise ValueError('graph must be connected')
        return (best, distance, parent if keep_parent else None)
    (first, _, _) = farthest(0)
    (second, distance, parent) = farthest(first, True)
    path = []
    node = second
    while node >= 0:
        path.append(node)
        if node == first:
            break
        node = parent[node]
    return (distance[second], path)

def diameter(tree):
    return tree_diameter(tree)[0]

def tree_center(tree):
    """Return the one or two vertices minimizing maximum edge distance."""
    n = len(tree)
    if n == 0:
        return []
    parent = [-2] * n
    parent[0] = -1
    order = [0]
    for vertex in order:
        for entry in tree[vertex]:
            (other, _) = _tree_tree_diameter_edge(entry)
            if other == parent[vertex]:
                continue
            if parent[other] != -2:
                raise ValueError('graph must be a tree')
            parent[other] = vertex
            order.append(other)
    if len(order) != n:
        raise ValueError('graph must be connected')
    degree = list(map(len, tree))
    if sum(degree) != n - 1 << 1:
        raise ValueError('graph must be a tree')
    if n <= 2:
        return list(range(n))
    leaves = [vertex for vertex in range(n) if degree[vertex] == 1]
    remaining = n
    while remaining > 2:
        remaining -= len(leaves)
        next_leaves = []
        for leaf in leaves:
            degree[leaf] = 0
            for entry in tree[leaf]:
                (other, _) = _tree_tree_diameter_edge(entry)
                if degree[other] > 0:
                    degree[other] -= 1
                    if degree[other] == 1:
                        next_leaves.append(other)
        leaves = next_leaves
    leaves.sort()
    return leaves

def tree_metric_center(tree):
    """木を連続なmetric空間とみなした中心位置と半径を返す。"""
    (diameter_value, path) = tree_diameter(tree)
    if not path:
        return (0, (-1, -1, 0))
    if len(path) == 1:
        return (0, (path[0], path[0], 0))
    target = diameter_value / 2
    elapsed = 0
    for (first, second) in zip(path, path[1:]):
        weight = None
        for entry in tree[first]:
            (other, current_weight) = _tree_tree_diameter_edge(entry)
            if other == second:
                weight = current_weight
                break
        if elapsed + weight == target:
            return (target, (second, second, 0))
        if elapsed + weight > target:
            return (target, (first, second, target - elapsed))
        elapsed += weight
    return (target, (path[-1], path[-1], 0))
MASK64 = (1 << 64) - 1

def _tree_tree_isomorphism_mix64(value):
    value = value + 11400714819323198485 & MASK64
    value = (value ^ value >> 30) * 13787848793156543929 & MASK64
    value = (value ^ value >> 27) * 10723151780598845931 & MASK64
    return value ^ value >> 31

def _tree_tree_isomorphism_parent_order(tree, root):
    n = len(tree)
    assert 0 <= root < n
    if sum(map(len, tree)) != n - 1 << 1:
        raise ValueError('the graph must be a tree')
    parent = [-2] * n
    parent[root] = -1
    order = [root]
    for v in order:
        p = parent[v]
        for to in tree[v]:
            if not 0 <= to < n:
                raise ValueError('the graph must be a tree')
            if to == p:
                continue
            if parent[to] != -2:
                raise ValueError('the graph must be a tree')
            parent[to] = v
            order.append(to)
    if len(order) != n:
        raise ValueError('the graph must be connected')
    return (parent, order)

class AHUInterner:
    __slots__ = ('mapping',)

    def __init__(self):
        self.mapping = {(): 0}

    def intern(self, signature):
        mapping = self.mapping
        class_id = mapping.get(signature)
        if class_id is None:
            class_id = len(mapping)
            mapping[signature] = class_id
        return class_id

    def __len__(self):
        return len(self.mapping)

class RootedTreeIsomorphism:
    __slots__ = ('tree', 'n', 'root', 'interner', 'parent', 'order', 'height', 'class_id', 'compressed', 'children_ordered', 'hash', 'hashes', 'num_classes')

    def __init__(self, tree, root=0, interner=None):
        n = len(tree)
        (parent, order) = _tree_tree_isomorphism_parent_order(tree, root)
        if interner is None:
            interner = AHUInterner()
        children = [[] for _ in range(n)]
        for v in order[1:]:
            children[parent[v]].append(v)
        height = [0] * n
        class_id = [0] * n
        hashes = [(0, 0)] * n
        for v in reversed(order):
            child = children[v]
            if child:
                child.sort(key=class_id.__getitem__)
                h = 0
                for to in child:
                    value = height[to] + 1
                    if value > h:
                        h = value
                height[v] = h
            signature = tuple((class_id[to] for to in child))
            class_id[v] = interner.intern(signature)
            basis1 = _tree_tree_isomorphism_mix64(height[v] ^ 2611923443488327891)
            basis2 = _tree_tree_isomorphism_mix64(height[v] ^ 1376283091369227076)
            hash1 = 11820040416388919760
            hash2 = 589684135938649225
            for to in child:
                child_hash = hashes[to]
                hash1 = hash1 * (basis1 + child_hash[0] & MASK64 | 1) & MASK64
                hash2 = hash2 * (basis2 + child_hash[1] & MASK64 | 1) & MASK64
            hashes[v] = (_tree_tree_isomorphism_mix64(hash1 ^ len(child)), _tree_tree_isomorphism_mix64(hash2 ^ len(child)))
        self.tree = tree
        self.n = n
        self.root = root
        self.interner = interner
        self.parent = parent
        self.order = order
        self.height = height
        self.class_id = class_id
        self.compressed = class_id
        self.children_ordered = children
        self.hash = hashes
        self.hashes = hashes
        self.num_classes = len(set(class_id))

    def same_subtree(self, u, v):
        return self.class_id[u] == self.class_id[v]
RootedTreeHash = RootedTreeIsomorphism
AHUAlgorithm = RootedTreeIsomorphism

def rooted_tree_hashes(tree, root=0):
    (hash1, hash2) = _tree_tree_isomorphism_rooted_tree_hash_arrays(tree, root)
    return list(zip(hash1, hash2))

def _tree_tree_isomorphism_rooted_tree_hash_arrays(tree, root):
    (parent, order) = _tree_tree_isomorphism_parent_order(tree, root)
    n = len(tree)
    height = [0] * n
    hash1 = [0] * n
    hash2 = [0] * n
    for v in reversed(order):
        maximum = 0
        for to in tree[v]:
            if parent[to] == v:
                value = height[to] + 1
                if value > maximum:
                    maximum = value
        height[v] = maximum
        basis1 = _tree_tree_isomorphism_mix64(maximum ^ 2611923443488327891)
        basis2 = _tree_tree_isomorphism_mix64(maximum ^ 1376283091369227076)
        value1 = 11820040416388919760
        value2 = 589684135938649225
        child_count = 0
        for to in tree[v]:
            if parent[to] == v:
                child_count += 1
                value1 = value1 * (basis1 + hash1[to] & MASK64 | 1) & MASK64
                value2 = value2 * (basis2 + hash2[to] & MASK64 | 1) & MASK64
        hash1[v] = _tree_tree_isomorphism_mix64(value1 ^ child_count)
        hash2[v] = _tree_tree_isomorphism_mix64(value2 ^ child_count)
    return (hash1, hash2)

def tree_hash(tree):
    centers = tree_center(tree)
    if not centers:
        return ()
    hashes = []
    for root in centers:
        (hash1, hash2) = _tree_tree_isomorphism_rooted_tree_hash_arrays(tree, root)
        hashes.append((hash1[root], hash2[root]))
    if len(hashes) == 1:
        hashes.append(hashes[0])
    hashes.sort()
    return tuple(hashes)

def rooted_tree_isomorphic(tree1, root1, tree2, root2):
    if len(tree1) != len(tree2):
        return False
    if not tree1:
        return True
    interner = AHUInterner()
    first = RootedTreeIsomorphism(tree1, root1, interner).class_id[root1]
    second = RootedTreeIsomorphism(tree2, root2, interner)
    return first == second.class_id[root2]

def unrooted_tree_isomorphic(tree1, tree2):
    if len(tree1) != len(tree2):
        return False
    if not tree1:
        return True
    interner = AHUInterner()

    def key(tree):
        result = []
        for root in tree_center(tree):
            ahu = RootedTreeIsomorphism(tree, root, interner)
            result.append(ahu.class_id[root])
        if len(result) == 1:
            result.append(result[0])
        result.sort()
        return tuple(result)
    return key(tree1) == key(tree2)
import sys

def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n = next(data)
    graph = [[] for _ in range(n)]
    for v in range(1, n):
        p = next(data)
        graph[p].append(v)
        graph[v].append(p)
    tree = RootedTreeIsomorphism(graph)
    print(tree.num_classes)
    print(*tree.class_id)
if __name__ == '__main__':
    solve()
