class SatSolver:
    """Iterative watched-literal SAT solver with chronological backtracking."""

    __slots__ = ("n", "clauses", "activity", "assignment", "assigns")

    def __init__(self, variable_count):
        if variable_count < 0:
            raise ValueError("variable_count must be nonnegative")
        self.n = variable_count
        self.clauses = []
        self.activity = [0] * variable_count
        self.assignment = [-1] * variable_count
        self.assigns = [False] * variable_count

    def _literal(self, literal):
        if isinstance(literal, int):
            if literal == 0 or abs(literal) > self.n:
                raise ValueError("literal is outside the variable range")
            return literal
        variable, value = literal
        if not 0 <= variable < self.n:
            raise ValueError("variable is outside the range")
        return variable + 1 if value else -variable - 1

    def add_clause(self, clause):
        values = []
        seen = set()
        for source in clause:
            literal = self._literal(source)
            if -literal in seen:
                return
            if literal not in seen:
                seen.add(literal)
                values.append(literal)
                self.activity[abs(literal) - 1] += 1
        self.clauses.append(values)

    def if_then(self, first_variable, first_value, second_variable, second_value):
        self.add_clause(((first_variable, not first_value),
                         (second_variable, second_value)))

    def set_val(self, variable, value):
        self.add_clause(((variable, value),))

    @staticmethod
    def _index(literal):
        return ((abs(literal) - 1) << 1) | (literal < 0)

    def solve(self, assumptions=()):
        assignment = [-1] * self.n
        trail = []
        queue_index = 0
        watches = [[] for _ in range(self.n << 1)]
        watch_positions = []
        contradiction = False

        def literal_state(literal):
            value = assignment[abs(literal) - 1]
            if value < 0:
                return -1
            return value if literal > 0 else value ^ 1

        def enqueue(literal):
            variable = abs(literal) - 1
            value = 1 if literal > 0 else 0
            old = assignment[variable]
            if old >= 0:
                return old == value
            assignment[variable] = value
            trail.append(literal)
            return True

        for clause_id, clause in enumerate(self.clauses):
            if not clause:
                contradiction = True
                watch_positions.append((0, 0))
            elif len(clause) == 1:
                watch_positions.append((0, 0))
                watches[self._index(clause[0])].append(clause_id)
                if not enqueue(clause[0]):
                    contradiction = True
            else:
                watch_positions.append((0, 1))
                watches[self._index(clause[0])].append(clause_id)
                watches[self._index(clause[1])].append(clause_id)
        for source in assumptions:
            if not enqueue(self._literal(source)):
                contradiction = True

        def propagate(start):
            current = start
            while current < len(trail):
                false_literal = -trail[current]
                current += 1
                watch_index = self._index(false_literal)
                watching = watches[watch_index]
                position = 0
                while position < len(watching):
                    clause_id = watching[position]
                    clause = self.clauses[clause_id]
                    first, second = watch_positions[clause_id]
                    if clause[first] == false_literal:
                        false_position, other_position = first, second
                    elif clause[second] == false_literal:
                        false_position, other_position = second, first
                    else:
                        watching[position] = watching[-1]
                        watching.pop()
                        continue
                    other_literal = clause[other_position]
                    if literal_state(other_literal) == 1:
                        position += 1
                        continue
                    replacement = -1
                    for candidate in range(len(clause)):
                        if candidate == other_position or candidate == false_position:
                            continue
                        if literal_state(clause[candidate]) != 0:
                            replacement = candidate
                            break
                    if replacement >= 0:
                        if false_position == first:
                            watch_positions[clause_id] = (replacement, second)
                        else:
                            watch_positions[clause_id] = (first, replacement)
                        watches[self._index(clause[replacement])].append(clause_id)
                        watching[position] = watching[-1]
                        watching.pop()
                        continue
                    state = literal_state(other_literal)
                    if state == 0 or not enqueue(other_literal):
                        return current, clause_id
                    position += 1
            return current, -1

        decisions = []
        if not contradiction:
            queue_index, conflict = propagate(queue_index)
            contradiction = conflict >= 0
        while True:
            if contradiction:
                while decisions:
                    variable, trail_size, tried_false = decisions.pop()
                    while len(trail) > trail_size:
                        literal = trail.pop()
                        assignment[abs(literal) - 1] = -1
                    queue_index = trail_size
                    if not tried_false:
                        decisions.append((variable, trail_size, True))
                        enqueue(-variable - 1)
                        queue_index, conflict = propagate(queue_index)
                        contradiction = conflict >= 0
                        break
                else:
                    self.assignment = assignment
                    self.assigns = [value == 1 for value in assignment]
                    return False
                continue
            variable = -1
            best_activity = -1
            for index, value in enumerate(assignment):
                if value < 0 and self.activity[index] > best_activity:
                    variable = index
                    best_activity = self.activity[index]
            if variable < 0:
                self.assignment = assignment
                self.assigns = [value == 1 for value in assignment]
                return True
            decisions.append((variable, len(trail), False))
            enqueue(variable + 1)
            queue_index, conflict = propagate(queue_index)
            contradiction = conflict >= 0


SATSolver = SatSolver
