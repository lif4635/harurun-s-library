class DSUOnTree:
    __slots__ = (
        "tree",
        "n",
        "root",
        "parent",
        "size",
        "heavy",
        "down",
        "up",
        "euler",
    )

    def __init__(self, tree, root=0):
        n = len(tree)
        if not 0 <= root < n:
            raise IndexError("root is out of range")
        parent = [-2] * n
        parent[root] = -1
        order = [root]
        for node in order:
            for other in tree[node]:
                if other == parent[node]:
                    continue
                if parent[other] != -2:
                    raise ValueError("graph must be a tree")
                parent[other] = node
                order.append(other)
        if len(order) != n:
            raise ValueError("graph must be connected")
        size = [1] * n
        heavy = [-1] * n
        for node in reversed(order):
            best = 0
            for other in tree[node]:
                if parent[other] == node:
                    size[node] += size[other]
                    if size[other] > best:
                        best = size[other]
                        heavy[node] = other
        down = [0] * n
        up = [0] * n
        euler = [0] * n
        timer = 0
        stack = [(root, 0)]
        while stack:
            node, state = stack.pop()
            if state == 0:
                down[node] = timer
                euler[timer] = node
                timer += 1
                stack.append((node, 1))
                children = [
                    other for other in tree[node] if parent[other] == node
                ]
                best = heavy[node]
                for other in reversed(children):
                    if other != best:
                        stack.append((other, 0))
                if best >= 0:
                    stack.append((best, 0))
            else:
                up[node] = timer
        self.tree = tree
        self.n = n
        self.root = root
        self.parent = parent
        self.size = size
        self.heavy = heavy
        self.down = down
        self.up = up
        self.euler = euler

    def index(self, vertex):
        return self.down[vertex]

    idx = index

    def run(self, add, query, remove, reset=None):
        tree = self.tree
        parent = self.parent
        heavy = self.heavy
        down = self.down
        up = self.up
        euler = self.euler
        stack = [(0, self.root, True)]
        while stack:
            state, node, keep = stack.pop()
            if state == 0:
                stack.append((1, node, keep))
                best = heavy[node]
                if best >= 0:
                    stack.append((0, best, True))
                children = [
                    other
                    for other in tree[node]
                    if parent[other] == node and other != best
                ]
                for other in reversed(children):
                    stack.append((0, other, False))
            else:
                best = heavy[node]
                for other in tree[node]:
                    if parent[other] == node and other != best:
                        for index in range(down[other], up[other]):
                            add(euler[index])
                add(node)
                query(node)
                if not keep:
                    for index in range(down[node], up[node]):
                        remove(euler[index])
                    if reset is not None:
                        reset()
