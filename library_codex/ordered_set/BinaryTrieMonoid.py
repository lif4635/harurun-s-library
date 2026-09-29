"""整数キーに値を持ち、点更新とキーの半開区間のモノイド積を求める。"""


class BinaryTrieMonoid:
    __slots__ = ("bit_length", "op", "identity", "commutative", "left", "right",
                 "bit", "key", "data", "root", "lazy", "free", "size")

    def __init__(self, op, identity, bit_length=30, *, commutative=False):
        if bit_length <= 0:
            raise ValueError("bit_length must be positive")
        self.bit_length = bit_length
        self.op = op
        self.identity = identity
        self.commutative = commutative
        self.left = []
        self.right = []
        self.bit = []
        self.key = []
        self.data = []
        self.root = -1
        self.lazy = 0
        self.free = []
        self.size = 0

    def _new(self, key, bit, left, right, data):
        if self.free:
            node = self.free.pop()
            self.key[node] = key
            self.bit[node] = bit
            self.left[node] = left
            self.right[node] = right
            self.data[node] = data
            return node
        node = len(self.data)
        self.key.append(key)
        self.bit.append(bit)
        self.left.append(left)
        self.right.append(right)
        self.data.append(data)
        return node

    def set(self, key, value):
        if not 0 <= key < 1 << self.bit_length:
            raise ValueError("key is outside the bit range")
        key ^= self.lazy
        node = self.root
        if node < 0:
            self.root = self._new(key, -1, -1, -1, value)
            self.size = 1
            return
        left, right, bit, keys, data, op = self.left, self.right, self.bit, self.key, self.data, self.op
        path = []
        while bit[node] >= 0:
            path.append(node)
            node = right[node] if key >> bit[node] & 1 else left[node]
        diff = (key ^ keys[node]).bit_length() - 1
        if diff < 0:
            data[node] = value
        else:
            length = 0
            node = self.root
            while length < len(path) and bit[path[length]] > diff:
                ancestor = path[length]
                node = right[ancestor] if key >> bit[ancestor] & 1 else left[ancestor]
                length += 1
            del path[length:]
            leaf = self._new(key, -1, -1, -1, value)
            if key >> diff & 1:
                branch = self._new(key, diff, node, leaf, op(data[node], value))
            else:
                branch = self._new(key, diff, leaf, node, op(value, data[node]))
            if not path:
                self.root = branch
            elif key >> bit[path[-1]] & 1:
                right[path[-1]] = branch
            else:
                left[path[-1]] = branch
            self.size += 1
        for parent in reversed(path):
            data[parent] = op(data[left[parent]], data[right[parent]])

    def get(self, key):
        if not 0 <= key < 1 << self.bit_length:
            return self.identity
        key ^= self.lazy
        node = self.root
        if node < 0:
            return self.identity
        left, right, bit = self.left, self.right, self.bit
        while bit[node] >= 0:
            node = right[node] if key >> bit[node] & 1 else left[node]
        return self.data[node] if self.key[node] == key else self.identity

    def discard(self, key):
        if self.root < 0 or not 0 <= key < 1 << self.bit_length:
            return False
        key ^= self.lazy
        node = self.root
        left, right, bit, data, op = self.left, self.right, self.bit, self.data, self.op
        path = []
        while bit[node] >= 0:
            path.append(node)
            node = right[node] if key >> bit[node] & 1 else left[node]
        if self.key[node] != key:
            return False
        self.size -= 1
        data[node] = self.identity
        self.free.append(node)
        if not path:
            self.root = -1
            return True
        parent = path.pop()
        sibling = left[parent] if right[parent] == node else right[parent]
        data[parent] = self.identity
        self.free.append(parent)
        if not path:
            self.root = sibling
        elif left[path[-1]] == parent:
            left[path[-1]] = sibling
        else:
            right[path[-1]] = sibling
        for parent in reversed(path):
            data[parent] = op(data[left[parent]], data[right[parent]])
        return True

    def prod(self, left, right):
        result = self.identity
        if left >= right or self.root < 0:
            return result
        low, high, bit, keys, data, op, lazy = self.left, self.right, self.bit, self.key, self.data, self.op, self.lazy
        stack = [self.root]
        while stack:
            node = stack.pop()
            shift = bit[node] + 1
            start = (keys[node] ^ lazy) >> shift << shift
            end = start + (1 << shift)
            if right <= start or end <= left:
                continue
            if left <= start and end <= right:
                result = op(result, data[node])
            elif lazy >> bit[node] & 1:
                stack.append(low[node])
                stack.append(high[node])
            else:
                stack.append(high[node])
                stack.append(low[node])
        return result

    def all_prod(self):
        return self.data[self.root] if self.root >= 0 else self.identity

    def xor_all(self, mask):
        if not 0 <= mask < 1 << self.bit_length:
            raise ValueError("xor mask is outside the bit range")
        if mask and not self.commutative:
            raise ValueError("xor_all requires commutative=True")
        self.lazy ^= mask

    def items(self):
        result = []
        if self.root < 0:
            return result
        left, right, bit, lazy = self.left, self.right, self.bit, self.lazy
        stack = [self.root]
        while stack:
            node = stack.pop()
            if bit[node] < 0:
                result.append((self.key[node] ^ lazy, self.data[node]))
            elif lazy >> bit[node] & 1:
                stack.append(left[node])
                stack.append(right[node])
            else:
                stack.append(right[node])
                stack.append(left[node])
        return result

    def __len__(self):
        return self.size

    def __str__(self):
        return str(dict(self.items()))

    def __repr__(self):
        return "BinaryTrieMonoid(%r)" % dict(self.items())
