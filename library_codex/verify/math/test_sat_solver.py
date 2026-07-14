import itertools
import random

from library_codex.math.SATSolver import SatSolver


def test_sat_solver_against_exhaustive_assignments():
    rng = random.Random(71)
    for variables in range(8):
        for _ in range(300):
            clauses = []
            for _ in range(rng.randrange(15)):
                clause = []
                for _ in range(rng.randrange(5)):
                    if variables:
                        variable = rng.randrange(variables)
                        clause.append((variable, bool(rng.randrange(2))))
                clauses.append(clause)
            expected = None
            for assignment in itertools.product((False, True), repeat=variables):
                if all(any(assignment[v] == value for v, value in clause)
                       for clause in clauses):
                    expected = assignment
                    break
            solver = SatSolver(variables)
            for clause in clauses:
                solver.add_clause(clause)
            assert solver.solve() == (expected is not None)
            if expected is not None:
                assert all(any(solver.assigns[v] == value for v, value in clause)
                           for clause in clauses)


def test_sat_implications_and_assumptions():
    solver = SatSolver(4)
    solver.set_val(0, True)
    solver.if_then(0, True, 1, True)
    solver.if_then(1, True, 2, False)
    assert solver.solve()
    assert solver.assigns[:3] == [True, True, False]
    assert not solver.solve(((2, True),))
