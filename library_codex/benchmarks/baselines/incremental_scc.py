def scc_ids(graph):
    """成分数と各頂点の成分番号を返す。番号は縮約DAGのトポロジカル順。"""
    n = len(graph)
    order = [-1] * n
    low = [0] * n
    position = [0] * n
    component = [-1] * n
    active = []
    timer = count = 0
    for root in range(n):
        if order[root] >= 0:
            continue
        order[root] = low[root] = timer
        timer += 1
        active.append(root)
        stack = [root]
        while stack:
            vertex = stack[-1]
            index = position[vertex]
            row = graph[vertex]
            if index < len(row):
                position[vertex] = index + 1
                entry = row[index]
                other = entry if isinstance(entry, int) else entry[0]
                if order[other] < 0:
                    order[other] = low[other] = timer
                    timer += 1
                    active.append(other)
                    stack.append(other)
                elif component[other] < 0 and order[other] < low[vertex]:
                    low[vertex] = order[other]
            else:
                stack.pop()
                if low[vertex] == order[vertex]:
                    while True:
                        other = active.pop()
                        component[other] = count
                        if other == vertex:
                            break
                    count += 1
                if stack and low[vertex] < low[stack[-1]]:
                    low[stack[-1]] = low[vertex]
    for vertex in range(n):
        component[vertex] = count - 1 - component[vertex]
    return (count, component)

class SCC:
    __slots__ = ('n', 'graph', 'component', 'groups', 'dag', 'count')

    def __init__(self, graph):
        n = len(graph)
        adjacency = [[] for _ in range(n)]
        reverse = [[] for _ in range(n)]
        for (node, row) in enumerate(graph):
            target = adjacency[node]
            for entry in row:
                other = entry if isinstance(entry, int) else entry[0]
                target.append(other)
                reverse[other].append(node)
        seen = bytearray(n)
        order = []
        for start in range(n):
            if seen[start]:
                continue
            seen[start] = 1
            stack = [(start, 0)]
            while stack:
                (node, index) = stack[-1]
                if index == len(adjacency[node]):
                    order.append(node)
                    stack.pop()
                    continue
                other = adjacency[node][index]
                stack[-1] = (node, index + 1)
                if not seen[other]:
                    seen[other] = 1
                    stack.append((other, 0))
        component = [-1] * n
        groups = []
        for start in reversed(order):
            if component[start] >= 0:
                continue
            component[start] = len(groups)
            group = []
            stack = [start]
            while stack:
                node = stack.pop()
                group.append(node)
                for other in reverse[node]:
                    if component[other] < 0:
                        component[other] = component[start]
                        stack.append(other)
            groups.append(group)
        dag_sets = [set() for _ in groups]
        for (node, row) in enumerate(adjacency):
            first = component[node]
            for other in row:
                second = component[other]
                if first != second:
                    dag_sets[first].add(second)
        self.n = n
        self.graph = adjacency
        self.component = component
        self.groups = groups
        self.dag = [list(row) for row in dag_sets]
        self.count = len(groups)

    def same(self, first, second):
        return self.component[first] == self.component[second]

    def __getitem__(self, vertex):
        return self.component[vertex]

def scc(graph):
    solver = SCC(graph)
    return (solver.component, solver.groups)
'Advanced edge-connectivity and incremental SCC algorithms.'

class ThreeEdgeConnectedComponents:
    """Partition an undirected multigraph into 2/3-edge-connected blocks.

    The implementation is the linear-time path-absorption algorithm, expressed
    as one iterative DFS.  Self-loops do not affect the partition and parallel
    edges are handled by edge ID.
    """
    __slots__ = ('n', 'edges', 'component', 'groups', 'component2', 'groups2', 'count', 'count2')

    def __init__(self, n, edges):
        self.n = n
        self.edges = list(edges)
        incident = [[] for _ in range(n)]
        for (edge_id, (u, v)) in enumerate(self.edges):
            incident[u].append(edge_id)
            if v != u:
                incident[v].append(edge_id)
        parent_edge = [-1] * n
        dfs_in = [-1] * n
        dfs_out = [0] * n
        low = [n] * n
        degree = [0] * n
        path = [-1] * n
        color2 = [-1] * n
        color3 = [-1] * n
        dfs_id = 0

        def other(edge_id, vertex):
            (u, v) = self.edges[edge_id]
            return u ^ v ^ vertex

        def absorb(vertex, border_left, border_right):
            while path[vertex] >= 0:
                child = path[vertex]
                if border_left < dfs_in[child] or dfs_out[child] < border_right:
                    break
                degree[vertex] += degree[child] - 2
                degree[child] = 0
                path[vertex] = path[child]
                color3[child] = vertex
        for start in range(n):
            if dfs_in[start] != -1:
                continue
            dfs_in[start] = dfs_id
            dfs_id += 1
            vertex = start
            while True:
                if dfs_out[vertex] >= len(incident[vertex]):
                    dfs_out[vertex] = dfs_id
                    edge_to_parent = parent_edge[vertex]
                    if edge_to_parent < 0:
                        break
                    child = vertex
                    vertex = other(edge_to_parent, vertex)
                    if dfs_in[vertex] >= low[child]:
                        color2[child] = vertex
                        low_child = low[child]
                        tail = child
                        if degree[tail] == 2:
                            degree[tail] -= 2
                            tail = path[tail]
                        if low[vertex] <= low_child:
                            saved = path[vertex]
                            path[vertex] = tail
                            absorb(vertex, n, -1)
                            path[vertex] = saved
                        else:
                            low[vertex] = low_child
                            absorb(vertex, n, -1)
                            path[vertex] = tail
                    else:
                        degree[vertex] -= 1
                        degree[child] -= 1
                    continue
                edge_id = incident[vertex][dfs_out[vertex]]
                dfs_out[vertex] += 1
                to = other(edge_id, vertex)
                if to == vertex:
                    continue
                degree[vertex] += 1
                if edge_id == parent_edge[vertex]:
                    continue
                if dfs_in[to] == -1:
                    dfs_in[to] = dfs_id
                    dfs_id += 1
                    parent_edge[to] = edge_id
                    vertex = to
                    continue
                if dfs_in[to] < dfs_in[vertex]:
                    if dfs_in[to] < low[vertex]:
                        low[vertex] = dfs_in[to]
                        absorb(vertex, n, -1)
                else:
                    absorb(vertex, dfs_in[to], dfs_out[to])
                    degree[vertex] -= 2
        inverse_order = [0] * n
        for vertex in range(n):
            inverse_order[dfs_in[vertex]] = vertex

        def assign(pointer):
            count = 0
            for vertex in inverse_order:
                if pointer[vertex] == -1:
                    pointer[vertex] = count
                    count += 1
                else:
                    pointer[vertex] = pointer[pointer[vertex]]
            groups = [[] for _ in range(count)]
            for (vertex, component) in enumerate(pointer):
                groups[component].append(vertex)
            return (count, groups)
        (self.count2, self.groups2) = assign(color2)
        (self.count, self.groups) = assign(color3)
        self.component2 = color2
        self.component = color3

    def __getitem__(self, vertex):
        return self.component[vertex]

class _graph_connectivity_advanced_connectivity_DSU:
    __slots__ = ('parent',)

    def __init__(self, n):
        self.parent = [-1] * n

    def find(self, vertex):
        root = vertex
        while self.parent[root] >= 0:
            root = self.parent[root]
        while vertex != root:
            nxt = self.parent[vertex]
            self.parent[vertex] = root
            vertex = nxt
        return root

    def unite(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return False
        if self.parent[first] > self.parent[second]:
            (first, second) = (second, first)
        self.parent[first] += self.parent[second]
        self.parent[second] = first
        return True

def incremental_scc_offline(n, edges):
    """Return SCC-union edge IDs for every directed edge-insertion time.

    ``result[t]`` is a list of original edge IDs.  If a DSU unions the original
    endpoints of those edges after insertion t, its components exactly equal
    the SCC partition of the prefix ``edges[:t+1]``.  Complexity is
    O((N+M) log M) SCC work.
    """
    edges = list(edges)
    m = len(edges)
    result = [[] for _ in range(m)]
    if not m:
        return result
    original_u = [edge[0] for edge in edges]
    original_v = [edge[1] for edge in edges]
    work_u = original_u[:]
    work_v = original_v[:]
    full_graph = [[] for _ in range(n)]
    for (u, v) in edges:
        full_graph[u].append(v)
    final_component = SCC(full_graph).component
    active = [edge_id for (edge_id, (u, v)) in enumerate(edges) if final_component[u] == final_component[v]]
    tasks = [(n, 0, active)]
    while tasks:
        (vertex_count, split, edge_ids) = tasks.pop()
        local_m = len(edge_ids)
        if split == local_m:
            continue
        if split + 1 == local_m:
            dsu = _graph_connectivity_advanced_connectivity_DSU(vertex_count)
            bucket = result[edge_ids[split]]
            for edge_id in edge_ids:
                u = work_u[edge_id]
                v = work_v[edge_id]
                if dsu.unite(u, v):
                    bucket.append(edge_id)
            continue
        mapping = {}
        next_vertex = 0
        for edge_id in edge_ids:
            u = work_u[edge_id]
            v = work_v[edge_id]
            if u not in mapping:
                mapping[u] = next_vertex
                next_vertex += 1
            if v not in mapping:
                mapping[v] = next_vertex
                next_vertex += 1
            work_u[edge_id] = mapping[u]
            work_v[edge_id] = mapping[v]
        vertex_count = next_vertex
        middle = split + local_m >> 1
        graph = [[] for _ in range(vertex_count)]
        for position in range(middle):
            edge_id = edge_ids[position]
            graph[work_u[edge_id]].append(work_v[edge_id])
        component = SCC(graph).component
        left = []
        right = []
        for position in range(split):
            edge_id = edge_ids[position]
            (left if component[work_u[edge_id]] == component[work_v[edge_id]] else right).append(edge_id)
        left_split = len(left)
        for position in range(split, middle):
            edge_id = edge_ids[position]
            (left if component[work_u[edge_id]] == component[work_v[edge_id]] else right).append(edge_id)
        right_split = len(right)
        for position in range(middle, local_m):
            edge_id = edge_ids[position]
            if component[work_u[edge_id]] != component[work_v[edge_id]]:
                right.append(edge_id)
        for edge_id in right:
            work_u[edge_id] = component[work_u[edge_id]]
            work_v[edge_id] = component[work_v[edge_id]]
        component_count = max(component, default=-1) + 1
        tasks.append((component_count, right_split, right))
        tasks.append((vertex_count, left_split, left))
    return result
IncrementalSccOffline = incremental_scc_offline
'要素の併合・連結判定・成分サイズを扱う基本Union-Find。'

class UnionFind:
    __slots__ = ('n', 'parent', 'component_count')

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
            (first, second) = (second, first)
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

    def __str__(self):
        return str(self.groups())

    def __repr__(self):
        return 'UnionFind(%r)' % self.groups()
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, m) = map(int, read().split())
    values = list(map(int, read().split()))
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    events = incremental_scc_offline(n, edges)
    uf = UnionFind(n)
    total = 0
    mod = 998244353
    answer = []
    for event in events:
        for index in event:
            (u, v) = edges[index]
            (u, v) = (uf.find(u), uf.find(v))
            if u != v:
                total = (total + values[u] * values[v]) % mod
                combined = (values[u] + values[v]) % mod
                values[uf.merge(u, v)] = combined
        answer.append(str(total))
    sys.stdout.write('\n'.join(answer))
if __name__ == '__main__':
    main()
