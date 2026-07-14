class StronglyConnectedComponents:
    __slots__ = ("n", "graph", "component", "groups", "dag", "count")

    def __init__(self, graph):
        n = len(graph)
        adjacency = [[] for _ in range(n)]
        reverse = [[] for _ in range(n)]
        for node, row in enumerate(graph):
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
                node, index = stack[-1]
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
        for node, row in enumerate(adjacency):
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


def strongly_connected_components(graph):
    solver = StronglyConnectedComponents(graph)
    return solver.component, solver.groups


SCC = StronglyConnectedComponents
