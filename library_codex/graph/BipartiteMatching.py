class BipartiteMatching:
    __slots__ = (
        "left_size", "right_size", "graph", "match_left", "match_right",
        "matching_size"
    )

    def __init__(self, left_size, right_size):
        assert left_size >= 0 and right_size >= 0
        self.left_size = left_size
        self.right_size = right_size
        self.graph = [[] for _ in range(left_size)]
        self.match_left = [-1] * left_size
        self.match_right = [-1] * right_size
        self.matching_size = 0

    def add_edge(self, left, right):
        assert 0 <= left < self.left_size and 0 <= right < self.right_size
        self.graph[left].append(right)

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

    flow = solve

    def pairs(self):
        self.solve()
        return [(left, right) for left, right in enumerate(self.match_left) if right != -1]

    maximum_matching = pairs

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
        return (
            [i for i, seen in enumerate(seen_left) if not seen],
            [i for i, seen in enumerate(seen_right) if seen],
        )

    def maximum_independent_set(self):
        seen_left, seen_right = self._alternating_reachable()
        return (
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
        return result

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
        return [vzero] + groups + [vinf]

    dm_decomposition = dulmage_mendelsohn


def bipartite_matching(graph, right_size):
    matcher = BipartiteMatching(len(graph), right_size)
    for left, edges in enumerate(graph):
        for right in edges:
            matcher.add_edge(left, right)
    matcher.solve()
    return matcher.match_left


def maximum_bipartite_matching(left_size, right_size, edges):
    matcher = BipartiteMatching(left_size, right_size)
    for left, right in edges:
        matcher.add_edge(left, right)
    return matcher.maximum_matching()
