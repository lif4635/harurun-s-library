class FunctionalGraph:
    __slots__ = (
        "n", "to", "depth", "component", "entry", "cycle_pos", "cycles", "up"
    )

    def __init__(self, to):
        n = len(to)
        for v in to:
            assert 0 <= v < n

        indeg = [0] * n
        for v in to:
            indeg[v] += 1
        que = [v for v in range(n) if indeg[v] == 0]
        for u in que:
            v = to[u]
            indeg[v] -= 1
            if indeg[v] == 0:
                que.append(v)

        component = [-1] * n
        entry = [-1] * n
        cycle_pos = [-1] * n
        depth = [0] * n
        cycles = []
        for s in range(n):
            if indeg[s] and component[s] == -1:
                cid = len(cycles)
                cycle = []
                u = s
                while True:
                    component[u] = cid
                    entry[u] = u
                    cycle_pos[u] = len(cycle)
                    cycle.append(u)
                    u = to[u]
                    if u == s:
                        break
                cycles.append(cycle)

        for u in reversed(que):
            v = to[u]
            component[u] = component[v]
            entry[u] = entry[v]
            cycle_pos[u] = cycle_pos[v]
            depth[u] = depth[v] + 1

        h = max(1, (n - 1).bit_length())
        up = [0] * (n * h)
        up[:n] = to
        for level in range(1, h):
            base = level * n
            prev = base - n
            for v in range(n):
                up[base + v] = up[prev + up[prev + v]]

        self.n = n
        self.to = list(to)
        self.depth = depth
        self.component = component
        self.entry = entry
        self.cycle_pos = cycle_pos
        self.cycles = cycles
        self.up = up

    def _jump_tree(self, v, k):
        n = self.n
        up = self.up
        base = 0
        while k:
            if k & 1:
                v = up[base + v]
            base += n
            k >>= 1
        return v

    def move(self, v, k):
        assert k >= 0
        d = self.depth[v]
        if k < d:
            return self._jump_tree(v, k)
        cycle = self.cycles[self.component[v]]
        return cycle[(self.cycle_pos[v] + k - d) % len(cycle)]

    jump = move

    def dist(self, u, v):
        if self.component[u] != self.component[v]:
            return -1
        du = self.depth[u]
        dv = self.depth[v]
        if dv:
            if du < dv:
                return -1
            d = du - dv
            return d if self._jump_tree(u, d) == v else -1
        cycle = self.cycles[self.component[u]]
        return du + (self.cycle_pos[v] - self.cycle_pos[u]) % len(cycle)

    def in_cycle(self, v):
        return self.depth[v] == 0

    def root(self, v):
        return self.entry[v]

    def cycle_size(self, v):
        return len(self.cycles[self.component[v]])

    def reachable_size(self, v):
        return self.depth[v] + len(self.cycles[self.component[v]])

    def get_cycle(self, v):
        return self.cycles[self.component[v]]

    def first_meeting(self, first, second):
        """Return the first time equal-speed walks meet, or ``-1``."""
        if self.component[first] != self.component[second]:
            return -1
        if first == second:
            return 0
        first_depth = self.depth[first]
        second_depth = self.depth[second]
        if first_depth == second_depth:
            if self.entry[first] != self.entry[second]:
                return -1
            elapsed = 0
            first_vertex = first
            second_vertex = second
            maximum = first_depth
            bit = len(self.up) // self.n - 1
            while bit >= 0:
                step = 1 << bit
                if elapsed + step <= maximum:
                    next_first = self.up[bit * self.n + first_vertex]
                    next_second = self.up[bit * self.n + second_vertex]
                    if next_first != next_second:
                        first_vertex = next_first
                        second_vertex = next_second
                        elapsed += step
                bit -= 1
            return elapsed + 1
        cycle = self.cycles[self.component[first]]
        size = len(cycle)
        first_phase = self.cycle_pos[first] - first_depth
        second_phase = self.cycle_pos[second] - second_depth
        if (first_phase - second_phase) % size:
            return -1
        return max(first_depth, second_depth)

    def meeting_vertex(self, first, second):
        """Return ``(time, vertex)`` of the first meeting, or ``None``."""
        time = self.first_meeting(first, second)
        return None if time < 0 else (time, self.move(first, time))
