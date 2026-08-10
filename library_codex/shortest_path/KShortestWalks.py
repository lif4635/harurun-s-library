"""非負辺重みの有向グラフで、同じ頂点や辺を再訪してよいwalkをコスト順に列挙する。"""

from heapq import heappop, heappush


def _rank(node):
    return 0 if node is None else node[3]


def _meld(first, second):
    """2つの永続leftist heapを、入力を変更せずに併合する。"""
    path = []
    while first is not None and second is not None:
        if second[0] < first[0]:
            first, second = second, first
        path.append(first)
        first = first[2]
    root = first if first is not None else second
    while path:
        old = path.pop()
        left = old[1]
        right = root
        if _rank(left) < _rank(right):
            left, right = right, left
        root = (old[0], left, right, _rank(right) + 1)
    return root


def _insert(root, item):
    return _meld(root, (item, None, None, 1))


def k_shortest_walks(vertex_count, edges, source, target, k):
    """sourceからtargetへのwalkのコストを、小さい順に最大k個返す。"""
    if k <= 0:
        return []
    if not 0 <= source < vertex_count or not 0 <= target < vertex_count:
        raise IndexError("source or target is outside the graph")

    graph = [[] for _ in range(vertex_count)]
    reverse = [[] for _ in range(vertex_count)]
    for edge_id, edge in enumerate(edges):
        start, end, cost = edge
        if not 0 <= start < vertex_count or not 0 <= end < vertex_count:
            raise IndexError("an edge endpoint is outside the graph")
        if cost < 0:
            raise ValueError("edge weights must be nonnegative")
        graph[start].append((end, cost, edge_id))
        reverse[end].append((start, cost, edge_id))

    infinity = float("inf")
    distance = [infinity] * vertex_count
    parent = [-1] * vertex_count
    parent_edge = [-1] * vertex_count
    distance[target] = 0
    heap = [(0, target)]
    while heap:
        dist, vertex = heappop(heap)
        if dist != distance[vertex]:
            continue
        for predecessor, cost, edge_id in reverse[vertex]:
            candidate = dist + cost
            if candidate < distance[predecessor]:
                distance[predecessor] = candidate
                parent[predecessor] = vertex
                parent_edge[predecessor] = edge_id
                heappush(heap, (candidate, predecessor))

    if distance[source] == infinity:
        return []

    children = [[] for _ in range(vertex_count)]
    for vertex in range(vertex_count):
        if parent[vertex] != -1:
            children[parent[vertex]].append(vertex)

    roots = [None] * vertex_count
    order = [target]
    for vertex in order:
        root = None if vertex == target else roots[parent[vertex]]
        tree_edge = parent_edge[vertex]
        for to, cost, edge_id in graph[vertex]:
            if edge_id == tree_edge or distance[to] == infinity:
                continue
            delta = cost + distance[to] - distance[vertex]
            root = _insert(root, (delta, to, edge_id))
        roots[vertex] = root
        order.extend(children[vertex])

    answer = [distance[source]]
    root = roots[source]
    if root is None:
        return answer

    candidates = []
    serial = 0
    heappush(candidates, (answer[0] + root[0][0], serial, root))
    while candidates and len(answer) < k:
        cost, _, node = heappop(candidates)
        answer.append(cost)
        delta, to, _edge_id = node[0]
        left = node[1]
        right = node[2]
        if left is not None:
            serial += 1
            heappush(candidates, (
                cost + left[0][0] - delta, serial, left
            ))
        if right is not None:
            serial += 1
            heappush(candidates, (
                cost + right[0][0] - delta, serial, right
            ))
        next_root = roots[to]
        if next_root is not None:
            serial += 1
            heappush(candidates, (
                cost + next_root[0][0], serial, next_root
            ))
    return answer
