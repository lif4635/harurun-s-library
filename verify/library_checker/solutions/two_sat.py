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
'2-SATの充足可能性を判定し、真偽割当を返す。'

class TwoSAT:
    """2-SAT with the node convention ``2*v=false, 2*v+1=true``."""
    __slots__ = ('n', 'variable_count', 'graph', 'answer')

    def __init__(self, n):
        self.n = n
        self.variable_count = n
        self.graph = [[] for _ in range(n << 1)]
        self.answer = None

    @staticmethod
    def literal(variable, value=True):
        return variable << 1 | bool(value)

    def add_implication_literal(self, source, target):
        self.graph[source].append(target)
        self.graph[target ^ 1].append(source ^ 1)

    def add_variable(self):
        """補助変数を1個追加し、その変数番号を返す。"""
        variable = self.variable_count
        self.variable_count += 1
        self.graph.extend(([], []))
        return variable

    def add_clause_literal(self, first, second):
        self.graph[first ^ 1].append(second)
        self.graph[second ^ 1].append(first)

    def add_clause(self, first_variable, first_value, second_variable, second_value):
        self.add_clause_literal(self.literal(first_variable, first_value), self.literal(second_variable, second_value))

    def set_value(self, variable, value=True):
        literal = self.literal(variable, value)
        self.graph[literal ^ 1].append(literal)

    def add_xor(self, first, second):
        self.add_clause(first, True, second, True)
        self.add_clause(first, False, second, False)

    def add_equal(self, first, second):
        self.add_clause(first, False, second, True)
        self.add_clause(first, True, second, False)

    def add_at_most_one(self, literals):
        """指定literalのうち高々1個だけがtrueとなる制約を追加する。"""
        literals = list(literals)
        if len(literals) <= 1:
            return
        previous = self.literal(self.add_variable())
        self.add_clause_literal(literals[0] ^ 1, previous)
        for literal in literals[1:-1]:
            current = self.literal(self.add_variable())
            self.add_clause_literal(literal ^ 1, current)
            self.add_clause_literal(previous ^ 1, current)
            self.add_clause_literal(literal ^ 1, previous ^ 1)
            previous = current
        self.add_clause_literal(literals[-1] ^ 1, previous ^ 1)

    def solve(self):
        (_, component) = scc_ids(self.graph)
        answer = [False] * self.variable_count
        for variable in range(self.variable_count):
            false = variable << 1
            if component[false] == component[false | 1]:
                self.answer = None
                return None
            answer[variable] = component[false] < component[false | 1]
        self.answer = answer[:self.n]
        return self.answer
    satisfiable = solve
import sys
read = sys.stdin.buffer.readline
header = read().split()
(n, m) = (int(header[2]), int(header[3]))
solver = TwoSAT(n)
for _ in range(m):
    (a, b, _) = map(int, read().split())
    solver.add_clause(abs(a) - 1, a > 0, abs(b) - 1, b > 0)
answer = solver.solve()
if answer is None:
    print('s UNSATISFIABLE')
else:
    print('s SATISFIABLE')
    print('v', *(i + 1 if value else -i - 1 for (i, value) in enumerate(answer)), 0)
