from array import array

from library_codex.data_structure.RollbackUnionFind import RollbackUnionFind


class OfflineDynamicConnectivity:
    __slots__ = (
        "n", "q", "size", "uf", "events", "query_count", "head",
        "item_a", "item_b", "next_item", "_built",
    )

    EDGE_ADD = 0
    EDGE_REMOVE = 1
    VALUE_ADD = 2
    QUERY_SAME = 3
    QUERY_SIZE = 4
    QUERY_COMPONENTS = 5
    QUERY_VALUE = 6

    def __init__(self, n, q, values=None):
        assert n >= 0 and q >= 0
        self.n = n
        self.q = q
        size = 1
        while size < q:
            size <<= 1
        self.size = size
        self.uf = RollbackUnionFind(n, values)
        self.events = [[] for _ in range(q)]
        self.query_count = 0
        self.head = []
        self.item_a = []
        self.item_b = []
        self.next_item = array("i")
        self._built = False

    def _check_time(self, time):
        assert not self._built
        assert 0 <= time < self.q

    def add_edge(self, time, u, v):
        self._check_time(time)
        assert 0 <= u < self.n and 0 <= v < self.n
        if u > v:
            u, v = v, u
        self.events[time].append((self.EDGE_ADD, u, v))

    link = add_edge

    def remove_edge(self, time, u, v):
        self._check_time(time)
        assert 0 <= u < self.n and 0 <= v < self.n
        if u > v:
            u, v = v, u
        self.events[time].append((self.EDGE_REMOVE, u, v))

    del_edge = remove_edge
    erase_edge = remove_edge
    cut = remove_edge

    def add_value(self, time, vertex, delta):
        self._check_time(time)
        assert self.uf.values is not None
        assert 0 <= vertex < self.n
        self.events[time].append((self.VALUE_ADD, vertex, delta))

    add_vertex_value = add_value

    def query_same(self, time, u, v):
        self._check_time(time)
        assert 0 <= u < self.n and 0 <= v < self.n
        query_id = self.query_count
        self.query_count += 1
        self.events[time].append((self.QUERY_SAME, u, v, query_id))
        return query_id

    add_same_query = query_same

    def query_size(self, time, vertex):
        self._check_time(time)
        assert 0 <= vertex < self.n
        query_id = self.query_count
        self.query_count += 1
        self.events[time].append((self.QUERY_SIZE, vertex, query_id))
        return query_id

    add_size_query = query_size

    def query_components(self, time):
        self._check_time(time)
        query_id = self.query_count
        self.query_count += 1
        self.events[time].append((self.QUERY_COMPONENTS, query_id))
        return query_id

    add_components_query = query_components

    def query_component_value(self, time, vertex):
        self._check_time(time)
        assert self.uf.values is not None
        assert 0 <= vertex < self.n
        query_id = self.query_count
        self.query_count += 1
        self.events[time].append((self.QUERY_VALUE, vertex, query_id))
        return query_id

    query_component_sum = query_component_value
    add_component_value_query = query_component_value

    def _add_interval(self, a, b, left, right):
        if left >= right:
            return
        size = self.size
        head = self.head
        item_a = self.item_a
        item_b = self.item_b
        next_item = self.next_item
        left += size
        right += size
        while left < right:
            if left & 1:
                item_a.append(a)
                item_b.append(b)
                next_item.append(head[left])
                head[left] = len(item_a) - 1
                left += 1
            if right & 1:
                right -= 1
                item_a.append(a)
                item_b.append(b)
                next_item.append(head[right])
                head[right] = len(item_a) - 1
            left >>= 1
            right >>= 1

    def build(self):
        if self._built:
            return self
        self._built = True
        self.head = array("i", [-1]) * (self.size << 1)
        active = {}
        q = self.q
        for time in range(q):
            for event in self.events[time]:
                kind = event[0]
                if kind == self.EDGE_ADD:
                    edge = event[1], event[2]
                    data = active.get(edge)
                    if data is None:
                        active[edge] = [time, 1]
                    else:
                        data[1] += 1
                elif kind == self.EDGE_REMOVE:
                    edge = event[1], event[2]
                    data = active.get(edge)
                    if data is None:
                        raise ValueError("removing an inactive edge")
                    if data[1] == 1:
                        self._add_interval(edge[0], edge[1], data[0], time)
                        del active[edge]
                    else:
                        data[1] -= 1
                elif kind == self.VALUE_ADD:
                    self._add_interval(~event[1], event[2], time, q)
        for edge, data in active.items():
            self._add_interval(edge[0], edge[1], data[0], q)
        return self

    def run(self, query, add=None, remove=None):
        self.build()
        if self.q == 0:
            return
        uf = self.uf
        size = self.size
        q = self.q
        head = self.head
        item_a = self.item_a
        item_b = self.item_b
        next_item = self.next_item
        track_edges = add is not None or remove is not None
        stack = [1]
        states = []
        merged_states = [] if track_edges else None

        while stack:
            node = stack.pop()
            if node < 0:
                if track_edges:
                    merged = merged_states.pop()
                    if remove is not None:
                        for u, v in reversed(merged):
                            remove(u, v)
                uf.rollback(states.pop())
                continue

            states.append(uf.get_state())
            merged = [] if track_edges else None
            item = head[node]
            while item != -1:
                a = item_a[item]
                b = item_b[item]
                if a >= 0:
                    if uf.merge(a, b):
                        if add is not None:
                            add(a, b)
                        if track_edges:
                            merged.append((a, b))
                else:
                    uf.add_value(~a, b)
                item = next_item[item]
            if track_edges:
                merged_states.append(merged)
            stack.append(~node)
            if node < size:
                stack.append((node << 1) | 1)
                stack.append(node << 1)
            else:
                time = node - size
                if time < q:
                    query(time, uf)

    def solve(self):
        answers = [None] * self.query_count
        events = self.events

        def query(time, uf):
            for event in events[time]:
                kind = event[0]
                if kind == self.QUERY_SAME:
                    answers[event[3]] = uf.same(event[1], event[2])
                elif kind == self.QUERY_SIZE:
                    answers[event[2]] = uf.size(event[1])
                elif kind == self.QUERY_COMPONENTS:
                    answers[event[1]] = uf.component_count
                elif kind == self.QUERY_VALUE:
                    answers[event[2]] = uf.component_value(event[1])

        self.run(query)
        return answers
