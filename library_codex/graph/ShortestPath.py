from collections import deque
import heapq


INF = float("inf")


def _edge(entry):
    if isinstance(entry, int):
        return entry, 1
    return entry[0], entry[1]


def bfs(graph, start=0, goal=None):
    n = len(graph)
    distance = [-1] * n
    previous = [-1] * n
    distance[start] = 0
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            break
        next_distance = distance[node] + 1
        for entry in graph[node]:
            other = entry if isinstance(entry, int) else entry[0]
            if distance[other] < 0:
                distance[other] = next_distance
                previous[other] = node
                queue.append(other)
    return distance, previous


def zero_one_bfs(graph, start=0):
    n = len(graph)
    distance = [INF] * n
    previous = [-1] * n
    distance[start] = 0
    queue = deque([start])
    while queue:
        node = queue.popleft()
        current = distance[node]
        for entry in graph[node]:
            other, weight = _edge(entry)
            if weight not in (0, 1):
                raise ValueError("edge weight must be 0 or 1")
            next_distance = current + weight
            if next_distance < distance[other]:
                distance[other] = next_distance
                previous[other] = node
                if weight:
                    queue.append(other)
                else:
                    queue.appendleft(other)
    return distance, previous


def dijkstra(graph, start=0, goal=None):
    n = len(graph)
    distance = [INF] * n
    previous = [-1] * n
    distance[start] = 0
    heap = [(0, start)]
    while heap:
        current, node = heapq.heappop(heap)
        if current != distance[node]:
            continue
        if node == goal:
            break
        for entry in graph[node]:
            other, weight = _edge(entry)
            if weight < 0:
                raise ValueError("Dijkstra requires nonnegative weights")
            next_distance = current + weight
            if next_distance < distance[other]:
                distance[other] = next_distance
                previous[other] = node
                heapq.heappush(heap, (next_distance, other))
    return distance, previous


def restore_path(previous, goal, start=None):
    path = []
    node = goal
    while node >= 0:
        path.append(node)
        if node == start:
            break
        node = previous[node]
    if start is not None and path[-1] != start:
        return []
    path.reverse()
    return path


def bellman_ford(vertex_count, edges, start=0):
    distance = [INF] * vertex_count
    previous = [-1] * vertex_count
    distance[start] = 0
    for _ in range(vertex_count - 1):
        changed = False
        for first, second, weight, *_ in edges:
            if distance[first] != INF:
                value = distance[first] + weight
                if value < distance[second]:
                    distance[second] = value
                    previous[second] = first
                    changed = True
        if not changed:
            break
    negative = bytearray(vertex_count)
    for _ in range(vertex_count):
        changed = False
        for first, second, weight, *_ in edges:
            if distance[first] == INF:
                continue
            if distance[first] + weight < distance[second] or negative[first]:
                if not negative[second]:
                    changed = True
                negative[second] = 1
                distance[second] = -INF
        if not changed:
            break
    return distance, previous, negative


def warshall_floyd(matrix):
    distance = [list(row) for row in matrix]
    n = len(distance)
    for middle in range(n):
        middle_row = distance[middle]
        for first in range(n):
            base = distance[first][middle]
            if base == INF:
                continue
            row = distance[first]
            for second in range(n):
                value = base + middle_row[second]
                if value < row[second]:
                    row[second] = value
    return distance


def topological_sort(graph, lexicographical=False):
    n = len(graph)
    indegree = [0] * n
    for row in graph:
        for entry in row:
            other = entry if isinstance(entry, int) else entry[0]
            indegree[other] += 1
    if lexicographical:
        queue = [node for node in range(n) if indegree[node] == 0]
        heapq.heapify(queue)
        result = []
        while queue:
            node = heapq.heappop(queue)
            result.append(node)
            for entry in graph[node]:
                other = entry if isinstance(entry, int) else entry[0]
                indegree[other] -= 1
                if indegree[other] == 0:
                    heapq.heappush(queue, other)
    else:
        queue = deque(node for node in range(n) if indegree[node] == 0)
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for entry in graph[node]:
                other = entry if isinstance(entry, int) else entry[0]
                indegree[other] -= 1
                if indegree[other] == 0:
                    queue.append(other)
    return result if len(result) == n else None


def connected_components(graph):
    n = len(graph)
    component = [-1] * n
    groups = []
    for start in range(n):
        if component[start] >= 0:
            continue
        component[start] = len(groups)
        group = []
        stack = [start]
        while stack:
            node = stack.pop()
            group.append(node)
            for entry in graph[node]:
                other = entry if isinstance(entry, int) else entry[0]
                if component[other] < 0:
                    component[other] = component[start]
                    stack.append(other)
        groups.append(group)
    return component, groups


def bipartite_coloring(graph):
    n = len(graph)
    color = [-1] * n
    for start in range(n):
        if color[start] >= 0:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for entry in graph[node]:
                other = entry if isinstance(entry, int) else entry[0]
                if color[other] < 0:
                    color[other] = color[node] ^ 1
                    queue.append(other)
                elif color[other] == color[node]:
                    return None
    return color


def dfs_forest(graph, root=0, postorder=False):
    """Return ``(DFS order, parent)`` for all components without recursion."""
    n = len(graph)
    if n == 0:
        return [], []
    parent = [-2] * n
    order = []
    starts = list(range(root, n)) + list(range(root))
    for start in starts:
        if parent[start] != -2:
            continue
        parent[start] = -1
        if not postorder:
            order.append(start)
        stack = [(start, 0)]
        while stack:
            vertex, index = stack[-1]
            if index == len(graph[vertex]):
                stack.pop()
                if postorder:
                    order.append(vertex)
                continue
            entry = graph[vertex][index]
            stack[-1] = (vertex, index + 1)
            to = entry if isinstance(entry, int) else entry[0]
            if parent[to] == -2:
                parent[to] = vertex
                if not postorder:
                    order.append(to)
                stack.append((to, 0))
    return order, parent


dijkstra_restore = dijkstra
bfs_restore = bfs
bfs01 = zero_one_bfs
floyd_warshall = warshall_floyd
