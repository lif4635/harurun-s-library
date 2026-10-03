import random

from library_codex.graph.TwoSAT import TwoSAT


def test_two_sat_against_all_assignments():
    rng = random.Random(31)
    for n in range(9):
        for _ in range(500):
            clauses = [
                (rng.randrange(n), bool(rng.randrange(2)),
                 rng.randrange(n), bool(rng.randrange(2)))
                for _ in range(rng.randrange(20))
            ] if n else []
            expected = []
            for mask in range(1 << n):
                values = [bool(mask >> v & 1) for v in range(n)]
                if all(values[a] == av or values[b] == bv for a, av, b, bv in clauses):
                    expected.append(values)
            solver = TwoSAT(n)
            for clause in clauses:
                solver.add_clause(*clause)
            answer = solver.solve()
            assert (answer is not None) == bool(expected)
            if answer is not None:
                assert all(answer[a] == av or answer[b] == bv for a, av, b, bv in clauses)


def test_two_sat_at_most_one():
    solver = TwoSAT(5)
    literals = [solver.literal(i) for i in range(5)]
    solver.add_at_most_one(literals)
    solver.set_value(3)
    answer = solver.solve()
    assert answer is not None and answer[3]
    assert sum(answer) == 1
    solver = TwoSAT(2)
    solver.add_at_most_one([solver.literal(0), solver.literal(1)])
    solver.set_value(0)
    solver.set_value(1)
    assert solver.solve() is None


def test_solve_again_after_adding_constraint():
    solver = TwoSAT(2)
    solver.add_equal(0, 1)
    assert solver.solve() is not None
    solver.set_value(0, True)
    assert solver.solve() == [True, True]
    solver.set_value(1, False)
    assert solver.solve() is None
