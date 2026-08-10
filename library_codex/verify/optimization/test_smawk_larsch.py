import random

from library_codex.optimization.LARSCH import LARSCH
from library_codex.optimization.SMAWK import smawk


def test_smawk_against_brute_totally_monotone_matrices():
    rng = random.Random(817293)
    assert smawk(0, 0, value=lambda row, column: 0) == []
    for rows in range(1, 50):
        for _ in range(20):
            columns = rng.randrange(1, 60)
            centers = sorted(
                rng.randrange(-columns, 2 * columns) for _ in range(rows)
            )

            def value(row, column):
                return (column - centers[row]) ** 2 + row * 7

            expected = [
                min(range(columns), key=lambda column: value(row, column))
                for row in range(rows)
            ]
            assert smawk(rows, columns, value=value) == expected
            assert smawk(
                rows,
                columns,
                better=lambda row, candidate, current: (
                    value(row, candidate) < value(row, current)
                ),
            ) == expected


def test_larsch_online_argmin_and_reset():
    rng = random.Random(912837)
    for size in range(80):
        base = [rng.randrange(-1000, 1001) for _ in range(size)]

        def value(row, column):
            return base[column] + (row - column) ** 2

        expected = [
            min(range(row + 1), key=lambda column: value(row, column))
            for row in range(size)
        ]
        solver = LARSCH(size, value)
        assert [solver.get_argmin() for _ in range(size)] == expected
        solver.reset()
        assert [solver.get_argmin() for _ in range(size)] == expected
        try:
            solver.get_argmin()
        except IndexError:
            pass
        else:
            raise AssertionError("exhausted LARSCH must reject another row")


def test_smawk_and_larsch_use_linear_number_of_evaluations():
    size = 10000
    smawk_calls = [0]

    def matrix_value(row, column):
        smawk_calls[0] += 1
        return (column - row // 2) ** 2

    assert smawk(size, size, value=matrix_value) == [
        row // 2 for row in range(size)
    ]
    assert smawk_calls[0] <= 12 * size

    larsch_calls = [0]

    def triangular_value(row, column):
        larsch_calls[0] += 1
        return (row - column) ** 2

    solver = LARSCH(size, triangular_value)
    assert [solver.get_argmin() for _ in range(size)] == list(range(size))
    assert larsch_calls[0] <= 12 * size
