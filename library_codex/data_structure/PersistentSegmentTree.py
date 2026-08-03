class PersistentSegmentTree:
    __slots__ = ("n", "size", "op", "e", "left", "right", "data", "roots")

    def __init__(self, a_or_n, op, e):
        if isinstance(a_or_n, int):
            n = a_or_n
            values = None
        else:
            values = list(a_or_n)
            n = len(values)
        assert n >= 0
        size = 1 << (n - 1).bit_length() if n else 1
        left = [0]
        right = [0]
        data = [e]

        if values is None or n == 0:
            root = 0
        else:
            level = []
            for i in range(size):
                value = values[i] if i < n else e
                if value == e:
                    level.append(0)
                else:
                    left.append(0)
                    right.append(0)
                    data.append(value)
                    level.append(len(data) - 1)
            while len(level) > 1:
                nxt = []
                for i in range(0, len(level), 2):
                    l = level[i]
                    r = level[i + 1]
                    if l == 0 and r == 0:
                        nxt.append(0)
                    else:
                        left.append(l)
                        right.append(r)
                        data.append(op(data[l], data[r]))
                        nxt.append(len(data) - 1)
                level = nxt
            root = level[0]

        self.n = n
        self.size = size
        self.op = op
        self.e = e
        self.left = left
        self.right = right
        self.data = data
        self.roots = [root]

    def get_root(self, root, index):
        assert 0 <= index < self.n
        left = 0
        right = self.size
        children_l = self.left
        children_r = self.right
        while right - left > 1 and root:
            mid = (left + right) >> 1
            if index < mid:
                root = children_l[root]
                right = mid
            else:
                root = children_r[root]
                left = mid
        return self.data[root]

    def get(self, index, version=-1):
        return self.get_root(self.roots[version], index)

    def _update_root(self, root, index, value, combine):
        assert 0 <= index < self.n
        nodes_l = self.left
        nodes_r = self.right
        data = self.data
        path = []
        left = 0
        right = self.size
        while right - left > 1:
            mid = (left + right) >> 1
            if index < mid:
                path.append((root, False))
                root = nodes_l[root] if root else 0
                right = mid
            else:
                path.append((root, True))
                root = nodes_r[root] if root else 0
                left = mid

        if combine:
            value = self.op(value, data[root])
        if value == self.e:
            child = 0
        else:
            nodes_l.append(0)
            nodes_r.append(0)
            data.append(value)
            child = len(data) - 1

        op = self.op
        for root, went_right in reversed(path):
            if went_right:
                l = nodes_l[root] if root else 0
                r = child
            else:
                l = child
                r = nodes_r[root] if root else 0
            if l == 0 and r == 0:
                child = 0
            else:
                nodes_l.append(l)
                nodes_r.append(r)
                data.append(op(data[l], data[r]))
                child = len(data) - 1
        return child

    def update_root(self, root, index, value):
        return self._update_root(root, index, value, False)

    def set(self, index, value, version=-1):
        root = self.update_root(self.roots[version], index, value)
        self.roots.append(root)
        return len(self.roots) - 1

    update = set

    def add(self, index, value, version=-1):
        """op(value, current)を格納した新versionを返す。O(log N)。"""
        root = self.roots[version]
        root = self._update_root(root, index, value, True)
        self.roots.append(root)
        return len(self.roots) - 1

    def prod_root(self, root, ql, qr):
        assert 0 <= ql <= qr <= self.n
        if ql == qr or root == 0:
            return self.e
        res = self.e
        op = self.op
        data = self.data
        nodes_l = self.left
        nodes_r = self.right
        stack = [(root, 0, self.size)]
        while stack:
            node, left, right = stack.pop()
            if node == 0 or qr <= left or right <= ql:
                continue
            if ql <= left and right <= qr:
                res = op(res, data[node])
                continue
            mid = (left + right) >> 1
            stack.append((nodes_r[node], mid, right))
            stack.append((nodes_l[node], left, mid))
        return res

    def prod(self, l, r, version=-1):
        return self.prod_root(self.roots[version], l, r)

    query = prod

    def all_prod(self, version=-1):
        return self.data[self.roots[version]]

    def fork(self, version=-1):
        self.roots.append(self.roots[version])
        return len(self.roots) - 1

    def new_tree(self):
        self.roots.append(0)
        return len(self.roots) - 1

    def node_count(self):
        return len(self.data) - 1

    def tolist(self, version=-1):
        """指定versionの要素列をlistで返す。O(N)。"""
        result = [self.e] * self.n
        root = self.roots[version]
        if not root:
            return result
        stack = [(root, 0, self.size)]
        while stack:
            node, left, right = stack.pop()
            if not node:
                continue
            if right - left == 1:
                if left < self.n:
                    result[left] = self.data[node]
                continue
            middle = (left + right) >> 1
            stack.append((self.right[node], middle, right))
            stack.append((self.left[node], left, middle))
        return result

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "PersistentSegmentTree(%r)" % self.tolist()
