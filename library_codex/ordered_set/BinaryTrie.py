"""整数multisetの追加・削除、順位、XOR最小値を圧縮binary trieで扱う。"""


class BinaryTrie:
    __slots__ = ("bit_length", "left", "right", "bit", "key", "count", "root", "lazy", "free")

    def __init__(self, bit_length=30):
        if bit_length <= 0:
            raise ValueError("bit_length must be positive")
        self.bit_length = bit_length
        self.left = []
        self.right = []
        self.bit = []
        self.key = []
        self.count = []
        self.root = -1
        self.lazy = 0
        self.free = []

    def _new(self, key, bit, left, right, count):
        if self.free:
            node = self.free.pop()
            self.key[node] = key
            self.bit[node] = bit
            self.left[node] = left
            self.right[node] = right
            self.count[node] = count
            return node
        node = len(self.count)
        self.key.append(key)
        self.bit.append(bit)
        self.left.append(left)
        self.right.append(right)
        self.count.append(count)
        return node

    def add(self, value, amount=1):
        if not 0 <= value < 1 << self.bit_length:
            raise ValueError("value is outside the bit range")
        if amount <= 0:
            return
        value ^= self.lazy
        node = self.root
        if node < 0:
            self.root = self._new(value, -1, -1, -1, amount)
            return
        left, right, bit, key, count = self.left, self.right, self.bit, self.key, self.count
        path = []
        while bit[node] >= 0:
            path.append(node)
            node = right[node] if value >> bit[node] & 1 else left[node]
        diff = (value ^ key[node]).bit_length() - 1
        if diff < 0:
            count[node] += amount
            for parent in path:
                count[parent] += amount
            return
        parent = -1
        node = self.root
        for ancestor in path:
            if bit[ancestor] <= diff:
                break
            count[ancestor] += amount
            parent = ancestor
            node = right[ancestor] if value >> bit[ancestor] & 1 else left[ancestor]
        leaf = self._new(value, -1, -1, -1, amount)
        if value >> diff & 1:
            branch = self._new(value, diff, node, leaf, count[node] + amount)
        else:
            branch = self._new(value, diff, leaf, node, count[node] + amount)
        if parent < 0:
            self.root = branch
        elif value >> bit[parent] & 1:
            right[parent] = branch
        else:
            left[parent] = branch

    def count_value(self, value):
        if not 0 <= value < 1 << self.bit_length:
            return 0
        value ^= self.lazy
        node = self.root
        left, right, bit = self.left, self.right, self.bit
        if node < 0:
            return 0
        while bit[node] >= 0:
            node = right[node] if value >> bit[node] & 1 else left[node]
        return self.count[node] if self.key[node] == value else 0

    def discard(self, value, amount=1):
        if amount <= 0 or not 0 <= value < 1 << self.bit_length or self.root < 0:
            return 0
        value ^= self.lazy
        node = self.root
        left, right, bit, count = self.left, self.right, self.bit, self.count
        path = []
        while bit[node] >= 0:
            path.append(node)
            node = right[node] if value >> bit[node] & 1 else left[node]
        if self.key[node] != value:
            return 0
        amount = min(amount, count[node])
        count[node] -= amount
        for parent in path:
            count[parent] -= amount
        if count[node] == 0:
            self.free.append(node)
            if not path:
                self.root = -1
            else:
                parent = path.pop()
                sibling = left[parent] if right[parent] == node else right[parent]
                self.free.append(parent)
                if not path:
                    self.root = sibling
                elif left[path[-1]] == parent:
                    left[path[-1]] = sibling
                else:
                    right[path[-1]] = sibling
        return amount

    def xor_all(self, value):
        if not 0 <= value < 1 << self.bit_length:
            raise ValueError("xor mask is outside the bit range")
        self.lazy ^= value

    def kth(self, index):
        node = self.root
        if node < 0 or not 0 <= index < self.count[node]:
            raise IndexError("kth index out of range")
        left, right, bit, count, lazy = self.left, self.right, self.bit, self.count, self.lazy
        while bit[node] >= 0:
            if lazy >> bit[node] & 1:
                zero, one = right[node], left[node]
            else:
                zero, one = left[node], right[node]
            if index < count[zero]:
                node = zero
            else:
                index -= count[zero]
                node = one
        return self.key[node] ^ lazy

    def min(self):
        return self.kth(0)

    def max(self):
        return self.kth(len(self) - 1)

    def bisect_left(self, value):
        node = self.root
        result = 0
        left, right, bit, key, count, lazy = self.left, self.right, self.bit, self.key, self.count, self.lazy
        while node >= 0:
            shift = bit[node] + 1
            prefix = (key[node] ^ lazy) >> shift
            target = value >> shift
            if prefix < target:
                return result + count[node]
            if prefix > target or shift == 0:
                return result
            if lazy >> bit[node] & 1:
                zero, one = right[node], left[node]
            else:
                zero, one = left[node], right[node]
            if value >> bit[node] & 1:
                result += count[zero]
                node = one
            else:
                node = zero
        return result

    def xor_min(self, value):
        node = self.root
        if node < 0:
            raise IndexError("xor_min from empty BinaryTrie")
        if value < 0:
            raise ValueError("xor query must be nonnegative")
        physical = value ^ self.lazy
        left, right, bit = self.left, self.right, self.bit
        while bit[node] >= 0:
            node = right[node] if physical >> bit[node] & 1 else left[node]
        return self.key[node] ^ self.lazy

    def xor_max(self, value):
        if value < 0:
            raise ValueError("xor query must be nonnegative")
        return self.xor_min(value ^ ((1 << self.bit_length) - 1))

    def __contains__(self, value):
        return self.count_value(value) > 0

    def __len__(self):
        return self.count[self.root] if self.root >= 0 else 0

    def tolist(self):
        result = []
        if self.root < 0:
            return result
        left, right, bit, lazy = self.left, self.right, self.bit, self.lazy
        stack = [self.root]
        while stack:
            node = stack.pop()
            if bit[node] < 0:
                result.extend([self.key[node] ^ lazy] * self.count[node])
            elif lazy >> bit[node] & 1:
                stack.append(left[node])
                stack.append(right[node])
            else:
                stack.append(right[node])
                stack.append(left[node])
        return result

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "BinaryTrie(%r)" % self.tolist()
