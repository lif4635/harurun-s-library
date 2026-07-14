class GraphicMatroid:
    __slots__ = ("n", "edges", "graph", "selected")

    def __init__(self, vertex_count, edges):
        self.n = vertex_count
        self.edges = list(edges)
        self.graph = [[] for _ in range(vertex_count)]
        for edge_id, (first, second) in enumerate(self.edges):
            self.graph[first].append((second, edge_id))
            self.graph[second].append((first, edge_id))
        self.selected = None

    def set(self, selected):
        self.selected = selected

    def circuit(self, edge):
        source, target = self.edges[edge]
        parent_vertex = [-1] * self.n
        parent_edge = [-1] * self.n
        parent_vertex[source] = source
        queue = [source]
        for vertex in queue:
            if vertex == target:
                break
            for neighbor, edge_id in self.graph[vertex]:
                if not self.selected[edge_id] or parent_vertex[neighbor] >= 0:
                    continue
                parent_vertex[neighbor] = vertex
                parent_edge[neighbor] = edge_id
                queue.append(neighbor)
        if parent_vertex[target] < 0:
            return []
        result = [edge]
        vertex = target
        while vertex != source:
            result.append(parent_edge[vertex])
            vertex = parent_vertex[vertex]
        return result


class PartitionMatroid:
    __slots__ = ("groups", "limits", "members")

    def __init__(self, groups, limits):
        self.groups = list(groups)
        self.limits = list(limits)
        self.members = None

    def set(self, selected):
        members = [[] for _ in self.limits]
        for element, chosen in enumerate(selected):
            group = self.groups[element]
            if chosen and group >= 0:
                members[group].append(element)
        self.members = members

    def circuit(self, element):
        group = self.groups[element]
        if group < 0 or len(self.members[group]) < self.limits[group]:
            return []
        return self.members[group] + [element]


class TransversalMatroid:
    """Elements are left vertices; independence means matchability to right vertices."""

    __slots__ = ("left_size", "right_size", "graph", "selected", "match_left",
                 "match_right")

    def __init__(self, left_size, right_size, edges):
        self.left_size = left_size
        self.right_size = right_size
        self.graph = [[] for _ in range(left_size)]
        for left, right in edges:
            self.graph[left].append(right)
        self.selected = None
        self.match_left = None
        self.match_right = None

    def _augment(self, start, match_left, match_right):
        parent_right = [-1] * self.right_size
        seen_left = bytearray(self.left_size)
        seen_left[start] = 1
        queue = [start]
        free = -1
        for left in queue:
            for right in self.graph[left]:
                if parent_right[right] >= 0:
                    continue
                parent_right[right] = left
                matched = match_right[right]
                if matched < 0:
                    free = right
                    break
                if not seen_left[matched]:
                    seen_left[matched] = 1
                    queue.append(matched)
            if free >= 0:
                break
        if free < 0:
            return False
        right = free
        while right >= 0:
            left = parent_right[right]
            previous = match_left[left]
            match_left[left] = right
            match_right[right] = left
            right = previous
        return True

    def set(self, selected):
        self.selected = selected
        match_left = [-1] * self.left_size
        match_right = [-1] * self.right_size
        for left, chosen in enumerate(selected):
            if chosen and not self._augment(left, match_left, match_right):
                raise ValueError("selected set is not independent")
        self.match_left = match_left
        self.match_right = match_right

    def circuit(self, element):
        seen_left = bytearray(self.left_size)
        seen_right = bytearray(self.right_size)
        seen_left[element] = 1
        queue = [element]
        for left in queue:
            for right in self.graph[left]:
                if seen_right[right]:
                    continue
                seen_right[right] = 1
                matched = self.match_right[right]
                if matched < 0:
                    return []
                if not seen_left[matched]:
                    seen_left[matched] = 1
                    queue.append(matched)
        result = [element]
        result.extend(left for left in range(self.left_size)
                      if left != element and seen_left[left] and self.selected[left])
        return result


def minimum_matroid_intersection(first, second, weights):
    """Minimum weight common independent set for every attainable cardinality."""
    weights = list(weights)
    size = len(weights)
    selected = [False] * size
    costs = [0]
    selections = [selected[:]]
    total = 0
    source = size
    sink = size + 1
    infinity = 10 ** 100
    scale = size + 1
    while True:
        first.set(selected)
        second.set(selected)
        graph = [[] for _ in range(size + 2)]
        for element in range(size):
            if selected[element]:
                continue
            circuit = first.circuit(element)
            edge_cost = weights[element] * scale + 1
            if not circuit:
                graph[source].append((element, edge_cost))
            else:
                for old in circuit:
                    if old != element:
                        graph[old].append((element, edge_cost))
            circuit = second.circuit(element)
            if not circuit:
                graph[element].append((sink, 0))
            else:
                for old in circuit:
                    if old != element:
                        graph[element].append((old, -weights[old] * scale + 1))
        distance = [infinity] * (size + 2)
        predecessor = [-1] * (size + 2)
        distance[source] = 0
        for _ in range(size + 1):
            updated = False
            for vertex, row in enumerate(graph):
                if distance[vertex] == infinity:
                    continue
                base = distance[vertex]
                for neighbor, edge_cost in row:
                    candidate = base + edge_cost
                    if candidate < distance[neighbor]:
                        distance[neighbor] = candidate
                        predecessor[neighbor] = vertex
                        updated = True
            if not updated:
                break
        if distance[sink] == infinity:
            break
        vertex = predecessor[sink]
        if vertex < 0:
            raise ArithmeticError("broken matroid augmenting path")
        while vertex != source:
            selected[vertex] = not selected[vertex]
            total += weights[vertex] if selected[vertex] else -weights[vertex]
            vertex = predecessor[vertex]
            if vertex < 0:
                raise ArithmeticError("broken matroid augmenting path")
        costs.append(total)
        selections.append(selected[:])
    return costs, selections


MinimumMatroidIntersection = minimum_matroid_intersection
