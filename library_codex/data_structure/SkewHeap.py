"""heap同士のmeldと全要素へのlazy加算に対応するSkew Heap。"""

class SkewHeap:
    """Array-backed meldable heap with whole-heap additive lazy action."""

    __slots__ = ("min_heap", "key", "value", "left", "right", "lazy")

    def __init__(self, min_heap=True):
        self.min_heap = min_heap
        self.key = []
        self.value = []
        self.left = []
        self.right = []
        self.lazy = []

    def new_node(self, key, value=None):
        node = len(self.key)
        self.key.append(key)
        self.value.append(value)
        self.left.append(-1)
        self.right.append(-1)
        self.lazy.append(0)
        return node

    def _better(self, first, second):
        a = self.key[first] + self.lazy[first]
        b = self.key[second] + self.lazy[second]
        return a < b if self.min_heap else a > b

    def _push(self, node):
        action = self.lazy[node]
        if action:
            self.key[node] += action
            left = self.left[node]
            right = self.right[node]
            if left >= 0:
                self.lazy[left] += action
            if right >= 0:
                self.lazy[right] += action
            self.lazy[node] = 0

    def meld(self, first, second):
        if first < 0:
            return second
        if second < 0:
            return first
        path = []
        while first >= 0 and second >= 0:
            if not self._better(first, second):
                first, second = second, first
            self._push(first)
            path.append(first)
            first = self.right[first]
        root = first if first >= 0 else second
        for node in reversed(path):
            self.right[node] = root
            self.left[node], self.right[node] = self.right[node], self.left[node]
            root = node
        return root

    def push(self, root, key, value=None):
        return self.meld(root, self.new_node(key, value))

    def add_all(self, root, delta):
        if root >= 0:
            self.lazy[root] += delta
        return root

    apply = add_all

    def top(self, root):
        if root < 0:
            raise IndexError("empty skew heap")
        self._push(root)
        return self.key[root], self.value[root]

    def pop(self, root):
        if root < 0:
            raise IndexError("empty skew heap")
        self._push(root)
        return self.meld(self.left[root], self.right[root])
