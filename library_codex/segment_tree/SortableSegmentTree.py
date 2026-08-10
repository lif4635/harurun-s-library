"""部分列の昇順・降順sortと区間monoid積を処理する列構造。"""

class SortableSegmentTree:
    """Sortable sequence with O(log N) point update and monoid range product."""

    __slots__ = (
        "n", "keys", "values", "op", "identity", "size", "tree"
    )

    def __init__(self, keys, values, op=lambda a, b: a + b, identity=0):
        if len(keys) != len(values):
            raise ValueError("key and value lengths differ")
        self.n = len(keys)
        self.keys = list(keys)
        self.values = list(values)
        self.op = op
        self.identity = identity
        size = 1
        while size < self.n:
            size <<= 1
        self.size = size
        tree = [identity] * (size << 1)
        tree[size:size + self.n] = self.values
        for node in range(size - 1, 0, -1):
            tree[node] = op(tree[node << 1], tree[node << 1 | 1])
        self.tree = tree

    def _rebuild_range(self, left, right):
        if left >= right:
            return
        size = self.size
        tree = self.tree
        tree[size + left:size + right] = self.values[left:right]
        left += size
        right += size
        op = self.op
        while left > 1:
            left >>= 1
            right = (right + 1) >> 1
            for node in range(left, right):
                tree[node] = op(tree[node << 1], tree[node << 1 | 1])

    def update(self, index, key, value):
        self.keys[index] = key
        self.values[index] = value
        node = self.size + index
        tree = self.tree
        tree[node] = value
        op = self.op
        while node > 1:
            node >>= 1
            tree[node] = op(tree[node << 1], tree[node << 1 | 1])

    def query(self, left, right):
        left += self.size
        right += self.size
        left_result = right_result = self.identity
        tree = self.tree
        op = self.op
        while left < right:
            if left & 1:
                left_result = op(left_result, tree[left])
                left += 1
            if right & 1:
                right -= 1
                right_result = op(tree[right], right_result)
            left >>= 1
            right >>= 1
        return op(left_result, right_result)

    def sort(self, left, right, reverse=False):
        pairs = sorted(
            zip(self.keys[left:right], self.values[left:right]),
            key=lambda pair: pair[0],
            reverse=reverse,
        )
        self.keys[left:right] = [pair[0] for pair in pairs]
        self.values[left:right] = [pair[1] for pair in pairs]
        self._rebuild_range(left, right)
