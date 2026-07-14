from library_codex.graph.MaxFlow import MaxFlowGraph


class ProjectSelection:
    __slots__ = (
        "original",
        "source",
        "sink",
        "node_count",
        "offset",
        "base",
        "edges",
        "solved",
    )

    def __init__(self, variable_count):
        if variable_count < 0:
            raise ValueError("variable_count must be nonnegative")
        self.original = variable_count
        self.source = variable_count
        self.sink = variable_count + 1
        self.node_count = variable_count + 2
        self.offset = 0
        self.base = [[0, 0] for _ in range(variable_count)]
        self.edges = []
        self.solved = False

    def _check(self):
        if self.solved:
            raise RuntimeError("cannot add terms after solve")

    def add_constant_cost(self, cost):
        self._check()
        self.offset += cost

    def add_constant_profit(self, profit):
        self.add_constant_cost(-profit)

    def add_unary_cost(self, variable, cost_zero, cost_one):
        self._check()
        self.base[variable][0] += cost_zero
        self.base[variable][1] += cost_one

    def add_unary_profit(self, variable, profit_zero, profit_one):
        self.add_unary_cost(variable, -profit_zero, -profit_one)

    def add_cost_0(self, variable, cost):
        self.add_unary_cost(variable, cost, 0)

    def add_cost_1(self, variable, cost):
        self.add_unary_cost(variable, 0, cost)

    def add_profit_0(self, variable, profit):
        self.add_unary_cost(variable, -profit, 0)

    def add_profit_1(self, variable, profit):
        self.add_unary_cost(variable, 0, -profit)

    def add_cost_01(self, first, second, cost):
        self._check()
        if cost < 0:
            raise ValueError("cost must be nonnegative")
        if cost:
            self.edges.append((first, second, cost))

    def add_cost_10(self, first, second, cost):
        self.add_cost_01(second, first, cost)

    def add_pair_cost(self, first, second, costs):
        zero_zero, zero_one = costs[0]
        one_zero, one_one = costs[1]
        penalty = zero_one + one_zero - zero_zero - one_one
        if penalty < 0:
            raise ValueError("pair cost must be submodular")
        self.add_constant_cost(zero_zero)
        self.add_unary_cost(first, 0, one_zero - zero_zero)
        self.add_unary_cost(second, 0, one_one - one_zero)
        self.add_cost_01(first, second, penalty)

    def add_pair_profit(self, first, second, profits):
        self.add_pair_cost(
            first,
            second,
            [[-value for value in row] for row in profits],
        )

    def add_profit_00(self, first, second, profit):
        self.add_pair_cost(first, second, [[-profit, 0], [0, 0]])

    def add_profit_11(self, first, second, profit):
        self.add_pair_cost(first, second, [[0, 0], [0, -profit]])

    def add_profit_all_zero(self, variables, profit):
        self._check()
        if profit < 0:
            raise ValueError("profit must be nonnegative")
        if profit == 0:
            return
        self.offset -= profit
        auxiliary = self.node_count
        self.node_count += 1
        self.edges.append((self.source, auxiliary, profit))
        for variable in variables:
            self.edges.append((auxiliary, variable, profit))

    def add_profit_all_one(self, variables, profit):
        self._check()
        if profit < 0:
            raise ValueError("profit must be nonnegative")
        if profit == 0:
            return
        self.offset -= profit
        auxiliary = self.node_count
        self.node_count += 1
        self.edges.append((auxiliary, self.sink, profit))
        for variable in variables:
            self.edges.append((variable, auxiliary, profit))

    def min_cost(self):
        self._check()
        self.solved = True
        graph = MaxFlowGraph(self.node_count)
        offset = self.offset
        for variable, (cost_zero, cost_one) in enumerate(self.base):
            if cost_zero <= cost_one:
                offset += cost_zero
                if cost_zero < cost_one:
                    graph.add_edge(
                        self.source, variable, cost_one - cost_zero
                    )
            else:
                offset += cost_one
                graph.add_edge(variable, self.sink, cost_zero - cost_one)
        for source, target, capacity in self.edges:
            graph.add_edge(source, target, capacity)
        value = offset + graph.flow(self.source, self.sink)
        reachable = graph.min_cut(self.source)
        assignment = [
            0 if reachable[variable] else 1
            for variable in range(self.original)
        ]
        return value, assignment

    minCost = min_cost


class KProjectSelection:
    __slots__ = ("sizes", "positions", "project")

    def __init__(self, sizes):
        if any(size < 1 for size in sizes):
            raise ValueError("every variable must have at least one state")
        self.sizes = list(sizes)
        positions = []
        count = 0
        for size in sizes:
            current = [-1] * size
            for state in range(1, size):
                current[state] = count
                count += 1
            positions.append(current)
        self.positions = positions
        project = ProjectSelection(count)
        infinity = 10 ** 100
        for variable, size in enumerate(sizes):
            for state in range(1, size - 1):
                project.add_cost_10(
                    positions[variable][state],
                    positions[variable][state + 1],
                    infinity,
                )
        self.project = project

    def add_constant_cost(self, cost):
        self.project.add_constant_cost(cost)

    def add_constant_profit(self, profit):
        self.project.add_constant_profit(profit)

    def add_unary_cost(self, variable, costs):
        size = self.sizes[variable]
        if len(costs) != size:
            raise ValueError("invalid unary cost length")
        self.project.add_constant_cost(costs[-1])
        for state in range(1, size):
            self.project.add_unary_cost(
                self.positions[variable][state],
                0,
                costs[state - 1] - costs[state],
            )

    def add_pair_cost(self, first, second, costs):
        first_size = self.sizes[first]
        second_size = self.sizes[second]
        if len(costs) != first_size or any(
            len(row) != second_size for row in costs
        ):
            raise ValueError("invalid pair cost shape")
        first_base = [costs[state][0] for state in range(first_size)]
        second_base = [
            costs[0][state] - costs[0][0]
            for state in range(second_size)
        ]
        self.add_unary_cost(first, first_base)
        self.add_unary_cost(second, second_base)
        for x in range(1, first_size):
            for y in range(1, second_size):
                difference = (
                    costs[x][y]
                    - costs[x][y - 1]
                    - costs[x - 1][y]
                    + costs[x - 1][y - 1]
                )
                if difference > 0:
                    raise ValueError("pair cost must be Monge")
                self.project.add_profit_00(
                    self.positions[first][x],
                    self.positions[second][y],
                    -difference,
                )

    def min_cost(self):
        value, bits = self.project.min_cost()
        assignment = [0] * len(self.sizes)
        for variable, size in enumerate(self.sizes):
            for state in range(1, size):
                if bits[self.positions[variable][state]]:
                    break
                assignment[variable] = state
        return value, assignment

    minCost = min_cost
