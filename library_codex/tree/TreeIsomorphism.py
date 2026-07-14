MASK64 = (1 << 64) - 1


def _mix64(value):
    value = (value + 0x9E3779B97F4A7C15) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    return value ^ (value >> 31)


def _parent_order(tree, root):
    n = len(tree)
    assert 0 <= root < n
    if sum(map(len, tree)) != (n - 1) << 1:
        raise ValueError("the graph must be a tree")
    parent = [-2] * n
    parent[root] = -1
    order = [root]
    for v in order:
        p = parent[v]
        for to in tree[v]:
            if not 0 <= to < n:
                raise ValueError("the graph must be a tree")
            if to == p:
                continue
            if parent[to] != -2:
                raise ValueError("the graph must be a tree")
            parent[to] = v
            order.append(to)
    if len(order) != n:
        raise ValueError("the graph must be connected")
    return parent, order


class AHUInterner:
    __slots__ = ("mapping",)

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
    __slots__ = (
        "tree", "n", "root", "interner", "parent", "order", "height",
        "class_id", "compressed", "children_ordered", "hash", "hashes",
        "num_classes",
    )

    def __init__(self, tree, root=0, interner=None):
        n = len(tree)
        parent, order = _parent_order(tree, root)
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
            signature = tuple(class_id[to] for to in child)
            class_id[v] = interner.intern(signature)

            basis1 = _mix64(height[v] ^ 0x243F6A8885A308D3)
            basis2 = _mix64(height[v] ^ 0x13198A2E03707344)
            hash1 = 0xA4093822299F31D0
            hash2 = 0x082EFA98EC4E6C89
            for to in child:
                child_hash = hashes[to]
                hash1 = (
                    hash1 * (((basis1 + child_hash[0]) & MASK64) | 1)
                ) & MASK64
                hash2 = (
                    hash2 * (((basis2 + child_hash[1]) & MASK64) | 1)
                ) & MASK64
            hashes[v] = (
                _mix64(hash1 ^ len(child)),
                _mix64(hash2 ^ len(child)),
            )

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


def tree_center(tree):
    n = len(tree)
    if n == 0:
        return []
    _parent_order(tree, 0)
    if n <= 2:
        return list(range(n))
    degree = list(map(len, tree))
    leaves = [v for v in range(n) if degree[v] == 1]
    remaining = n
    while remaining > 2:
        remaining -= len(leaves)
        next_leaves = []
        for leaf in leaves:
            degree[leaf] = 0
            for to in tree[leaf]:
                if degree[to] > 0:
                    degree[to] -= 1
                    if degree[to] == 1:
                        next_leaves.append(to)
        leaves = next_leaves
    leaves.sort()
    return leaves


def tree_centroid(tree):
    n = len(tree)
    if n == 0:
        return []
    parent, order = _parent_order(tree, 0)
    size = [1] * n
    for v in reversed(order[1:]):
        size[parent[v]] += size[v]
    result = []
    for v in range(n):
        largest = n - size[v]
        for to in tree[v]:
            if parent[to] == v and size[to] > largest:
                largest = size[to]
        if largest * 2 <= n:
            result.append(v)
    return result


def rooted_tree_hashes(tree, root=0):
    hash1, hash2 = _rooted_tree_hash_arrays(tree, root)
    return list(zip(hash1, hash2))


def _rooted_tree_hash_arrays(tree, root):
    parent, order = _parent_order(tree, root)
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
        basis1 = _mix64(maximum ^ 0x243F6A8885A308D3)
        basis2 = _mix64(maximum ^ 0x13198A2E03707344)
        value1 = 0xA4093822299F31D0
        value2 = 0x082EFA98EC4E6C89
        child_count = 0
        for to in tree[v]:
            if parent[to] == v:
                child_count += 1
                value1 = (
                    value1 * (((basis1 + hash1[to]) & MASK64) | 1)
                ) & MASK64
                value2 = (
                    value2 * (((basis2 + hash2[to]) & MASK64) | 1)
                ) & MASK64
        hash1[v] = _mix64(value1 ^ child_count)
        hash2[v] = _mix64(value2 ^ child_count)
    return hash1, hash2


def tree_hash(tree):
    centers = tree_center(tree)
    if not centers:
        return ()
    hashes = []
    for root in centers:
        hash1, hash2 = _rooted_tree_hash_arrays(tree, root)
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
