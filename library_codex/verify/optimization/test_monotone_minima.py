import random

from library_codex.optimization.MonotoneMinima import monotone_minima


def test_monotone_minima_against_rows():
    rng = random.Random(718934)
    for rows in range(100):
        columns = rng.randrange(1, 100)
        centers = sorted(rng.randrange(columns) for _ in range(rows))
        matrix = [
            [(column - centers[row]) ** 2 for column in range(columns)]
            for row in range(rows)
        ]
        expected = [
            min(range(columns), key=matrix[row].__getitem__)
            for row in range(rows)
        ]
        assert monotone_minima(
            rows,
            columns,
            lambda row, column: matrix[row][column],
        ) == expected
