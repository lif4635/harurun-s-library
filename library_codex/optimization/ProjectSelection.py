from library_codex.graph_flow.MaxFlow import MaxFlowGraph


_INF = float("inf")
_NEG_INF = float("-inf")


class ProjectSelection:
    __slots__ = (
        "original",
        "source",
        "sink",
        "node_count",
        "offset",
        "cost_zero",
        "cost_one",
        "pairs",
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
        self.cost_zero = [0] * variable_count
        self.cost_one = [0] * variable_count
        self.pairs = {}
        self.edges = []
        self.solved = False

    def _check(self):
        if self.solved:
            raise RuntimeError("cannot add terms after solve")

    def _variable(self, variable):
        if not 0 <= variable < self.original:
            raise IndexError("variable out of range")

    def _add_pair(self, first, second, zero_zero, zero_one, one_zero, one_one):
        self._variable(first)
        self._variable(second)
        if first == second:
            self.cost_zero[first] += zero_zero
            self.cost_one[first] += one_one
            return
        if first > second:
            first, second = second, first
            zero_one, one_zero = one_zero, zero_one
        key = first * self.original + second
        costs = self.pairs.get(key)
        if costs is None:
            self.pairs[key] = [zero_zero, zero_one, one_zero, one_one]
        else:
            costs[0] += zero_zero
            costs[1] += zero_one
            costs[2] += one_zero
            costs[3] += one_one

    def _hard_capacity(self):
        if self.offset != self.offset or self.offset == _NEG_INF:
            raise ValueError("costs must not contain NaN or negative infinity")
        if self.offset == _INF:
            raise ValueError("constraints forbid every possible assignment")
        capacity = 1
        for value in self.cost_zero:
            if value != value or value == _NEG_INF:
                raise ValueError("costs must not contain NaN or negative infinity")
            if value != _INF:
                capacity += abs(value)
        for value in self.cost_one:
            if value != value or value == _NEG_INF:
                raise ValueError("costs must not contain NaN or negative infinity")
            if value != _INF:
                capacity += abs(value)
        for costs in self.pairs.values():
            for value in costs:
                if value != value or value == _NEG_INF:
                    raise ValueError("costs must not contain NaN or negative infinity")
                if value != _INF:
                    capacity += abs(value)
        for _, _, value in self.edges:
            capacity += abs(value)
        return capacity

    @staticmethod
    def _replace_infinity(costs, hard_capacity):
        finite = [cost for cost in costs if cost != _INF]
        if not finite:
            raise ValueError("constraints forbid every possible assignment")
        replacement = min(finite) + hard_capacity
        return [replacement if cost == _INF else cost for cost in costs]

    @classmethod
    def _replace_pair_infinity(cls, costs, hard_capacity):
        result = cls._replace_infinity(costs, hard_capacity)
        difference = result[0] + result[3] - result[1] - result[2]
        if difference > 0:
            if costs[1] == _INF:
                result[1] += difference
            elif costs[2] == _INF:
                result[2] += difference
        return result

    def add_constant_cost(self, cost):
        self._check()
        self.offset += cost

    def add_constant_profit(self, profit):
        self.add_constant_cost(-profit)

    def add_unary_cost(self, variable, cost_zero, cost_one):
        self._check()
        self._variable(variable)
        self.cost_zero[variable] += cost_zero
        self.cost_one[variable] += cost_one

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
        self._add_pair(first, second, 0, cost, 0, 0)

    def add_cost_10(self, first, second, cost):
        self.add_cost_01(second, first, cost)

    def add_pair_cost(self, first, second, costs):
        self._check()
        if len(costs) != 2 or any(len(row) != 2 for row in costs):
            raise ValueError("pair cost must be a 2 by 2 table")
        zero_zero, zero_one = costs[0]
        one_zero, one_one = costs[1]
        self._add_pair(
            first,
            second,
            zero_zero,
            zero_one,
            one_zero,
            one_one,
        )

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
        if profit < 0 or profit != profit or profit == _INF:
            raise ValueError("profit must be finite and nonnegative")
        if profit == 0:
            return
        variables = list(variables)
        for variable in variables:
            self._variable(variable)
        self.offset -= profit
        auxiliary = self.node_count
        self.node_count += 1
        self.edges.append((self.source, auxiliary, profit))
        for variable in variables:
            self.edges.append((auxiliary, variable, profit))

    def add_profit_all_one(self, variables, profit):
        self._check()
        if profit < 0 or profit != profit or profit == _INF:
            raise ValueError("profit must be finite and nonnegative")
        if profit == 0:
            return
        variables = list(variables)
        for variable in variables:
            self._variable(variable)
        self.offset -= profit
        auxiliary = self.node_count
        self.node_count += 1
        self.edges.append((auxiliary, self.sink, profit))
        for variable in variables:
            self.edges.append((variable, auxiliary, profit))

    def build(self):
        self._check()
        hard_capacity = self._hard_capacity()
        cost_zero = [0] * self.original
        cost_one = [0] * self.original
        for variable in range(self.original):
            zero, one = self._replace_infinity(
                [self.cost_zero[variable], self.cost_one[variable]],
                hard_capacity,
            )
            cost_zero[variable] = zero
            cost_one[variable] = one
        offset = self.offset
        pair_edges = []
        for key, costs in self.pairs.items():
            first, second = divmod(key, self.original)
            zero_zero, zero_one, one_zero, one_one = self._replace_pair_infinity(
                costs,
                hard_capacity,
            )
            capacity = zero_one + one_zero - zero_zero - one_one
            if capacity < 0:
                raise ValueError(
                    f"combined pair cost for variables {first} and {second} "
                    "is not submodular"
                )
            offset += zero_zero
            cost_one[first] += one_zero - zero_zero
            cost_one[second] += one_one - one_zero
            if capacity:
                pair_edges.append((first, second, capacity))
        graph = MaxFlowGraph(self.node_count)
        for variable in range(self.original):
            zero = cost_zero[variable]
            one = cost_one[variable]
            if zero <= one:
                offset += zero
                if zero < one:
                    graph.add_edge(
                        self.source, variable, one - zero
                    )
            else:
                offset += one
                graph.add_edge(variable, self.sink, zero - one)
        for source, target, capacity in pair_edges:
            graph.add_edge(source, target, capacity)
        for source, target, capacity in self.edges:
            graph.add_edge(source, target, capacity)
        self.solved = True
        return graph, offset

    def min_cost(self):
        graph, offset = self.build()
        value = offset + graph.flow(self.source, self.sink)
        reachable = graph.min_cut(self.source)
        assignment = [
            0 if reachable[variable] else 1
            for variable in range(self.original)
        ]
        for variable, state in enumerate(assignment):
            costs = self.cost_zero if state == 0 else self.cost_one
            if costs[variable] == _INF:
                raise ValueError("constraints have no feasible assignment")
        for key, costs in self.pairs.items():
            first, second = divmod(key, self.original)
            index = assignment[first] * 2 + assignment[second]
            if costs[index] == _INF:
                raise ValueError("constraints have no feasible assignment")
        return value, assignment


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
        for variable, size in enumerate(sizes):
            for state in range(1, size - 1):
                project.add_cost_10(
                    positions[variable][state],
                    positions[variable][state + 1],
                    _INF,
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
