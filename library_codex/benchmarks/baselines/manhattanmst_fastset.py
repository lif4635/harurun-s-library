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

def minimum_spanning_forest(n, edges):
    edges = list(edges)
    parent = [-1] * n
    order = sorted(range(len(edges)), key=lambda i: edges[i][2])
    selected = []
    cost = 0
    components = n
    for eid in order:
        (u, v, w) = edges[eid]
        x = u
        while parent[x] >= 0:
            if parent[parent[x]] >= 0:
                parent[x] = parent[parent[x]]
            x = parent[x]
        y = v
        while parent[y] >= 0:
            if parent[parent[y]] >= 0:
                parent[y] = parent[parent[y]]
            y = parent[y]
        if x == y:
            continue
        if parent[x] > parent[y]:
            (x, y) = (y, x)
        parent[x] += parent[y]
        parent[y] = x
        cost += w
        selected.append(eid)
        components -= 1
        if components == 1:
            break
    return (cost, selected, components)

def minimum_spanning_tree(n, edges):
    (cost, selected, components) = minimum_spanning_forest(n, edges)
    if components > 1:
        return None
    return (cost, selected)

def kruskal(n, edges):
    return minimum_spanning_forest(n, edges)[0]

def second_spanning_tree(n, edges, strict=False):
    """MSTと辺集合が異なる最小costの全域木を1本求める。"""
    edges = list(edges)
    result = minimum_spanning_tree(n, edges)
    if result is None or n <= 1:
        return None
    (mst_cost, selected) = result
    selected_set = set(selected)
    tree = [[] for _ in range(n)]
    for edge_id in selected:
        (first, second, weight) = edges[edge_id]
        tree[first].append((second, weight, edge_id))
        tree[second].append((first, weight, edge_id))
    levels = max(1, n.bit_length())
    parent = [[-1] * n for _ in range(levels)]
    largest = [[()] * n for _ in range(levels)]
    depth = [0] * n
    order = [0]
    for vertex in order:
        for (other, weight, edge_id) in tree[vertex]:
            if other == parent[0][vertex]:
                continue
            parent[0][other] = vertex
            largest[0][other] = ((weight, edge_id),)
            depth[other] = depth[vertex] + 1
            order.append(other)

    def merge(first, second):
        by_weight = {}
        for (weight, edge_id) in first + second:
            old = by_weight.get(weight)
            if old is None or edge_id < old:
                by_weight[weight] = edge_id
        return tuple(sorted(((weight, edge_id) for (weight, edge_id) in by_weight.items()), reverse=True)[:2])
    for level in range(1, levels):
        old_parent = parent[level - 1]
        current_parent = parent[level]
        for vertex in range(n):
            middle = old_parent[vertex]
            if middle >= 0:
                current_parent[vertex] = old_parent[middle]
                largest[level][vertex] = merge(largest[level - 1][vertex], largest[level - 1][middle])

    def path_largest(first, second):
        values = ()
        if depth[first] < depth[second]:
            (first, second) = (second, first)
        difference = depth[first] - depth[second]
        level = 0
        while difference:
            if difference & 1:
                values = merge(values, largest[level][first])
                first = parent[level][first]
            difference >>= 1
            level += 1
        if first == second:
            return values
        for level in range(levels - 1, -1, -1):
            if parent[level][first] != parent[level][second]:
                values = merge(values, largest[level][first])
                values = merge(values, largest[level][second])
                first = parent[level][first]
                second = parent[level][second]
        values = merge(values, largest[0][first])
        return merge(values, largest[0][second])
    best = None
    for (edge_id, (first, second, weight)) in enumerate(edges):
        if edge_id in selected_set or first == second:
            continue
        candidates = path_largest(first, second)
        removed = None
        for (old_weight, old_edge_id) in candidates:
            candidate_cost = mst_cost + weight - old_weight
            if not strict or candidate_cost > mst_cost:
                removed = old_edge_id
                candidate = (candidate_cost, edge_id, old_edge_id)
                break
        if removed is not None and (best is None or candidate < best):
            best = candidate
    if best is None:
        return None
    (second_cost, added, removed) = best
    second_edges = [edge_id for edge_id in selected if edge_id != removed]
    second_edges.append(added)
    second_edges.sort()
    return (mst_cost, second_cost, selected, second_edges, added, removed)

def manhattan_mst(points):
    """Return ``(cost, vertex_pairs)`` of a Manhattan MST in O(N log N)."""
    n = len(points)
    if n <= 1:
        return (0, [])
    x = [point[0] for point in points]
    y = [point[1] for point in points]
    order = list(range(n))
    candidates = []
    for outer in range(2):
        for _ in range(2):
            order.sort(key=lambda i: x[i] + y[i])
            keys = sorted(set((-value for value in y)))
            index = {value: i for (i, value) in enumerate(keys)}
            sweep = FastSet(len(keys))
            at_key = [-1] * len(keys)
            for i in order:
                threshold = index[-y[i]]
                key = sweep.next(threshold)
                while key >= 0:
                    j = at_key[key]
                    if x[i] - x[j] < y[i] - y[j]:
                        break
                    candidates.append((abs(x[i] - x[j]) + abs(y[i] - y[j]), i, j))
                    sweep.discard(key)
                    key = sweep.next(threshold)
                at_key[threshold] = i
                sweep.add(threshold)
            (x, y) = (y, x)
        x = [-value for value in x]
    parent = [-1] * n

    def find(v):
        root = v
        while parent[root] >= 0:
            root = parent[root]
        while v != root:
            to = parent[v]
            parent[v] = root
            v = to
        return root
    answer = []
    cost = 0
    for (weight, first, second) in sorted(candidates):
        u = find(first)
        v = find(second)
        if u == v:
            continue
        if parent[u] > parent[v]:
            (u, v) = (v, u)
        parent[u] += parent[v]
        parent[v] = u
        cost += weight
        answer.append((first, second))
        if len(answer) == n - 1:
            break
    return (cost, answer)
import sys
read = sys.stdin.buffer.readline
n = int(read())
points = [tuple(map(int, read().split())) for _ in range(n)]
(cost, pairs) = manhattan_mst(points)
print(cost)
sys.stdout.write('\n'.join((f'{u} {v}' for (u, v) in pairs)) + '\n')
