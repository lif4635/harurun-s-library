"""更新ごとに過去のrootを残す永続randomized BST集合。"""

class PersistentRBSTSet:
    """Fully persistent immutable-key treap; roots are integer version handles."""

    __slots__ = ("key", "priority", "left", "right", "size", "serial", "roots")

    def __init__(self, values=()):
        self.key = [None]
        self.priority = [0]
        self.left = [0]
        self.right = [0]
        self.size = [0]
        self.serial = 0
        root = 0
        self.roots = [0]
        for value in values:
            root = self.insert_root(root, value)
        self.roots[0] = root

    @staticmethod
    def _mix(value):
        value &= (1 << 64) - 1
        value ^= value >> 30
        value = value * 0xBF58476D1CE4E5B9 & ((1 << 64) - 1)
        value ^= value >> 27
        value = value * 0x94D049BB133111EB & ((1 << 64) - 1)
        return value ^ (value >> 31)

    def _new(self, key, left=0, right=0, priority=None):
        if priority is None:
            self.serial += 1
            priority = self._mix(hash(key) ^ self.serial)
        node = len(self.key)
        self.key.append(key)
        self.priority.append(priority)
        self.left.append(left)
        self.right.append(right)
        self.size.append(1 + self.size[left] + self.size[right])
        return node

    def _copy(self, node, left=None, right=None):
        return self._new(
            self.key[node],
            self.left[node] if left is None else left,
            self.right[node] if right is None else right,
            self.priority[node],
        )

    def _split(self, root, key):
        left_path = []
        right_path = []
        node = root
        while node:
            if self.key[node] < key:
                left_path.append(node)
                node = self.right[node]
            else:
                right_path.append(node)
                node = self.left[node]
        left_root = 0
        for node in reversed(left_path):
            left_root = self._copy(node, right=left_root)
        right_root = 0
        for node in reversed(right_path):
            right_root = self._copy(node, left=right_root)
        return left_root, right_root

    def _merge(self, first, second):
        path = []
        while first and second:
            if self.priority[first] < self.priority[second]:
                path.append((first, 1))
                first = self.right[first]
            else:
                path.append((second, 0))
                second = self.left[second]
        root = first or second
        for node, replace_right in reversed(path):
            root = self._copy(node, right=root) if replace_right else self._copy(
                node, left=root
            )
        return root

    def contains_root(self, root, key):
        while root:
            if key == self.key[root]:
                return True
            root = self.left[root] if key < self.key[root] else self.right[root]
        return False

    def insert_root(self, root, key):
        if self.contains_root(root, key):
            return root
        left, right = self._split(root, key)
        return self._merge(self._merge(left, self._new(key)), right)

    def erase_root(self, root, key):
        path = []
        node = root
        while node and self.key[node] != key:
            direction = key > self.key[node]
            path.append((node, direction))
            node = self.right[node] if direction else self.left[node]
        if not node:
            return root
        result = self._merge(self.left[node], self.right[node])
        for parent, replace_right in reversed(path):
            result = self._copy(parent, right=result) if replace_right else self._copy(
                parent, left=result
            )
        return result

    def insert(self, key, version=-1):
        root = self.insert_root(self.roots[version], key)
        self.roots.append(root)
        return len(self.roots) - 1

    def erase(self, key, version=-1):
        root = self.erase_root(self.roots[version], key)
        self.roots.append(root)
        return len(self.roots) - 1

    def contains(self, key, version=-1):
        return self.contains_root(self.roots[version], key)

    def lower_bound_root(self, root, key):
        result = 0
        while root:
            if self.key[root] < key:
                result += self.size[self.left[root]] + 1
                root = self.right[root]
            else:
                root = self.left[root]
        return result

    def lower_bound(self, key, version=-1):
        return self.lower_bound_root(self.roots[version], key)

    def upper_bound(self, key, version=-1):
        root = self.roots[version]
        result = 0
        while root:
            if self.key[root] <= key:
                result += self.size[self.left[root]] + 1
                root = self.right[root]
            else:
                root = self.left[root]
        return result

    def kth_root(self, root, index):
        if not 0 <= index < self.size[root]:
            raise IndexError("kth index out of range")
        while True:
            left_size = self.size[self.left[root]]
            if index < left_size:
                root = self.left[root]
            elif index == left_size:
                return self.key[root]
            else:
                index -= left_size + 1
                root = self.right[root]

    def kth(self, index, version=-1):
        return self.kth_root(self.roots[version], index)

    def to_list(self, version=-1):
        result = []
        stack = []
        node = self.roots[version]
        while stack or node:
            while node:
                stack.append(node)
                node = self.left[node]
            node = stack.pop()
            result.append(self.key[node])
            node = self.right[node]
        return result
