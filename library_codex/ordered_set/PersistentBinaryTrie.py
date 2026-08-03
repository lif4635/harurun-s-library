"""過去versionの整数multisetでk番目・xor最小を扱う永続binary trie。"""

from operator import add

class PersistentBinaryTrie:
    __slots__ = ("bit_length", "left", "right", "count", "roots")

    def __init__(self, bit_length=30):
        self.bit_length = bit_length
        self.left = [-1]
        self.right = [-1]
        self.count = [0]
        self.roots = [0]

    def _clone(self, node):
        new_node = len(self.count)
        if node < 0:
            self.left.append(-1)
            self.right.append(-1)
            self.count.append(0)
        else:
            self.left.append(self.left[node])
            self.right.append(self.right[node])
            self.count.append(self.count[node])
        return new_node

    def count_value(self, value, version=-1):
        node = self.roots[version]
        for bit in range(self.bit_length - 1, -1, -1):
            node = self.right[node] if value >> bit & 1 else self.left[node]
            if node < 0:
                return 0
        return self.count[node]

    def add(self, value, version=-1, amount=1):
        if amount < 0 and self.count_value(value, version) < -amount:
            raise ValueError("negative multiplicity")
        old = self.roots[version]
        root = self._clone(old)
        self.count[root] += amount
        node = root
        for bit in range(self.bit_length - 1, -1, -1):
            direction = value >> bit & 1
            old_child = (
                self.right[old] if direction else self.left[old]
            ) if old >= 0 else -1
            child = self._clone(old_child)
            self.count[child] += amount
            if direction:
                self.right[node] = child
            else:
                self.left[node] = child
            node = child
            old = old_child
        self.roots.append(root)
        return len(self.roots) - 1

    insert = add

    def discard(self, value, version=-1, amount=1):
        amount = min(amount, self.count_value(value, version))
        return self.add(value, version, -amount)

    def kth(self, index, version=-1, xor=0):
        node = self.roots[version]
        if index < 0 or index >= self.count[node]:
            raise IndexError("kth index out of range")
        value = 0
        for bit in range(self.bit_length - 1, -1, -1):
            direction = xor >> bit & 1
            zero = self.right[node] if direction else self.left[node]
            zero_count = self.count[zero] if zero >= 0 else 0
            if index < zero_count:
                node = zero
            else:
                index -= zero_count
                node = self.left[node] if direction else self.right[node]
                value |= 1 << bit
        return value

    def xor_min(self, value, version=-1):
        return self.kth(0, version, value)

    def __len__(self):
        return self.count[self.roots[-1]]
