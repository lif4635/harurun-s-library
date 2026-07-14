from collections import defaultdict, deque
from operator import add

from library_codex.data_structure.SWAG import ErasableHeap


HashMap = dict
HashSet = set
DefaultDict = defaultdict
LinkedList = deque


class BitSet:
    __slots__ = ("n", "bits", "mask")

    def __init__(self, size, value=0):
        if size < 0:
            raise ValueError("size must be nonnegative")
        mask = (1 << size) - 1
        self.n = size
        self.bits = int(value) & mask
        self.mask = mask

    def set(self, index, value=True):
        if value:
            self.bits |= 1 << index
        else:
            self.bits &= ~(1 << index)

    def reset(self, index=None):
        if index is None:
            self.bits = 0
        else:
            self.bits &= ~(1 << index)

    def flip(self, index=None):
        if index is None:
            self.bits ^= self.mask
        else:
            self.bits ^= 1 << index

    def get(self, index):
        return self.bits >> index & 1

    def count(self):
        return self.bits.bit_count()

    def any(self):
        return bool(self.bits)

    def all(self):
        return self.bits == self.mask

    def find_next(self, index):
        shifted = self.bits >> max(0, index)
        if not shifted:
            return -1
        return max(0, index) + (shifted & -shifted).bit_length() - 1

    def find_prev(self, index):
        if index < 0:
            return -1
        value = self.bits & ((1 << (min(index, self.n - 1) + 1)) - 1)
        return value.bit_length() - 1

    def __getitem__(self, index):
        return self.get(index)

    def __len__(self):
        return self.n

    def __int__(self):
        return self.bits

    def __and__(self, other):
        return BitSet(max(self.n, other.n), self.bits & other.bits)

    def __or__(self, other):
        return BitSet(max(self.n, other.n), self.bits | other.bits)

    def __xor__(self, other):
        return BitSet(max(self.n, other.n), self.bits ^ other.bits)

    def __invert__(self):
        return BitSet(self.n, self.bits ^ self.mask)

    def __lshift__(self, shift):
        return BitSet(self.n, self.bits << shift)

    def __rshift__(self, shift):
        return BitSet(self.n, self.bits >> shift)


class TreapSet:
    __slots__ = (
        "root", "key", "priority", "left", "right", "parent", "size", "state"
    )

    def __init__(self, values=()):
        self.root = -1
        self.key = []
        self.priority = []
        self.left = []
        self.right = []
        self.parent = []
        self.size = []
        self.state = 0x9E3779B97F4A7C15
        for value in values:
            self.add(value)

    def _random(self):
        value = self.state
        value ^= value << 7 & ((1 << 64) - 1)
        value ^= value >> 9
        self.state = value
        return value

    def _new(self, key):
        node = len(self.key)
        self.key.append(key)
        self.priority.append(self._random())
        self.left.append(-1)
        self.right.append(-1)
        self.parent.append(-1)
        self.size.append(1)
        return node

    def _update(self, node):
        left = self.left[node]
        right = self.right[node]
        self.size[node] = 1 + (
            self.size[left] if left >= 0 else 0
        ) + (self.size[right] if right >= 0 else 0)

    def _update_up(self, node):
        while node >= 0:
            self._update(node)
            node = self.parent[node]

    def _rotate(self, node):
        parent = self.parent[node]
        grandparent = self.parent[parent]
        if self.left[parent] == node:
            middle = self.right[node]
            self.right[node] = parent
            self.left[parent] = middle
        else:
            middle = self.left[node]
            self.left[node] = parent
            self.right[parent] = middle
        if middle >= 0:
            self.parent[middle] = parent
        self.parent[parent] = node
        self.parent[node] = grandparent
        if grandparent < 0:
            self.root = node
        elif self.left[grandparent] == parent:
            self.left[grandparent] = node
        else:
            self.right[grandparent] = node
        self._update(parent)
        self._update(node)

    def _find(self, key):
        node = self.root
        while node >= 0:
            current = self.key[node]
            if key == current:
                return node
            node = self.left[node] if key < current else self.right[node]
        return -1

    def add(self, key):
        if self.root < 0:
            self.root = self._new(key)
            return True
        node = self.root
        while True:
            current = self.key[node]
            if key == current:
                return False
            if key < current:
                child = self.left[node]
                if child < 0:
                    child = self._new(key)
                    self.left[node] = child
                    self.parent[child] = node
                    break
            else:
                child = self.right[node]
                if child < 0:
                    child = self._new(key)
                    self.right[node] = child
                    self.parent[child] = node
                    break
            node = child
        self._update_up(node)
        while self.parent[child] >= 0 and self.priority[child] < self.priority[self.parent[child]]:
            self._rotate(child)
        self._update_up(self.parent[child])
        return True

    insert = add

    def discard(self, key):
        node = self._find(key)
        if node < 0:
            return False
        while self.left[node] >= 0 or self.right[node] >= 0:
            left = self.left[node]
            right = self.right[node]
            if right < 0 or (
                left >= 0 and self.priority[left] < self.priority[right]
            ):
                self._rotate(left)
            else:
                self._rotate(right)
        parent = self.parent[node]
        if parent < 0:
            self.root = -1
        elif self.left[parent] == node:
            self.left[parent] = -1
        else:
            self.right[parent] = -1
        self._update_up(parent)
        return True

    erase = discard

    def bisect_left(self, key):
        node = self.root
        result = 0
        while node >= 0:
            left = self.left[node]
            left_size = self.size[left] if left >= 0 else 0
            if self.key[node] < key:
                result += left_size + 1
                node = self.right[node]
            else:
                node = left
        return result

    lower_bound = bisect_left

    def bisect_right(self, key):
        node = self.root
        result = 0
        while node >= 0:
            left = self.left[node]
            left_size = self.size[left] if left >= 0 else 0
            if self.key[node] <= key:
                result += left_size + 1
                node = self.right[node]
            else:
                node = left
        return result

    upper_bound = bisect_right

    def kth(self, index):
        if index < 0 or index >= len(self):
            raise IndexError("kth index out of range")
        node = self.root
        while True:
            left = self.left[node]
            left_size = self.size[left] if left >= 0 else 0
            if index < left_size:
                node = left
            elif index == left_size:
                return self.key[node]
            else:
                index -= left_size + 1
                node = self.right[node]

    def ge(self, key, default=None):
        index = self.bisect_left(key)
        return self.kth(index) if index < len(self) else default

    def gt(self, key, default=None):
        index = self.bisect_right(key)
        return self.kth(index) if index < len(self) else default

    def le(self, key, default=None):
        index = self.bisect_right(key) - 1
        return self.kth(index) if index >= 0 else default

    def lt(self, key, default=None):
        index = self.bisect_left(key) - 1
        return self.kth(index) if index >= 0 else default

    def min(self):
        return self.kth(0)

    def max(self):
        return self.kth(len(self) - 1)

    def __contains__(self, key):
        return self._find(key) >= 0

    def __len__(self):
        root = self.root
        return self.size[root] if root >= 0 else 0

    def __iter__(self):
        stack = []
        node = self.root
        while stack or node >= 0:
            while node >= 0:
                stack.append(node)
                node = self.left[node]
            node = stack.pop()
            yield self.key[node]
            node = self.right[node]


class PointSetRangeFrequency:
    __slots__ = ("values", "positions")

    def __init__(self, values):
        if isinstance(values, int):
            values = [0] * values
        else:
            values = list(values)
        positions = {}
        for index, value in enumerate(values):
            positions.setdefault(value, TreapSet()).add(index)
        self.values = values
        self.positions = positions

    def set(self, index, value):
        old = self.values[index]
        if old == value:
            return
        self.positions[old].discard(index)
        self.positions.setdefault(value, TreapSet()).add(index)
        self.values[index] = value

    def query(self, left, right, value):
        positions = self.positions.get(value)
        if positions is None:
            return 0
        return positions.bisect_left(right) - positions.bisect_left(left)


class RangeSet:
    __slots__ = ("starts", "ends", "covered_length")

    def __init__(self):
        self.starts = TreapSet()
        self.ends = {}
        self.covered_length = 0

    def add(self, left, right):
        if left >= right:
            return 0
        starts = self.starts
        ends = self.ends
        start = starts.le(left)
        if start is not None and ends[start] >= left:
            left = start
            right = max(right, ends[start])
            self.covered_length -= ends.pop(start) - start
            starts.discard(start)
        start = starts.ge(left)
        while start is not None and start <= right:
            right = max(right, ends[start])
            self.covered_length -= ends.pop(start) - start
            starts.discard(start)
            start = starts.ge(left)
        starts.add(left)
        ends[left] = right
        added = right - left
        self.covered_length += added
        return added

    def discard(self, left, right):
        if left >= right:
            return 0
        overlaps = []
        start = self.starts.le(left)
        if start is None or self.ends[start] <= left:
            start = self.starts.ge(left)
        while start is not None and start < right:
            overlaps.append((start, self.ends[start]))
            start = self.starts.gt(start)
        removed = 0
        for start, end in overlaps:
            self.starts.discard(start)
            del self.ends[start]
            overlap = max(0, min(end, right) - max(start, left))
            removed += overlap
            self.covered_length -= end - start
            if start < left:
                self.starts.add(start)
                self.ends[start] = left
                self.covered_length += left - start
            if right < end:
                self.starts.add(right)
                self.ends[right] = end
                self.covered_length += end - right
        return removed

    erase = discard

    def contains(self, value):
        start = self.starts.le(value)
        return start is not None and value < self.ends[start]

    def mex(self, value=0):
        start = self.starts.le(value)
        if start is not None and value < self.ends[start]:
            return self.ends[start]
        return value

    def intervals(self):
        return [(start, self.ends[start]) for start in self.starts]

    def __len__(self):
        return len(self.starts)


class PersistentQueue:
    __slots__ = ("value", "parent", "up", "tail", "length")

    def __init__(self):
        self.value = []
        self.parent = []
        self.up = []
        self.tail = [-1]
        self.length = [0]

    def append(self, value, version=-1):
        version %= len(self.tail)
        parent = self.tail[version]
        node = len(self.value)
        self.value.append(value)
        self.parent.append(parent)
        ancestors = [parent]
        level = 0
        while ancestors[level] >= 0:
            previous = ancestors[level]
            row = self.up[previous]
            if level >= len(row):
                break
            ancestors.append(row[level])
            level += 1
        self.up.append(ancestors)
        self.tail.append(node)
        self.length.append(self.length[version] + 1)
        return len(self.tail) - 1

    push = append

    def popleft(self, version=-1):
        version %= len(self.tail)
        if self.length[version] == 0:
            raise IndexError("pop from empty PersistentQueue")
        self.tail.append(self.tail[version])
        self.length.append(self.length[version] - 1)
        return len(self.tail) - 1

    pop = popleft

    def front(self, version=-1):
        version %= len(self.tail)
        length = self.length[version]
        if length == 0:
            raise IndexError("front from empty PersistentQueue")
        node = self.tail[version]
        steps = length - 1
        bit = 0
        while steps:
            if steps & 1:
                node = self.up[node][bit]
            steps >>= 1
            bit += 1
        return self.value[node]

    def __len__(self):
        return self.length[-1]


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


class TopKSum:
    __slots__ = ("k", "largest", "selected", "rest", "selected_count", "total")

    def __init__(self, k, largest=True):
        self.k = k
        self.largest = largest
        self.selected = ErasableHeap(maximize=not largest)
        self.rest = ErasableHeap(maximize=largest)
        self.selected_count = {}
        self.total = 0

    def _selected_add(self, value):
        self.selected.push(value)
        self.selected_count[value] = self.selected_count.get(value, 0) + 1
        self.total += value

    def _selected_remove(self, value):
        self.selected.erase(value)
        count = self.selected_count[value] - 1
        if count:
            self.selected_count[value] = count
        else:
            del self.selected_count[value]
        self.total -= value

    def _rebalance(self):
        while len(self.selected) > self.k:
            value = self.selected.pop()
            count = self.selected_count[value] - 1
            if count:
                self.selected_count[value] = count
            else:
                del self.selected_count[value]
            self.total -= value
            self.rest.push(value)
        while len(self.selected) < self.k and len(self.rest):
            value = self.rest.pop()
            self._selected_add(value)
        if len(self.selected) and len(self.rest):
            selected_worst = self.selected.top()
            rest_best = self.rest.top()
            wrong = rest_best > selected_worst if self.largest else rest_best < selected_worst
            while wrong:
                self._selected_remove(selected_worst)
                self.rest.erase(rest_best)
                self._selected_add(rest_best)
                self.rest.push(selected_worst)
                if not len(self.selected) or not len(self.rest):
                    break
                selected_worst = self.selected.top()
                rest_best = self.rest.top()
                wrong = rest_best > selected_worst if self.largest else rest_best < selected_worst

    def add(self, value):
        if len(self.selected) < self.k:
            self._selected_add(value)
        else:
            self.rest.push(value)
        self._rebalance()

    def discard(self, value):
        if self.selected_count.get(value, 0):
            self._selected_remove(value)
        else:
            self.rest.erase(value)
        self._rebalance()

    def sum(self):
        return self.total


def sliding_window_minimum(values, width):
    values = list(values)
    if width <= 0 or width > len(values):
        return []
    queue = []
    head = 0
    result = []
    for index, value in enumerate(values):
        while len(queue) > head and values[queue[-1]] >= value:
            queue.pop()
        queue.append(index)
        if queue[head] <= index - width:
            head += 1
        if index + 1 >= width:
            result.append(values[queue[head]])
        if head > 1024 and head * 2 > len(queue):
            queue = queue[head:]
            head = 0
    return result
