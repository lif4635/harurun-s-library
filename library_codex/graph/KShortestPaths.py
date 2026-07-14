"""K shortest loopless paths by iterative Yen enumeration."""

from heapq import heappop, heappush


def _shortest_path(graph, source, target, banned_vertices, banned_edges):
    if source in banned_vertices or target in banned_vertices:
        return None
    n = len(graph)
    inf = float("inf")
    distance = [inf] * n
    parent_vertex = [-1] * n
    parent_edge = [-1] * n
    distance[source] = 0
    heap = [(0, source)]
    while heap:
        dist, v = heappop(heap)
        if distance[v] != dist:
            continue
        if v == target:
            break
        for to, weight, edge_id in graph[v]:
            if edge_id in banned_edges or to in banned_vertices:
                continue
            nxt = dist + weight
            if nxt < distance[to]:
                distance[to] = nxt
                parent_vertex[to] = v
                parent_edge[to] = edge_id
                heappush(heap, (nxt, to))
    if distance[target] == inf:
        return None
    vertices = []
    edge_ids = []
    v = target
    while v != source:
        vertices.append(v)
        edge_ids.append(parent_edge[v])
        v = parent_vertex[v]
    vertices.append(source)
    vertices.reverse()
    edge_ids.reverse()
    return distance[target], vertices, edge_ids


def _yen(graph, edge_weight, source, target, k):
    if k <= 0:
        return []
    first = _shortest_path(graph, source, target, set(), set())
    if first is None:
        return []
    answer = [first]
    accepted = {tuple(first[2])}
    candidates = []
    queued = set()
    serial = 0
    while len(answer) < k:
        _, previous_vertices, previous_edges = answer[-1]
        root_cost = 0
        for spur_index in range(len(previous_vertices) - 1):
            root_vertices = previous_vertices[:spur_index + 1]
            root_edges = previous_edges[:spur_index]
            removed = set()
            for _, vertices, edge_ids in answer:
                if (len(vertices) > spur_index
                        and vertices[:spur_index + 1] == root_vertices
                        and edge_ids[:spur_index] == root_edges):
                    removed.add(edge_ids[spur_index])
            banned_vertices = set(root_vertices[:-1])
            spur = _shortest_path(
                graph, root_vertices[-1], target, banned_vertices, removed
            )
            if spur is not None:
                spur_cost, spur_vertices, spur_edges = spur
                vertices = root_vertices[:-1] + spur_vertices
                edge_ids = root_edges + spur_edges
                key = tuple(edge_ids)
                if key not in accepted and key not in queued:
                    serial += 1
                    heappush(candidates, (
                        root_cost + spur_cost, serial, vertices, edge_ids
                    ))
                    queued.add(key)
            root_cost += edge_weight[previous_edges[spur_index]]
        if not candidates:
            break
        cost, _, vertices, edge_ids = heappop(candidates)
        key = tuple(edge_ids)
        queued.remove(key)
        accepted.add(key)
        answer.append((cost, vertices, edge_ids))
    return answer


def k_shortest_paths_directed(n, edges, source, target, k):
    """Return up to k directed loopless paths in nondecreasing cost order.

    Edges are ``(from, to, nonnegative_weight)``.  Each result is
    ``(cost, vertices, original_edge_ids)``.  Parallel edges are distinct.
    """
    graph = [[] for _ in range(n)]
    weight = [0] * len(edges)
    for edge_id, (u, v, cost) in enumerate(edges):
        if cost < 0:
            raise ValueError("Yen's algorithm requires nonnegative weights")
        graph[u].append((v, cost, edge_id))
        weight[edge_id] = cost
    return _yen(graph, weight, source, target, k)


def k_shortest_paths_undirected(n, edges, source, target, k):
    """Return up to k undirected loopless paths in nondecreasing cost order."""
    graph = [[] for _ in range(n)]
    weight = [0] * len(edges)
    for edge_id, (u, v, cost) in enumerate(edges):
        if cost < 0:
            raise ValueError("Yen's algorithm requires nonnegative weights")
        graph[u].append((v, cost, edge_id))
        graph[v].append((u, cost, edge_id))
        weight[edge_id] = cost
    return _yen(graph, weight, source, target, k)


class KShortestPathDirected:
    """Incremental wrapper compatible with repeated get-next usage."""

    def __init__(self, n, source, target):
        self.n = n
        self.source = source
        self.target = target
        self.edges = []
        self._answer = None
        self._position = 0

    def add_edge(self, source, target, weight):
        self.edges.append((source, target, weight))
        self._answer = None
        return len(self.edges) - 1

    def solve(self, k):
        return k_shortest_paths_directed(
            self.n, self.edges, self.source, self.target, k
        )

    def get_next_smallest(self):
        # Yen candidates depend on all previous paths; doubling amortizes calls.
        if self._answer is None or self._position >= len(self._answer):
            need = max(1, (self._position + 1) << 1)
            self._answer = self.solve(need)
        if self._position >= len(self._answer):
            return None
        result = self._answer[self._position]
        self._position += 1
        return result


class KShortestPathUndirected(KShortestPathDirected):
    def solve(self, k):
        return k_shortest_paths_undirected(
            self.n, self.edges, self.source, self.target, k
        )
