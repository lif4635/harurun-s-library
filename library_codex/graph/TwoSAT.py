"""2-SATの充足可能性を判定し、真偽割当を返す。"""

from library_codex.graph_connectivity.StronglyConnectedComponents import SCC

class TwoSAT:
    """2-SAT with the node convention ``2*v=false, 2*v+1=true``."""

    __slots__ = ("n", "variable_count", "graph", "answer")

    def __init__(self, n):
        self.n = n
        self.variable_count = n
        self.graph = [[] for _ in range(n << 1)]
        self.answer = None

    @staticmethod
    def literal(variable, value=True):
        return (variable << 1) | bool(value)

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
        scc = SCC(self.graph)
        component = scc.component
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
