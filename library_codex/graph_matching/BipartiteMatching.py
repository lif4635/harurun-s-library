class BipartiteMatching:
    __slots__ = (
        "left_size", "right_size", "graph", "match_left", "match_right",
        "matching_size", "_vertices", "_index"
    )

    def __init__(self, left_size, right_size=None):
        self._vertices = self._index = None
        if right_size is None:
            graph = left_size
            n = len(graph)
            color = [-1] * n
            for start in range(n):
                if color[start] != -1:
                    continue
                color[start] = 0
                queue = [start]
                for vertex in queue:
                    for other in graph[vertex]:
                        if not 0 <= other < n:
                            raise ValueError("vertex out of range")
                        if color[other] == -1:
                            color[other] = color[vertex] ^ 1
                            queue.append(other)
                        elif color[other] == color[vertex]:
                            raise ValueError("graph is not bipartite")
            vertices = [v for v in range(n) if color[v] == 0]
            left_size = len(vertices)
            vertices.extend(v for v in range(n) if color[v] == 1)
            right_size = n - left_size
            index = [0] * n
            for i, vertex in enumerate(vertices):
                index[vertex] = i
            self._vertices = vertices
            self._index = index
            self.graph = [
                [index[v] - left_size for v in graph[u]]
                for u in vertices[:left_size]
            ]
        else:
            self.graph = [[] for _ in range(left_size)]
        assert left_size >= 0 and right_size >= 0
        self.left_size = left_size
        self.right_size = right_size
        self.match_left = [-1] * left_size
        self.match_right = [-1] * right_size
        self.matching_size = 0

    def add_edge(self, left, right):
        if self._vertices is not None:
            n = len(self._vertices)
            if not (0 <= left < n and 0 <= right < n):
                raise ValueError("vertex out of range")
            u, v = self._index[left], self._index[right]
            offset = self.left_size
            if (u < offset) == (v < offset):
                graph = [[] for _ in range(n)]
                vertices = self._vertices
                for i, edges in enumerate(self.graph):
                    a = vertices[i]
                    for j in edges:
                        b = vertices[offset + j]
                        graph[a].append(b)
                        graph[b].append(a)
                graph[left].append(right)
                graph[right].append(left)
                rebuilt = type(self)(graph)
                for name in self.__slots__:
                    setattr(self, name, getattr(rebuilt, name))
                return
            if u >= offset:
                u, v = v, u
            left, right = u, v - offset
        assert 0 <= left < self.left_size and 0 <= right < self.right_size
        self.graph[left].append(right)

    def mates(self):
        self.solve()
        offset = self.left_size
        vertices = self._vertices
        if vertices is None:
            return [r + offset if r != -1 else -1 for r in self.match_left] + self.match_right
        result = [-1] * len(vertices)
        for left, right in enumerate(self.match_left):
            if right != -1:
                u, v = vertices[left], vertices[offset + right]
                result[u] = v
                result[v] = u
        return result

    def _vertex_result(self, left, right):
        if self._vertices is None:
            return left, right
        selected = bytearray(len(self._vertices))
        for i in left:
            selected[self._vertices[i]] = 1
        for i in right:
            selected[self._vertices[self.left_size + i]] = 1
        return [v for v, yes in enumerate(selected) if yes]

    def _edge_result(self, edges):
        if self._vertices is None:
            return edges
        vertices = self._vertices
        offset = self.left_size
        return [(vertices[u], vertices[offset + v]) for u, v in edges]

    def _augment(self, start, dist, target_depth, current):
        graph = self.graph
        match_left = self.match_left
        match_right = self.match_right
        stack = [start]
        while stack:
            left = stack[-1]
            edges = graph[left]
            i = current[left]
            descended = False
            while i < len(edges):
                right = edges[i]
                i += 1
                current[left] = i
                mate = match_right[right]
                if mate == -1:
                    if dist[left] + 1 != target_depth:
                        continue
                    next_right = right
                    for u in reversed(stack):
                        old = match_left[u]
                        match_left[u] = next_right
                        match_right[next_right] = u
                        next_right = old
                        dist[u] = -1
                    return True
                if dist[mate] == dist[left] + 1:
                    stack.append(mate)
                    descended = True
                    break
            if descended:
                continue
            dist[left] = -1
            stack.pop()
        return False

    def solve(self):
        left_size = self.left_size
        graph = self.graph
        match_left = self.match_left
        match_right = self.match_right
        while True:
            dist = [-1] * left_size
            que = []
            for left in range(left_size):
                if match_left[left] == -1:
                    dist[left] = 0
                    que.append(left)
            target_depth = -1
            for left in que:
                depth = dist[left] + 1
                if target_depth != -1 and depth >= target_depth:
                    continue
                for right in graph[left]:
                    mate = match_right[right]
                    if mate == -1:
                        target_depth = depth
                    elif dist[mate] == -1:
                        dist[mate] = depth
                        que.append(mate)
            if target_depth == -1:
                break
            current = [0] * left_size
            augmented = 0
            for left in range(left_size):
                if match_left[left] == -1 and dist[left] == 0:
                    augmented += self._augment(
                        left, dist, target_depth, current
                    )
            if augmented == 0:
                break
            self.matching_size += augmented
        return self.matching_size

    def pairs(self):
        self.solve()
        return self._edge_result([(left, right) for left, right in enumerate(self.match_left) if right != -1])

    def _alternating_reachable(self):
        self.solve()
        seen_left = [False] * self.left_size
        seen_right = [False] * self.right_size
        que = []
        for left, right in enumerate(self.match_left):
            if right == -1:
                seen_left[left] = True
                que.append(left)
        for left in que:
            matched = self.match_left[left]
            for right in self.graph[left]:
                if right == matched or seen_right[right]:
                    continue
                seen_right[right] = True
                mate = self.match_right[right]
                if mate != -1 and not seen_left[mate]:
                    seen_left[mate] = True
                    que.append(mate)
        return seen_left, seen_right

    def minimum_vertex_cover(self):
        seen_left, seen_right = self._alternating_reachable()
        return self._vertex_result(
            [i for i, seen in enumerate(seen_left) if not seen],
            [i for i, seen in enumerate(seen_right) if seen],
        )

    def maximum_independent_set(self):
        seen_left, seen_right = self._alternating_reachable()
        return self._vertex_result(
            [i for i, seen in enumerate(seen_left) if seen],
            [i for i, seen in enumerate(seen_right) if not seen],
        )

    def minimum_edge_cover(self):
        self.solve()
        covered_left = [False] * self.left_size
        covered_right = [False] * self.right_size
        result = []
        first_left = [-1] * self.right_size
        for left, edges in enumerate(self.graph):
            if not edges:
                return None
            for right in edges:
                if first_left[right] == -1:
                    first_left[right] = left
        if any(left == -1 for left in first_left):
            return None

        for left, right in enumerate(self.match_left):
            if right != -1:
                result.append((left, right))
                covered_left[left] = True
                covered_right[right] = True
        for left in range(self.left_size):
            if not covered_left[left]:
                right = self.graph[left][0]
                result.append((left, right))
                covered_left[left] = True
                covered_right[right] = True
        for right in range(self.right_size):
            if not covered_right[right]:
                left = first_left[right]
                result.append((left, right))
                covered_left[left] = True
                covered_right[right] = True
        return self._edge_result(result)

    def dulmage_mendelsohn(self):
        self.solve()
        left_size = self.left_size
        n = left_size + self.right_size
        graph = [[] for _ in range(n)]
        reverse = [[] for _ in range(n)]
        for left, edges in enumerate(self.graph):
            matched = self.match_left[left]
            for right in edges:
                rv = left_size + right
                graph[left].append(rv)
                reverse[rv].append(left)
                if right == matched:
                    graph[rv].append(left)
                    reverse[left].append(rv)

        used = [False] * n
        vinf = []
        que = []
        for left, right in enumerate(self.match_left):
            if right == -1:
                used[left] = True
                que.append(left)
        for v in que:
            vinf.append(v)
            for to in graph[v]:
                if not used[to]:
                    used[to] = True
                    que.append(to)

        vzero = []
        que = []
        for right, left in enumerate(self.match_right):
            v = left_size + right
            if left == -1 and not used[v]:
                used[v] = True
                que.append(v)
        for v in que:
            vzero.append(v)
            for to in reverse[v]:
                if not used[to]:
                    used[to] = True
                    que.append(to)

        seen = used.copy()
        order = []
        for start in range(n):
            if seen[start]:
                continue
            seen[start] = True
            stack = [(start, 0)]
            while stack:
                v, i = stack[-1]
                if i == len(graph[v]):
                    order.append(v)
                    stack.pop()
                    continue
                to = graph[v][i]
                stack[-1] = (v, i + 1)
                if not seen[to] and not used[to]:
                    seen[to] = True
                    stack.append((to, 0))

        component = [-1] * n
        groups = []
        for start in reversed(order):
            if component[start] != -1:
                continue
            cid = len(groups)
            group = []
            component[start] = cid
            stack = [start]
            while stack:
                v = stack.pop()
                group.append(v)
                for to in reverse[v]:
                    if not used[to] and component[to] == -1:
                        component[to] = cid
                        stack.append(to)
            groups.append(group)
        groups = [vzero] + groups + [vinf]
        if self._vertices is not None:
            groups = [[self._vertices[v] for v in group] for group in groups]
        return groups

    def _allowed_edge_data(self, components=True):
        self.solve()
        left_size = self.left_size
        n = left_size + self.right_size
        graph = [[] for _ in range(n)]
        reverse = [[] for _ in range(n)]
        for left, edges in enumerate(self.graph):
            matched = self.match_left[left]
            for right in edges:
                right_vertex = left_size + right
                if right == matched:
                    graph[right_vertex].append(left)
                    reverse[left].append(right_vertex)
                else:
                    graph[left].append(right_vertex)
                    reverse[right_vertex].append(left)

        from_free_left = bytearray(n)
        queue = []
        for left, right in enumerate(self.match_left):
            if right == -1:
                from_free_left[left] = 1
                queue.append(left)
        for vertex in queue:
            for other in graph[vertex]:
                if not from_free_left[other]:
                    from_free_left[other] = 1
                    queue.append(other)

        to_free_right = bytearray(n)
        queue = []
        for right, left in enumerate(self.match_right):
            vertex = left_size + right
            if left == -1:
                to_free_right[vertex] = 1
                queue.append(vertex)
        for vertex in queue:
            for other in reverse[vertex]:
                if not to_free_right[other]:
                    to_free_right[other] = 1
                    queue.append(other)

        if not components:
            return from_free_left, to_free_right, None

        used = bytearray(n)
        order = []
        for start in range(n):
            if used[start]:
                continue
            used[start] = 1
            stack = [(start, 0)]
            while stack:
                vertex, index = stack[-1]
                if index == len(graph[vertex]):
                    order.append(vertex)
                    stack.pop()
                    continue
                other = graph[vertex][index]
                stack[-1] = (vertex, index + 1)
                if not used[other]:
                    used[other] = 1
                    stack.append((other, 0))
        component = [-1] * n
        for start in reversed(order):
            if component[start] >= 0:
                continue
            component[start] = start
            stack = [start]
            while stack:
                vertex = stack.pop()
                for other in reverse[vertex]:
                    if component[other] < 0:
                        component[other] = start
                        stack.append(other)
        return from_free_left, to_free_right, component

    def essential_vertices(self):
        from_left, to_right, _ = self._allowed_edge_data(False)
        offset = self.left_size
        result = (
            [right != -1 and not from_left[left]
             for left, right in enumerate(self.match_left)],
            [left != -1 and not to_right[offset + right]
             for right, left in enumerate(self.match_right)],
        )
        if self._vertices is None:
            return result
        flags = [False] * len(self._vertices)
        for i, value in enumerate(result[0] + result[1]):
            flags[self._vertices[i]] = value
        return flags

    def allowed_edges(self):
        """Return edges that occur in at least one maximum matching."""
        from_left, to_right, component = self._allowed_edge_data()
        offset = self.left_size
        result = []
        seen = set()
        for left, edges in enumerate(self.graph):
            for right in edges:
                pair = left, right
                if pair in seen:
                    continue
                seen.add(pair)
                right_vertex = offset + right
                if (
                    self.match_left[left] == right
                    or from_left[left]
                    or to_right[right_vertex]
                    or component[left] == component[right_vertex]
                ):
                    result.append(pair)
        return self._edge_result(result)

    def essential_edges(self):
        """Return edges contained in every maximum matching."""
        from_left, to_right, component = self._allowed_edge_data()
        offset = self.left_size
        result = []
        for left, right in enumerate(self.match_left):
            if right < 0:
                continue
            right_vertex = offset + right
            if not (
                from_left[left]
                or to_right[right_vertex]
                or component[left] == component[right_vertex]
            ):
                result.append((left, right))
        return self._edge_result(result)
