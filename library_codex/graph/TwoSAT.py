"""2-SATの充足可能性を判定し、真偽割当を返す。"""

from graph.StronglyConnectedComponents import StronglyConnectedComponents

class TwoSAT:
    """2-SAT with the node convention ``2*v=false, 2*v+1=true``."""

    __slots__ = ("n", "graph", "answer")

    def __init__(self, n):
        self.n = n
        self.graph = [[] for _ in range(n << 1)]
        self.answer = None

    @staticmethod
    def literal(variable, value=True):
        return (variable << 1) | bool(value)

    def add_implication_literal(self, source, target):
        self.graph[source].append(target)
        self.graph[target ^ 1].append(source ^ 1)

    def add_clause_literal(self, first, second):
        self.graph[first ^ 1].append(second)
        self.graph[second ^ 1].append(first)

    def add_clause(self, first_variable, first_value,
                   second_variable, second_value):
        self.add_clause_literal(
            self.literal(first_variable, first_value),
            self.literal(second_variable, second_value),
        )

    def set_value(self, variable, value=True):
        literal = self.literal(variable, value)
        self.graph[literal ^ 1].append(literal)

    def add_xor(self, first, second):
        self.add_clause(first, True, second, True)
        self.add_clause(first, False, second, False)

    def add_equal(self, first, second):
        self.add_clause(first, False, second, True)
        self.add_clause(first, True, second, False)

    def solve(self):
        scc = StronglyConnectedComponents(self.graph)
        component = scc.component
        answer = [False] * self.n
        for variable in range(self.n):
            false = variable << 1
            if component[false] == component[false | 1]:
                self.answer = None
                return None
            answer[variable] = component[false] < component[false | 1]
        self.answer = answer
        return answer

    satisfiable = solve

