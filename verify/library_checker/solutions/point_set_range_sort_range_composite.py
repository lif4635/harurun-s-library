class FastSet:
    __slots__ = ('n', 'level', 'size')

    def __init__(self, size, values=()):
        if size < 0:
            raise ValueError('size must be nonnegative')
        level = []
        length = size
        while True:
            level.append([0] * (length + 63 >> 6))
            if length <= 64:
                break
            length = length + 63 >> 6
        self.n = size
        self.level = level
        self.size = 0
        for value in values:
            self.add(value)

    def add(self, value):
        if not 0 <= value < self.n:
            raise IndexError('value is out of range')
        level = self.level
        index = value
        word_index = index >> 6
        mask = 1 << (index & 63)
        if level[0][word_index] & mask:
            return False
        self.size += 1
        for words in level:
            word_index = index >> 6
            mask = 1 << (index & 63)
            old = words[word_index]
            words[word_index] = old | mask
            if old:
                break
            index = word_index
        return True
    insert = add

    def discard(self, value):
        if not 0 <= value < self.n:
            return False
        level = self.level
        index = value
        word_index = index >> 6
        mask = 1 << (index & 63)
        if not level[0][word_index] & mask:
            return False
        self.size -= 1
        for words in level:
            word_index = index >> 6
            words[word_index] &= ~(1 << (index & 63))
            if words[word_index]:
                break
            index = word_index
        return True
    erase = discard

    def next(self, value):
        if value < 0:
            value = 0
        if value >= self.n:
            return -1
        index = value
        found_level = -1
        for (height, words) in enumerate(self.level):
            word_index = index >> 6
            if word_index >= len(words):
                return -1
            shifted = words[word_index] >> (index & 63)
            if shifted:
                index += (shifted & -shifted).bit_length() - 1
                found_level = height
                break
            index = word_index + 1
        if found_level < 0:
            return -1
        for height in range(found_level - 1, -1, -1):
            index <<= 6
            word = self.level[height][index >> 6]
            index += (word & -word).bit_length() - 1
        return index if index < self.n else -1
    ge = next

    def prev(self, value):
        if value >= self.n:
            value = self.n - 1
        if value < 0:
            return -1
        index = value
        found_level = -1
        for (height, words) in enumerate(self.level):
            word_index = index >> 6
            mask = words[word_index] & (1 << (index & 63) + 1) - 1
            if mask:
                index = (word_index << 6) + mask.bit_length() - 1
                found_level = height
                break
            if word_index == 0:
                return -1
            index = word_index - 1
        if found_level < 0:
            return -1
        for height in range(found_level - 1, -1, -1):
            index = index << 6 | 63
            words = self.level[height]
            word_index = index >> 6
            if word_index >= len(words):
                word_index = len(words) - 1
            word = words[word_index]
            index = (word_index << 6) + word.bit_length() - 1
        return index
    le = prev

    def min(self):
        value = self.next(0)
        if value < 0:
            raise ValueError('min of empty FastSet')
        return value

    def max(self):
        value = self.prev(self.n - 1)
        if value < 0:
            raise ValueError('max of empty FastSet')
        return value

    def __contains__(self, value):
        return 0 <= value < self.n and bool(self.level[0][value >> 6] >> (value & 63) & 1)

    def __len__(self):
        return self.size

    def tolist(self):
        """保持する整数を昇順listで返す。O(K log_64 N)。"""
        result = []
        value = self.next(0)
        while value >= 0:
            result.append(value)
            value = self.next(value + 1)
        return result

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'FastSet(%r)' % self.tolist()
'Point updates and range products for an arbitrary monoid.\n\nUse this when values change one position at a time and a half-open interval\nmust be folded with an associative operation.  ``max_right`` and ``min_left``\nalso find the first boundary where a monotone predicate stops holding.\n'

class SegTree:
    __slots__ = ('n', 'size', 'log', 'data', 'op', 'identity')

    def __init__(self, op, identity, values):
        if isinstance(values, int):
            n = values
            values = [identity] * n
        else:
            values = list(values)
            n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        data = [identity] * (size << 1)
        data[size:size + n] = values
        for node in range(size - 1, 0, -1):
            data[node] = op(data[node << 1], data[node << 1 | 1])
        self.n = n
        self.size = size
        self.log = size.bit_length() - 1
        self.data = data
        self.op = op
        self.identity = identity

    def set(self, index, value):
        node = index + self.size
        data = self.data
        data[node] = value
        op = self.op
        node >>= 1
        while node:
            data[node] = op(data[node << 1], data[node << 1 | 1])
            node >>= 1

    def add(self, index, value):
        """indexの現在値をop(value, current)で置き換える。O(log N)。"""
        node = index + self.size
        data = self.data
        op = self.op
        data[node] = op(value, data[node])
        node >>= 1
        while node:
            data[node] = op(data[node << 1], data[node << 1 | 1])
            node >>= 1

    def get(self, index):
        return self.data[index + self.size]

    def tolist(self):
        """現在の要素列をlistで返す。O(N)。"""
        return self.data[self.size:self.size + self.n]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'SegTree(%r)' % self.tolist()

    def prod(self, left, right):
        left += self.size
        right += self.size
        first = self.identity
        second = self.identity
        data = self.data
        op = self.op
        while left < right:
            if left & 1:
                first = op(first, data[left])
                left += 1
            if right & 1:
                right -= 1
                second = op(data[right], second)
            left >>= 1
            right >>= 1
        return op(first, second)
    query = prod

    def all_prod(self):
        return self.data[1]

    def max_right(self, left, predicate):
        if left == self.n:
            return self.n
        left += self.size
        value = self.identity
        data = self.data
        op = self.op
        while True:
            while not left & 1:
                left >>= 1
            merged = op(value, data[left])
            if not predicate(merged):
                while left < self.size:
                    left <<= 1
                    merged = op(value, data[left])
                    if predicate(merged):
                        value = merged
                        left += 1
                return min(left - self.size, self.n)
            value = merged
            left += 1
            if left & -left == left:
                break
        return self.n

    def min_left(self, right, predicate):
        if right == 0:
            return 0
        right += self.size
        value = self.identity
        data = self.data
        op = self.op
        while True:
            right -= 1
            while right > 1 and right & 1:
                right >>= 1
            merged = op(data[right], value)
            if not predicate(merged):
                while right < self.size:
                    right = right << 1 | 1
                    merged = op(data[right], value)
                    if predicate(merged):
                        value = merged
                        right -= 1
                return max(0, right + 1 - self.size)
            value = merged
            if right & -right == right:
                break
        return 0

    def __getitem__(self, index):
        return self.get(index)
'区間をキーで並べ替えながら、値の更新と非可換な区間積を扱う。'

class SortableArray:
    """相異なる整数キーと値の組を、現在の配列順で管理する。"""
    __slots__ = ('n', 'op', 'identity', '_keys', '_values', '_used', '_left', '_right', '_size', '_priority', '_forward', '_backward', '_roots', '_reverse', '_starts', '_seg')

    def __init__(self, op, identity, items):
        items = list(items)
        keys = [key for (key, value) in items]
        used = set(keys)
        if len(used) != len(keys):
            raise ValueError('keys must be distinct')
        self.n = n = len(items)
        self.op = op
        self.identity = identity
        self._keys = [0] + keys
        self._values = [identity] + [value for (key, value) in items]
        self._used = used
        self._left = [0] * (n + 1)
        self._right = [0] * (n + 1)
        self._size = [0] + [1] * n
        self._priority = [0]
        state = 712367821
        for _ in items:
            state ^= state << 13 & 4294967295
            state ^= state >> 17
            state ^= state << 5 & 4294967295
            self._priority.append(state)
        self._forward = self._values[:]
        self._backward = self._values[:]
        self._roots = list(range(1, n + 1))
        self._reverse = bytearray(n)
        self._starts = FastSet(n + 1, range(n + 1))
        self._seg = SegTree(op, identity, self._values[1:])

    def _pull(self, node):
        left = self._left[node]
        right = self._right[node]
        self._size[node] = self._size[left] + self._size[right] + 1
        op = self.op
        value = self._values[node]
        self._forward[node] = op(op(self._forward[left], value), self._forward[right])
        self._backward[node] = op(op(self._backward[right], value), self._backward[left])

    def _split(self, root, key, by_key=False):
        path = []
        left = self._left
        right = self._right
        sizes = self._size
        keys = self._keys
        while root:
            take = keys[root] < key if by_key else sizes[left[root]] < key
            if take:
                if not by_key:
                    key -= sizes[left[root]] + 1
                path.append(root)
                root = right[root]
            else:
                path.append(-root)
                root = left[root]
        first = second = 0
        for node in reversed(path):
            if node > 0:
                right[node] = first
                self._pull(node)
                first = node
            else:
                node = -node
                left[node] = second
                self._pull(node)
                second = node
        return (first, second)

    def _union(self, first, second):
        stack = [(first, second, False)]
        results = []
        left = self._left
        right = self._right
        priorities = self._priority
        while stack:
            (a, b, finish) = stack.pop()
            if finish:
                right[a] = results.pop()
                left[a] = results.pop()
                self._pull(a)
                results.append(a)
            elif not a or not b:
                results.append(a or b)
            else:
                if priorities[a] < priorities[b]:
                    (a, b) = (b, a)
                (low, high) = self._split(b, self._keys[a], True)
                stack.append((a, 0, True))
                stack.append((right[a], high, False))
                stack.append((left[a], low, False))
        return results[0]

    def _cut(self, index):
        if index in self._starts:
            return
        start = self._starts.prev(index)
        root = self._roots[start]
        reverse = self._reverse[start]
        count = index - start
        if reverse:
            count = self._size[root] - count
        (first, second) = self._split(root, count)
        if reverse:
            (first, second) = (second, first)
        self._roots[start] = first
        self._roots[index] = second
        self._reverse[index] = reverse
        self._starts.add(index)
        values = self._backward if reverse else self._forward
        self._seg.set(start, values[first])
        self._seg.set(index, values[second])

    def _range(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError('invalid half-open range')

    def get(self, index):
        """現在のindex番目にある(key, value)を返す。"""
        if not 0 <= index < self.n:
            raise IndexError('index out of range')
        start = self._starts.prev(index)
        root = self._roots[start]
        rank = index - start
        if self._reverse[start]:
            rank = self._size[root] - 1 - rank
        while True:
            count = self._size[self._left[root]]
            if rank == count:
                return (self._keys[root], self._values[root])
            if rank < count:
                root = self._left[root]
            else:
                rank -= count + 1
                root = self._right[root]

    def set(self, index, key, value):
        """現在のindex番目のキーと値を置き換える。"""
        (old, _) = self.get(index)
        if key != old and key in self._used:
            raise ValueError('key is already present')
        self._cut(index)
        self._cut(index + 1)
        node = self._roots[index]
        self._used.remove(old)
        self._used.add(key)
        self._keys[node] = key
        self._values[node] = value
        self._forward[node] = self._backward[node] = value
        self._seg.set(index, value)

    def sort(self, left, right, reverse=False):
        """半開区間[left, right)をキーの昇順、reverse=Trueなら降順にする。"""
        self._range(left, right)
        if right - left <= 1:
            return
        self._cut(left)
        self._cut(right)
        root = self._roots[left]
        index = self._starts.next(left + 1)
        while index < right:
            root = self._union(root, self._roots[index])
            self._roots[index] = 0
            self._starts.discard(index)
            self._seg.set(index, self.identity)
            index = self._starts.next(index + 1)
        self._roots[left] = root
        self._reverse[left] = bool(reverse)
        self._seg.set(left, self._backward[root] if reverse else self._forward[root])

    def prod(self, left, right):
        """半開区間[left, right)の値を、現在の左から右への順でopで畳み込む。"""
        self._range(left, right)
        if left == right:
            return self.identity
        self._cut(left)
        self._cut(right)
        return self._seg.prod(left, right)

    def all_prod(self):
        """現在の配列全体の値を、左から右への順でopで畳み込んだ値を返す。"""
        return self._seg.all_prod()

    def tolist(self):
        """現在の配列順の(key, value)を並べたlistを返す。"""
        result = []
        start = self._starts.next(0)
        while start < self.n:
            root = self._roots[start]
            (left, right) = (self._left, self._right)
            if self._reverse[start]:
                (left, right) = (right, left)
            stack = []
            while root or stack:
                while root:
                    stack.append(root)
                    root = left[root]
                root = stack.pop()
                result.append((self._keys[root], self._values[root]))
                root = right[root]
            start = self._starts.next(start + 1)
        return result

    def __len__(self):
        return self.n

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'SortableArray(%r)' % self.tolist()
import sys

def op(first, second):
    (a, b) = (first >> 30, first & 1073741823)
    (c, d) = (second >> 30, second & 1073741823)
    return a * c % 998244353 << 30 | (b * c + d) % 998244353
read = sys.stdin.buffer.readline
(n, q) = map(int, read().split())
items = []
for _ in range(n):
    (key, a, b) = map(int, read().split())
    items.append((key, a << 30 | b))
data = SortableArray(op, 1 << 30, items)
answers = []
for _ in range(q):
    query = list(map(int, read().split()))
    (kind, left, right) = query[:3]
    if kind == 0:
        data.set(left, right, query[3] << 30 | query[4])
    elif kind == 1:
        value = data.prod(left, right)
        answers.append(str(((value >> 30) * query[3] + (value & 1073741823)) % 998244353))
    else:
        data.sort(left, right, kind == 3)
sys.stdout.write('\n'.join(answers) + '\n')
