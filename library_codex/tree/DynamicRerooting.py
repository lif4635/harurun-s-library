class _DashedNode:
    __slots__ = ("left", "right", "parent", "key", "sum")

    def __init__(self, key):
        self.left = self.right = self.parent = None
        self.key = self.sum = key


class _DashedSplay:
    __slots__ = ("rake",)

    def __init__(self, rake):
        self.rake = rake

    def _update(self, node):
        value = node.key
        if node.left is not None:
            value = self.rake(value, node.left.sum)
        if node.right is not None:
            value = self.rake(value, node.right.sum)
        node.sum = value

    def _rotate_right(self, node):
        parent = node.parent
        grandparent = parent.parent
        parent.left = node.right
        if node.right is not None:
            node.right.parent = parent
        node.right = parent
        parent.parent = node
        self._update(parent)
        self._update(node)
        node.parent = grandparent
        if grandparent is not None:
            if grandparent.left is parent:
                grandparent.left = node
            if grandparent.right is parent:
                grandparent.right = node

    def _rotate_left(self, node):
        parent = node.parent
        grandparent = parent.parent
        parent.right = node.left
        if node.left is not None:
            node.left.parent = parent
        node.left = parent
        parent.parent = node
        self._update(parent)
        self._update(node)
        node.parent = grandparent
        if grandparent is not None:
            if grandparent.left is parent:
                grandparent.left = node
            if grandparent.right is parent:
                grandparent.right = node

    def splay(self, node):
        while node.parent is not None:
            parent = node.parent
            grandparent = parent.parent
            if grandparent is None:
                if parent.left is node:
                    self._rotate_right(node)
                else:
                    self._rotate_left(node)
            elif grandparent.left is parent:
                if parent.left is node:
                    self._rotate_right(parent)
                    self._rotate_right(node)
                else:
                    self._rotate_left(node)
                    self._rotate_right(node)
            else:
                if parent.right is node:
                    self._rotate_left(parent)
                    self._rotate_left(node)
                else:
                    self._rotate_right(node)
                    self._rotate_left(node)

    @staticmethod
    def _rightmost(node):
        while node.right is not None:
            node = node.right
        return node

    def insert(self, root, value):
        created = _DashedNode(value)
        if root is None:
            return created
        current = self._rightmost(root)
        self.splay(current)
        created.parent = current
        current.right = created
        self._update(current)
        self.splay(created)
        return created

    def erase(self, node):
        self.splay(node)
        left = node.left
        right = node.right
        if left is None:
            if right is not None:
                right.parent = None
            return right
        if right is None:
            left.parent = None
            return left
        left.parent = None
        root = self._rightmost(left)
        self.splay(root)
        root.right = right
        right.parent = root
        self._update(root)
        return root


class _TopNode:
    __slots__ = (
        "left", "right", "parent", "info", "key", "sum", "reverse_sum",
        "light", "belong", "reversed",
    )

    def __init__(self, info):
        self.left = self.right = self.parent = None
        self.info = info
        self.key = self.sum = self.reverse_sum = None
        self.light = self.belong = None
        self.reversed = False

    def is_root(self):
        return (self.parent is None
                or self.parent.left is not self and self.parent.right is not self)


class TopTree:
    __slots__ = (
        "vertex", "compress", "rake", "add_edge", "add_vertex", "dashed",
    )

    def __init__(self, vertex, compress, rake, add_edge, add_vertex):
        self.vertex = vertex
        self.compress = compress
        self.rake = rake
        self.add_edge = add_edge
        self.add_vertex = add_vertex
        self.dashed = _DashedSplay(rake)

    @staticmethod
    def _toggle(node):
        node.left, node.right = node.right, node.left
        node.sum, node.reverse_sum = node.reverse_sum, node.sum
        node.reversed = not node.reversed

    def push(self, node):
        if node.reversed:
            if node.left is not None:
                self._toggle(node.left)
            if node.right is not None:
                self._toggle(node.right)
            node.reversed = False

    push_rev = push

    def update(self, node):
        key = (self.add_vertex(node.light.sum, node.info)
               if node.light is not None else self.vertex(node.info))
        forward = backward = key
        if node.left is not None:
            forward = self.compress(node.left.sum, forward)
            backward = self.compress(backward, node.left.reverse_sum)
        if node.right is not None:
            forward = self.compress(forward, node.right.sum)
            backward = self.compress(node.right.reverse_sum, backward)
        node.key = key
        node.sum = forward
        node.reverse_sum = backward

    def _rotate_right(self, node):
        parent = node.parent
        grandparent = parent.parent
        self.push(parent)
        self.push(node)
        parent.left = node.right
        if node.right is not None:
            node.right.parent = parent
        node.right = parent
        parent.parent = node
        self.update(parent)
        self.update(node)
        node.parent = grandparent
        if grandparent is not None:
            if grandparent.left is parent:
                grandparent.left = node
            if grandparent.right is parent:
                grandparent.right = node

    def _rotate_left(self, node):
        parent = node.parent
        grandparent = parent.parent
        self.push(parent)
        self.push(node)
        parent.right = node.left
        if node.left is not None:
            node.left.parent = parent
        node.left = parent
        parent.parent = node
        self.update(parent)
        self.update(node)
        node.parent = grandparent
        if grandparent is not None:
            if grandparent.left is parent:
                grandparent.left = node
            if grandparent.right is parent:
                grandparent.right = node

    def splay(self, node):
        self.push(node)
        auxiliary_root = node
        while not auxiliary_root.is_root():
            auxiliary_root = auxiliary_root.parent
        node.belong = auxiliary_root.belong
        if node is not auxiliary_root:
            auxiliary_root.belong = None
        while not node.is_root():
            parent = node.parent
            if parent.is_root():
                self.push(parent)
                self.push(node)
                if parent.left is node:
                    self._rotate_right(node)
                else:
                    self._rotate_left(node)
            else:
                grandparent = parent.parent
                self.push(grandparent)
                self.push(parent)
                self.push(node)
                if grandparent.left is parent:
                    if parent.left is node:
                        self._rotate_right(parent)
                        self._rotate_right(node)
                    else:
                        self._rotate_left(node)
                        self._rotate_right(node)
                else:
                    if parent.right is node:
                        self._rotate_left(parent)
                        self._rotate_left(node)
                    else:
                        self._rotate_right(node)
                        self._rotate_left(node)

    def expose(self, node):
        preferred = None
        current = node
        last = None
        while current is not None:
            self.splay(current)
            if current.right is not None:
                current.light = self.dashed.insert(
                    current.light, self.add_edge(current.right.sum)
                )
                current.right.belong = current.light
            current.right = preferred
            if current.right is not None:
                self.dashed.splay(current.right.belong)
                self.push(current.right)
                current.light = self.dashed.erase(current.right.belong)
            self.update(current)
            preferred = current
            last = current
            current = current.parent
        self.splay(node)
        return last

    def link(self, child, parent):
        self.expose(parent)
        self.expose(child)
        child.parent = parent
        parent.right = child
        self.update(parent)

    def cut(self, child):
        self.expose(child)
        parent = child.left
        if parent is None:
            raise ValueError("the node has no parent")
        child.left = None
        parent.parent = None
        self.update(child)

    def evert(self, node):
        self.expose(node)
        self._toggle(node)
        self.push(node)

    def alloc(self, info):
        node = _TopNode(info)
        self.update(node)
        return node

    def is_connected(self, first, second):
        self.expose(first)
        self.expose(second)
        return first is second or first.parent is not None

    def lca(self, first, second):
        if not self.is_connected(first, second):
            return None
        self.expose(first)
        return self.expose(second)

    def set_key(self, node, info):
        self.expose(node)
        node.info = info
        self.update(node)

    def query(self, node):
        self.evert(node)
        return node.sum

    def query_subtree(self, root, node):
        self.evert(root)
        self.expose(node)
        left = node.left
        node.left = None
        self.update(node)
        result = node.sum
        node.left = left
        self.update(node)
        return result


class DynamicRerooting:
    __slots__ = ("n", "top_tree", "vertices")

    def __init__(self, info, vertex, compress, rake, add_edge, add_vertex):
        self.n = len(info)
        self.top_tree = TopTree(vertex, compress, rake, add_edge, add_vertex)
        self.vertices = [self.top_tree.alloc(value) for value in info]

    def add_edge(self, first, second):
        self.top_tree.evert(self.vertices[first])
        self.top_tree.link(self.vertices[first], self.vertices[second])

    link = add_edge

    def delete_edge(self, first, second):
        self.top_tree.evert(self.vertices[first])
        self.top_tree.cut(self.vertices[second])

    del_edge = delete_edge
    cut = delete_edge

    def get_info(self, vertex):
        return self.vertices[vertex].info

    def set_info(self, vertex, info):
        self.top_tree.set_key(self.vertices[vertex], info)

    def query(self, root):
        return self.top_tree.query(self.vertices[root])

    def query_subtree(self, root, vertex):
        return self.top_tree.query_subtree(
            self.vertices[root], self.vertices[vertex]
        )
