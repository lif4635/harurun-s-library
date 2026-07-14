class UnionFind:
    __slots__ = ("n", "parent", "component_count")

    def __init__(self, size):
        self.n = size
        self.parent = [-1] * size
        self.component_count = size

    def find(self, node):
        parent = self.parent
        root = node
        while parent[root] >= 0:
            root = parent[root]
        while node != root:
            next_node = parent[node]
            parent[node] = root
            node = next_node
        return root

    leader = find
    root = find

    def merge(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return first
        parent = self.parent
        if parent[first] > parent[second]:
            first, second = second, first
        parent[first] += parent[second]
        parent[second] = first
        self.component_count -= 1
        return first

    unite = merge
    union = merge

    def same(self, first, second):
        return self.find(first) == self.find(second)

    def size(self, node):
        return -self.parent[self.find(node)]

    def groups(self):
        result = [[] for _ in range(self.n)]
        for node in range(self.n):
            result[self.find(node)].append(node)
        return [group for group in result if group]


class DynamicUnionFind:
    __slots__ = ("parent", "component_size", "component_count")

    def __init__(self):
        self.parent = {}
        self.component_size = {}
        self.component_count = 0

    def add(self, node):
        if node in self.parent:
            return False
        self.parent[node] = node
        self.component_size[node] = 1
        self.component_count += 1
        return True

    def find(self, node):
        parent = self.parent
        if node not in parent:
            parent[node] = node
            self.component_size[node] = 1
            self.component_count += 1
            return node
        root = node
        while parent[root] != root:
            root = parent[root]
        while node != root:
            next_node = parent[node]
            parent[node] = root
            node = next_node
        return root

    leader = find

    def merge(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return first
        parent = self.parent
        size = self.component_size
        if size[first] < size[second]:
            first, second = second, first
        parent[second] = first
        size[first] += size.pop(second)
        self.component_count -= 1
        return first

    unite = merge

    def same(self, first, second):
        return self.find(first) == self.find(second)

    def size(self, node):
        return self.component_size[self.find(node)]


class WeightedUnionFind:
    __slots__ = ("n", "parent", "potential", "component_count")

    def __init__(self, size):
        self.n = size
        self.parent = [-1] * size
        self.potential = [0] * size
        self.component_count = size

    def find(self, node):
        parent = self.parent
        potential = self.potential
        root = node
        total = 0
        while parent[root] >= 0:
            total += potential[root]
            root = parent[root]
        prefix = 0
        while node != root:
            next_node = parent[node]
            weight = potential[node]
            parent[node] = root
            potential[node] = total - prefix
            prefix += weight
            node = next_node
        return root

    leader = find

    def weight(self, node):
        self.find(node)
        return self.potential[node]

    def merge(self, first, second, difference):
        difference += self.weight(first) - self.weight(second)
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return difference == 0
        parent = self.parent
        if parent[first] > parent[second]:
            first, second = second, first
            difference = -difference
        parent[first] += parent[second]
        parent[second] = first
        self.potential[second] = difference
        self.component_count -= 1
        return True

    unite = merge

    def same(self, first, second):
        return self.find(first) == self.find(second)

    def diff(self, first, second):
        if self.find(first) != self.find(second):
            return None
        return self.weight(second) - self.weight(first)

    difference = diff

    def size(self, node):
        return -self.parent[self.find(node)]


class EnumerateUnionFind(UnionFind):
    __slots__ = ("next",)

    def __init__(self, size):
        super().__init__(size)
        self.next = list(range(size))

    def merge(self, first, second):
        first_root = self.find(first)
        second_root = self.find(second)
        if first_root == second_root:
            return first_root
        self.next[first], self.next[second] = self.next[second], self.next[first]
        return super().merge(first_root, second_root)

    unite = merge

    def members(self, node):
        start = node
        result = [start]
        node = self.next[start]
        while node != start:
            result.append(node)
            node = self.next[node]
        return result


class MonoidUnionFind(UnionFind):
    __slots__ = ("value", "op", "edge_count")

    def __init__(self, values, op):
        values = list(values)
        super().__init__(len(values))
        self.value = values
        self.op = op
        self.edge_count = [0] * len(values)

    def merge(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            self.edge_count[first] += 1
            return first
        parent = self.parent
        if parent[first] > parent[second]:
            first, second = second, first
        parent[first] += parent[second]
        parent[second] = first
        self.value[first] = self.op(self.value[first], self.value[second])
        self.edge_count[first] += self.edge_count[second] + 1
        self.component_count -= 1
        return first

    unite = merge

    def get(self, node):
        return self.value[self.find(node)]

    def set(self, node, value):
        self.value[self.find(node)] = value

    def edges(self, node):
        return self.edge_count[self.find(node)]

    def has_cycle(self, node):
        root = self.find(node)
        return self.edge_count[root] >= -self.parent[root]


class PartialPersistentUnionFind:
    __slots__ = (
        "n", "parent", "parent_time", "size_time", "size_value", "last_time"
    )

    def __init__(self, size):
        self.n = size
        self.parent = [-1] * size
        self.parent_time = [1 << 60] * size
        self.size_time = [[-1] for _ in range(size)]
        self.size_value = [[1] for _ in range(size)]
        self.last_time = -1

    def find(self, node, time=None):
        if time is None:
            time = self.last_time
        parent = self.parent
        parent_time = self.parent_time
        while parent[node] >= 0 and parent_time[node] <= time:
            node = parent[node]
        return node

    leader = find

    def merge(self, first, second, time=None):
        if time is None:
            time = self.last_time + 1
        if time < self.last_time:
            raise ValueError("time must be nondecreasing")
        self.last_time = time
        first = self.find(first, time)
        second = self.find(second, time)
        if first == second:
            return False
        parent = self.parent
        if parent[first] > parent[second]:
            first, second = second, first
        parent[first] += parent[second]
        parent[second] = first
        self.parent_time[second] = time
        self.size_time[first].append(time)
        self.size_value[first].append(-parent[first])
        return True

    unite = merge

    def same(self, first, second, time=None):
        return self.find(first, time) == self.find(second, time)

    def size(self, node, time=None):
        from bisect import bisect_right

        if time is None:
            time = self.last_time
        root = self.find(node, time)
        index = bisect_right(self.size_time[root], time) - 1
        return self.size_value[root][index]

    def when_unite(self, first, second):
        if not self.same(first, second):
            return -1
        low = -1
        high = self.last_time
        while low + 1 < high:
            middle = (low + high) >> 1
            if self.same(first, second, middle):
                high = middle
            else:
                low = middle
        return high

    def size_ge(self, node, target):
        if target <= 1:
            return -1
        if self.size(node) < target:
            return -1
        low = -1
        high = self.last_time
        while low + 1 < high:
            middle = (low + high) >> 1
            if self.size(node, middle) >= target:
                high = middle
            else:
                low = middle
        return high


class RangeParallelUnionFind:
    __slots__ = ("n", "level")

    def __init__(self, size):
        self.n = size
        self.level = [UnionFind(size) for _ in range(max(1, size.bit_length()))]

    def merge(self, first, second, length=1, callback=None):
        if length <= 0:
            return
        if first < 0 or second < 0 or first + length > self.n or second + length > self.n:
            raise IndexError("range is out of bounds")
        if length == 1:
            stack = [(first, second, 0)]
        else:
            level = (length - 1).bit_length() - 1
            width = 1 << level
            stack = [
                (first, second, level),
                (first + length - width, second + length - width, level),
            ]
        while stack:
            left, right, level = stack.pop()
            union_find = self.level[level]
            left_root = union_find.find(left)
            right_root = union_find.find(right)
            if left_root == right_root:
                continue
            new_root = union_find.merge(left_root, right_root)
            if level == 0:
                if callback is not None:
                    old_root = right_root if new_root == left_root else left_root
                    callback(new_root, old_root)
                continue
            half = 1 << (level - 1)
            stack.append((left + half, right + half, level - 1))
            stack.append((left, right, level - 1))

    unite = merge

    def find(self, node):
        return self.level[0].find(node)

    def same(self, first, second):
        return self.level[0].same(first, second)

    def size(self, node):
        return self.level[0].size(node)


class ContiguousUnionFind(UnionFind):
    __slots__ = ("left", "right")

    def __init__(self, size):
        super().__init__(size)
        self.left = list(range(size))
        self.right = [index + 1 for index in range(size)]

    def merge(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return first
        left = min(self.left[first], self.left[second])
        right = max(self.right[first], self.right[second])
        root = super().merge(first, second)
        self.left[root] = left
        self.right[root] = right
        return root

    unite = merge

    def range_merge(self, left, right):
        left = max(left, 0)
        right = min(right, self.n)
        if left >= right:
            return
        root = self.find(left)
        while self.right[root] < right:
            next_root = self.find(self.right[root])
            root = self.merge(root, next_root)

    range_unite = range_merge

    def interval(self, node):
        root = self.find(node)
        return self.left[root], self.right[root]
