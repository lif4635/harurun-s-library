"""二部多重グラフの辺を、同じ頂点に接する辺が異色になるよう最小色数で彩色する。"""

def _graph_matching_bipartite_edge_coloring_pack_vertices(degrees, limit):
    group = [-1] * len(degrees)
    totals = []
    for (vertex, degree) in enumerate(degrees):
        if not degree:
            continue
        if not totals or totals[-1] + degree > limit:
            totals.append(0)
        group[vertex] = len(totals) - 1
        totals[-1] += degree
    return (group, totals)

def _graph_matching_bipartite_edge_coloring_perfect_matching(size, ids, left, right):
    graph = [[] for _ in range(size)]
    for eid in ids:
        graph[left[eid]].append(eid)
    match_left = [-1] * size
    match_right = [-1] * size
    remaining = size
    for u in range(size):
        for eid in graph[u]:
            v = right[eid]
            if match_right[v] < 0:
                match_left[u] = eid
                match_right[v] = u
                remaining -= 1
                break
    while remaining:
        distance = [-1] * size
        queue = []
        for u in range(size):
            if match_left[u] < 0:
                distance[u] = 0
                queue.append(u)
        shortest = size + 1
        for u in queue:
            if distance[u] >= shortest:
                continue
            for eid in graph[u]:
                v = match_right[right[eid]]
                if v < 0:
                    shortest = distance[u] + 1
                elif distance[v] < 0:
                    distance[v] = distance[u] + 1
                    queue.append(v)
        if shortest == size + 1:
            raise ArithmeticError('regular graph has no perfect matching')
        current = [0] * size
        for root in queue:
            if match_left[root] >= 0:
                continue
            stack = [root]
            path = []
            found = -1
            while stack:
                u = stack[-1]
                choices = graph[u]
                while current[u] < len(choices):
                    eid = choices[current[u]]
                    current[u] += 1
                    v = match_right[right[eid]]
                    if v < 0:
                        if distance[u] + 1 == shortest:
                            found = eid
                            break
                    elif distance[v] == distance[u] + 1:
                        stack.append(v)
                        path.append(eid)
                        break
                else:
                    distance[u] = -1
                    stack.pop()
                    if path:
                        path.pop()
                    continue
                if found >= 0:
                    path.append(found)
                    for (u, eid) in zip(stack, path):
                        match_left[u] = eid
                        match_right[right[eid]] = u
                    remaining -= 1
                    break
    return match_left

def _graph_matching_bipartite_edge_coloring_split_edges(size, ids, left, right):
    graph = [[] for _ in range(2 * size)]
    for (i, eid) in enumerate(ids):
        graph[left[eid]].append(i)
        graph[size + right[eid]].append(i)
    used = bytearray(len(ids))
    halves = ([], [])
    for root in range(size):
        vertex = root
        parity = 0
        while graph[vertex]:
            i = graph[vertex].pop()
            if used[i]:
                continue
            used[i] = 1
            eid = ids[i]
            halves[parity].append(eid)
            parity ^= 1
            vertex = left[eid] + size + right[eid] - vertex
    return halves

def bipartite_edge_coloring(left_size, right_size, edges):
    """入力辺と同じ順に最小色数の色番号listを返す。多重辺も個別に彩色する。"""
    if left_size < 0 or right_size < 0:
        raise ValueError('part sizes must be nonnegative')
    edges = list(edges)
    degree_left = [0] * left_size
    degree_right = [0] * right_size
    for (u, v) in edges:
        if not 0 <= u < left_size or not 0 <= v < right_size:
            raise IndexError('edge endpoint is out of range')
        degree_left[u] += 1
        degree_right[v] += 1
    delta = max(max(degree_left, default=0), max(degree_right, default=0))
    if not delta:
        return []
    (left_group, degree_left) = _graph_matching_bipartite_edge_coloring_pack_vertices(degree_left, delta)
    (right_group, degree_right) = _graph_matching_bipartite_edge_coloring_pack_vertices(degree_right, delta)
    size = max(len(degree_left), len(degree_right))
    if size == 1:
        return list(range(len(edges)))
    degree_left.extend([0] * (size - len(degree_left)))
    degree_right.extend([0] * (size - len(degree_right)))
    left = [left_group[u] for (u, _) in edges]
    right = [right_group[v] for (_, v) in edges]
    u = v = 0
    while u < size and v < size:
        if degree_left[u] == delta:
            u += 1
        elif degree_right[v] == delta:
            v += 1
        else:
            amount = min(delta - degree_left[u], delta - degree_right[v])
            left.extend([u] * amount)
            right.extend([v] * amount)
            degree_left[u] += amount
            degree_right[v] += amount
    colors = [-1] * len(edges)
    chosen = bytearray(len(left))
    stack = [(delta, list(range(len(left))), 0)]
    while stack:
        (degree, ids, offset) = stack.pop()
        if degree == 1:
            for eid in ids:
                if eid < len(colors):
                    colors[eid] = offset
        elif degree & 1:
            matching = _graph_matching_bipartite_edge_coloring_perfect_matching(size, ids, left, right)
            for eid in matching:
                chosen[eid] = 1
                if eid < len(colors):
                    colors[eid] = offset
            rest = [eid for eid in ids if not chosen[eid]]
            stack.append((degree - 1, rest, offset + 1))
        else:
            (first, second) = _graph_matching_bipartite_edge_coloring_split_edges(size, ids, left, right)
            degree //= 2
            stack.append((degree, second, offset + degree))
            stack.append((degree, first, offset))
    return colors
'Recognition and coloring algorithms for undirected graphs.'

class ChordalGraphRecognizer:
    """Maximum-cardinality-search chordal graph recognizer."""

    def __init__(self, graph):
        self.n = len(graph)
        self.adjacency = [list(set(neighbors) - {v}) for (v, neighbors) in enumerate(graph)]
        self._mcs = None
        self._peo = None
        self._chordal = None
        self._violation = None
        self._cycle = None

    def mcs_order(self):
        if self._mcs is not None:
            return self._mcs[:]
        n = self.n
        score = [0] * n
        previous = list(range(-1, n - 1))
        following = list(range(1, n)) + [-1] if n else []
        buckets = [-1] * (max(map(len, self.adjacency), default=0) + 1)
        buckets[0] = 0 if n else -1
        maximum = 0
        order = []
        for _ in range(n):
            while maximum and buckets[maximum] < 0:
                maximum -= 1
            v = buckets[maximum]
            after = following[v]
            buckets[maximum] = after
            if after >= 0:
                previous[after] = -1
            score[v] = -1
            order.append(v)
            for to in self.adjacency[v]:
                old = score[to]
                if old >= 0:
                    (before, after) = (previous[to], following[to])
                    if before < 0:
                        buckets[old] = after
                    else:
                        following[before] = after
                    if after >= 0:
                        previous[after] = before
                    old += 1
                    score[to] = old
                    after = buckets[old]
                    previous[to] = -1
                    following[to] = after
                    if after >= 0:
                        previous[after] = to
                    buckets[old] = to
                    if old > maximum:
                        maximum = old
        self._mcs = order
        return order[:]

    def is_chordal(self):
        if self._chordal is not None:
            return self._chordal
        peo = list(reversed(self.mcs_order()))
        position = [0] * self.n
        for (i, v) in enumerate(peo):
            position[v] = i
        children = [-1] * self.n
        following = [-1] * self.n
        for v in peo:
            best = self.n
            parent = -1
            for to in self.adjacency[v]:
                if position[v] < position[to] < best:
                    best = position[to]
                    parent = to
            if parent >= 0:
                following[v] = children[parent]
                children[parent] = v
        marked = [-1] * self.n
        first_bad = self.n
        violation = None
        for parent in range(self.n):
            if children[parent] < 0:
                continue
            for to in self.adjacency[parent]:
                marked[to] = parent
            v = children[parent]
            while v >= 0:
                if position[v] < first_bad:
                    for to in self.adjacency[v]:
                        if position[to] > position[v] and to != parent and (marked[to] != parent):
                            violation = (v, parent, to)
                            first_bad = position[v]
                            break
                v = following[v]
        self._peo = peo
        self._violation = violation
        self._chordal = violation is None
        return self._chordal

    def perfect_elimination_order(self):
        return self._peo[:] if self.is_chordal() else []

    def induced_cycle(self):
        """Return a chordless cycle witness, or [] for a chordal graph."""
        if self._cycle is not None:
            return self._cycle[:]
        if self.is_chordal():
            self._cycle = []
            return []
        (v, source, target) = self._violation
        position = [0] * self.n
        for (i, vertex) in enumerate(self._peo):
            position[vertex] = i
        forbidden = set(self.adjacency[v]) - {source, target}
        parent = [-1] * self.n
        parent[source] = source
        queue = [source]
        i = 0
        while i < len(queue):
            x = queue[i]
            i += 1
            if x == target:
                break
            for to in self.adjacency[x]:
                if parent[to] == -1 and to != v and (to not in forbidden) and (position[to] > position[v]):
                    parent[to] = x
                    queue.append(to)
        if parent[target] == -1:
            self._cycle = []
            return []
        path = []
        x = target
        while x != source:
            path.append(x)
            x = parent[x]
        path.append(source)
        path.reverse()
        self._cycle = [v] + path
        return self._cycle[:]

def _graph_enumeration_graph_properties_bipartite_edge_coloring(left_size, right_size, edges):
    """(最小色数, 入力辺と同じ順の色番号list)を返す。"""
    colors = bipartite_edge_coloring(left_size, right_size, edges)
    return (max(colors, default=-1) + 1, colors)
import sys
read = sys.stdin.buffer.readline
(n, m) = map(int, read().split())
graph = [[] for _ in range(n)]
for _ in range(m):
    (u, v) = map(int, read().split())
    graph[u].append(v)
    graph[v].append(u)
recognizer = ChordalGraphRecognizer(graph)
del graph
if recognizer.is_chordal():
    print('YES')
    print(*recognizer.perfect_elimination_order())
else:
    cycle = recognizer.induced_cycle()
    print('NO')
    print(len(cycle))
    print(*cycle)
