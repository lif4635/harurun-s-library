"""Graph orderings and replacement shortest paths."""

from heapq import heappop, heappush


class _Ratio:
    __slots__ = ("zero", "one")

    def __init__(self, zero, one):
        self.zero = zero
        self.one = one

    def __lt__(self, other):
        # heapq should pop the maximum zero/one ratio.  Cross products avoid
        # floating-point precision loss; zero denominators behave as infinity.
        self_empty = self.zero == 0 and self.one == 0
        other_empty = other.zero == 0 and other.one == 0
        if self_empty or other_empty:
            return self_empty and not other_empty
        if self.one == 0 or other.one == 0:
            return self.one == 0 and other.one != 0
        return self.zero * other.one > other.zero * self.one


def optimal_tree_topological_order(parent, weight0, weight1, root=0):
    """Optimal parent-before-child order for a pairwise inversion objective.

    Minimizes ``sum(weight1[order[i]] * weight0[order[j]], i < j)``.
    ``parent`` must describe one rooted tree and weights must be nonnegative.
    Returns ``(minimum_value, order)`` in O(N log N).
    """
    n = len(parent)
    if len(weight0) != n or len(weight1) != n:
        raise ValueError("array lengths differ")
    if n == 0:
        return 0, []
    uf = list(range(n))
    head = list(range(n))
    tail = list(range(n))
    nxt = [-1] * n
    zero = list(weight0)
    one = list(weight1)
    value = [0] * n
    version = [0] * n

    def find(v):
        root_v = v
        while uf[root_v] != root_v:
            root_v = uf[root_v]
        while uf[v] != v:
            to = uf[v]
            uf[v] = root_v
            v = to
        return root_v

    heap = []
    serial = 0
    for v in range(n):
        if v != root:
            heappush(heap, (_Ratio(zero[v], one[v]), serial, v, 0))
            serial += 1
    while heap:
        _, _, component, stamp = heappop(heap)
        if find(component) != component or version[component] != stamp:
            continue
        ancestor = parent[head[component]]
        if ancestor < 0:
            continue
        ancestor = find(ancestor)
        if ancestor == component:
            continue
        # Parent component followed by child component.
        nxt[tail[ancestor]] = head[component]
        tail[ancestor] = tail[component]
        new_zero = zero[ancestor] + zero[component]
        new_one = one[ancestor] + one[component]
        new_value = (value[ancestor] + value[component]
                     + one[ancestor] * zero[component])
        uf[component] = ancestor
        zero[ancestor] = new_zero
        one[ancestor] = new_one
        value[ancestor] = new_value
        version[ancestor] += 1
        if ancestor != find(root):
            heappush(heap, (
                _Ratio(new_zero, new_one), serial, ancestor,
                version[ancestor]
            ))
            serial += 1
    component = find(root)
    order = []
    vertex = head[component]
    while vertex != -1:
        order.append(vertex)
        vertex = nxt[vertex]
    if len(order) != n:
        raise ValueError("parent does not describe one tree rooted at root")
    return value[component], order


def bipolar_orientation(graph, source, target):
    """Return st-number positions, or ``None`` when construction fails.

    A successful order starts with source, ends with target, and every other
    vertex has both an earlier and a later neighbor.  DFS, lowlink, and linked
    list insertion are all iterative.
    """
    n = len(graph)
    if source == target or not 0 <= source < n or not 0 <= target < n:
        return None
    order_number = [-1] * n
    low = list(range(n))
    parent = [-1] * n
    preorder = []
    order_number[source] = 0
    order_number[target] = 1
    preorder.append(target)
    clock = 2
    stack = [(target, 0)]
    while stack:
        vertex, index = stack[-1]
        if index == len(graph[vertex]):
            stack.pop()
            par = parent[vertex]
            if par >= 0 and order_number[low[vertex]] < order_number[low[par]]:
                low[par] = low[vertex]
            continue
        to = graph[vertex][index]
        stack[-1] = (vertex, index + 1)
        if order_number[to] == -1:
            parent[to] = vertex
            order_number[to] = clock
            clock += 1
            preorder.append(to)
            stack.append((to, 0))
        elif to != parent[vertex] and order_number[to] < order_number[low[vertex]]:
            low[vertex] = to
    if len(preorder) != n - 1:
        return None

    previous = [-1] * n
    following = [-1] * n
    following[source] = target
    previous[target] = source
    sign = [False] * n
    for vertex in preorder[1:]:
        par = parent[vertex]
        if not sign[low[vertex]]:
            before = previous[par]
            previous[vertex] = before
            following[vertex] = par
            previous[par] = vertex
            if before >= 0:
                following[before] = vertex
            sign[par] = True
        else:
            after = following[par]
            previous[vertex] = par
            following[vertex] = after
            following[par] = vertex
            if after >= 0:
                previous[after] = vertex
            sign[par] = False
    permutation = []
    vertex = source
    while vertex != -1:
        permutation.append(vertex)
        vertex = following[vertex]
    if len(permutation) != n or permutation[-1] != target:
        return None
    position = [0] * n
    for i, vertex in enumerate(permutation):
        position[vertex] = i
    for vertex in range(n):
        if vertex == source:
            if not any(position[to] > 0 for to in graph[vertex]):
                return None
        elif vertex == target:
            if not any(position[to] < n - 1 for to in graph[vertex]):
                return None
        elif (not any(position[to] < position[vertex] for to in graph[vertex])
              or not any(position[to] > position[vertex] for to in graph[vertex])):
            return None
    return position


def _dijkstra_with_parent(graph, start, forced=None):
    n = len(graph)
    inf = float("inf")
    distance = [inf] * n
    parent_edge = [-1] * n
    heap = []
    if forced is None:
        distance[start] = 0
        heappush(heap, (0, start))
    else:
        vertex = start
        value = 0
        distance[vertex] = 0
        heappush(heap, (0, vertex))
        for to, edge_id, weight in forced:
            value += weight
            parent_edge[to] = edge_id
            distance[to] = value
            heappush(heap, (value, to))
            vertex = to
    while heap:
        dist, vertex = heappop(heap)
        if distance[vertex] != dist:
            continue
        for to, weight, edge_id in graph[vertex]:
            nxt = dist + weight
            if nxt < distance[to]:
                distance[to] = nxt
                parent_edge[to] = edge_id
                heappush(heap, (nxt, to))
    return distance, parent_edge


def shortest_path_without_each_edge(n, edges, source, target):
    """Shortest s-t distance after deleting each undirected edge.

    Edges are ``(u,v,positive_weight)`` and may be parallel.  All non-selected
    shortest-path edges keep the original shortest distance; selected path
    edges are answered by offline interval minima.  Complexity is
    O((N+M) log N).
    """
    graph = [[] for _ in range(n)]
    for edge_id, (u, v, weight) in enumerate(edges):
        if weight <= 0:
            raise ValueError("replacement-path routine requires positive weights")
        graph[u].append((v, weight, edge_id))
        graph[v].append((u, weight, edge_id))
    distance_s, parent_s = _dijkstra_with_parent(graph, source)
    shortest = distance_s[target]
    if shortest == float("inf"):
        return [float("inf")] * len(edges)
    path_edges = []
    path_vertices = [target]
    vertex = target
    while vertex != source:
        edge_id = parent_s[vertex]
        if edge_id < 0:
            return [float("inf")] * len(edges)
        path_edges.append(edge_id)
        u, v, _ = edges[edge_id]
        vertex = u ^ v ^ vertex
        path_vertices.append(vertex)
    path_edges.reverse()
    path_vertices.reverse()
    path_edge_set = set(path_edges)
    k = len(path_edges)
    if k == 0:
        return [0] * len(edges)

    forced = []
    for i in range(k - 1, -1, -1):
        edge_id = path_edges[i]
        forced.append((path_vertices[i], edge_id, edges[edge_id][2]))
    distance_t, parent_t = _dijkstra_with_parent(graph, target, forced)

    path_index = [-1] * n
    for i, v in enumerate(path_vertices):
        path_index[v] = i

    def attachment(parent_edge, root, reverse_path=False):
        children = [[] for _ in range(n)]
        for v, edge_id in enumerate(parent_edge):
            if edge_id >= 0:
                u, w, _ = edges[edge_id]
                par = u ^ w ^ v
                children[par].append(v)
        label = [-1] * n
        label[root] = path_index[root]
        stack = [root]
        while stack:
            v = stack.pop()
            for to in children[v]:
                index = path_index[to]
                label[to] = index if index >= 0 else label[v]
                stack.append(to)
        return label

    left_label = attachment(parent_s, source)
    right_label = attachment(parent_t, target, True)
    starts = [[] for _ in range(k)]
    for edge_id, (u, v, weight) in enumerate(edges):
        if edge_id in path_edge_set:
            continue
        if distance_s[u] < float("inf") and distance_t[v] < float("inf"):
            left = left_label[u]
            right = right_label[v]
            if 0 <= left < right:
                starts[left].append((distance_s[u] + weight + distance_t[v], right))
        if distance_s[v] < float("inf") and distance_t[u] < float("inf"):
            left = left_label[v]
            right = right_label[u]
            if 0 <= left < right:
                starts[left].append((distance_s[v] + weight + distance_t[u], right))
    replacement = [float("inf")] * k
    heap = []
    for i in range(k):
        for candidate in starts[i]:
            heappush(heap, candidate)
        while heap and heap[0][1] <= i:
            heappop(heap)
        if heap:
            replacement[i] = heap[0][0]
    answer = [shortest] * len(edges)
    for i, edge_id in enumerate(path_edges):
        answer[edge_id] = replacement[i]
    return answer
