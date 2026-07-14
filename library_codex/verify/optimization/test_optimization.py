from itertools import product
import random

from library_codex.optimization.Optimization import (
    MonotoneConvexHullTrick,
    LineContainer,
    convex_convex_min_plus_convolution,
    convex_min_plus_convolution,
    golden_section_search,
    maximal_rectangle,
    maximal_rectangle_binary,
    monotone_minima,
)
from library_codex.optimization.ProjectSelection import (
    KProjectSelection,
    ProjectSelection,
)


def test_monotone_minima_and_convex_min_plus():
    rng = random.Random(718934)
    for rows in range(100):
        columns = rng.randrange(1, 100)
        centers = sorted(rng.randrange(columns) for _ in range(rows))
        matrix = [
            [(column - centers[row]) ** 2 for column in range(columns)]
            for row in range(rows)
        ]
        expected = [min(range(columns), key=matrix[row].__getitem__) for row in range(rows)]
        assert monotone_minima(rows, columns, lambda i, j: matrix[i][j]) == expected
    for _ in range(5000):
        first = [rng.randrange(-100, 101) for _ in range(rng.randrange(1, 30))]
        differences = sorted(rng.randrange(-30, 31) for _ in range(rng.randrange(29)))
        second = [rng.randrange(-100, 101)]
        for difference in differences:
            second.append(second[-1] + difference)
        expected = [
            min(
                first[index] + second[total - index]
                for index in range(len(first))
                if 0 <= total - index < len(second)
            )
            for total in range(len(first) + len(second) - 1)
        ]
        assert convex_min_plus_convolution(first, second) == expected
        first_convex = [rng.randrange(-100, 101)]
        for difference in sorted(rng.randrange(-30, 31) for _ in range(rng.randrange(29))):
            first_convex.append(first_convex[-1] + difference)
        expected = [
            min(
                first_convex[index] + second[total - index]
                for index in range(len(first_convex))
                if 0 <= total - index < len(second)
            )
            for total in range(len(first_convex) + len(second) - 1)
        ]
        assert convex_convex_min_plus_convolution(first_convex, second) == expected


def test_monotone_cht_all_directions_and_objectives():
    rng = random.Random(187349)
    for minimize in (False, True):
        for increasing in (False, True):
            for _ in range(500):
                slopes = sorted(set(rng.randrange(-1000, 1001) for _ in range(100)))
                if not increasing:
                    slopes.reverse()
                lines = [(slope, rng.randrange(-10**6, 10**6)) for slope in slopes]
                container = MonotoneConvexHullTrick(minimize, increasing)
                for line in lines:
                    container.add_line(*line)
                for _ in range(200):
                    point = rng.randrange(-10**6, 10**6)
                    values = [slope * point + intercept for slope, intercept in lines]
                    expected = min(values) if minimize else max(values)
                    assert container.query(point) == expected
    for minimize in (False, True):
        for _ in range(500):
            lines = [
                (rng.randrange(-10**9, 10**9), rng.randrange(-10**18, 10**18))
                for _ in range(200)
            ]
            container = LineContainer(minimize)
            for line in lines:
                container.add_line(*line)
            for _ in range(200):
                point = rng.randrange(-(1 << 62), 1 << 62)
                values = [slope * point + intercept for slope, intercept in lines]
                assert container.query(point) == (
                    min(values) if minimize else max(values)
                )


def test_rectangle_and_integer_golden_search():
    rng = random.Random(981734)
    for size in range(100):
        heights = [rng.randrange(30) for _ in range(size)]
        expected = max(
            [0]
            + [
                min(heights[left:right]) * (right - left)
                for left in range(size)
                for right in range(left + 1, size + 1)
            ]
        )
        assert maximal_rectangle(heights) == expected
    for height in range(20):
        for width in range(20):
            matrix = [[rng.randrange(2) for _ in range(width)] for _ in range(height)]
            prefix = [[0] * (width + 1) for _ in range(height + 1)]
            for row in range(height):
                for column in range(width):
                    prefix[row + 1][column + 1] = (
                        prefix[row][column + 1]
                        + prefix[row + 1][column]
                        - prefix[row][column]
                        + matrix[row][column]
                    )
            expected = 0
            for top in range(height):
                for bottom in range(top + 1, height + 1):
                    for left in range(width):
                        for right in range(left + 1, width + 1):
                            area = (bottom - top) * (right - left)
                            total = (
                                prefix[bottom][right]
                                - prefix[top][right]
                                - prefix[bottom][left]
                                + prefix[top][left]
                            )
                            if total == area:
                                expected = max(expected, area)
            assert maximal_rectangle_binary(matrix) == expected
    for _ in range(10000):
        center = rng.randrange(-10**9, 10**9)
        left = rng.randrange(-10**9, center + 1)
        right = rng.randrange(center, 10**9 + 1)
        point, value = golden_section_search(
            lambda x: (x - center) ** 2 + 7, left, right
        )
        assert (point, value) == (center, 7)


def test_binary_project_selection_against_brute():
    rng = random.Random(519873)
    for size in range(8):
        for _ in range(1000):
            unary = [[rng.randrange(-20, 21) for _ in range(2)] for _ in range(size)]
            pairs = []
            solver = ProjectSelection(size)
            for variable in range(size):
                solver.add_unary_cost(variable, *unary[variable])
            for first in range(size):
                for second in range(first):
                    if rng.randrange(3) == 0:
                        a = rng.randrange(-20, 21)
                        b = rng.randrange(-20, 21)
                        c = rng.randrange(-20, 21)
                        d = b + c - a - rng.randrange(21)
                        costs = [[a, b], [c, d]]
                        pairs.append((first, second, costs))
                        solver.add_pair_cost(first, second, costs)
            expected = None
            for assignment in product(range(2), repeat=size):
                cost = sum(unary[i][assignment[i]] for i in range(size))
                cost += sum(costs[assignment[i]][assignment[j]] for i, j, costs in pairs)
                if expected is None or cost < expected:
                    expected = cost
            value, assignment = solver.min_cost()
            assert value == expected
            actual = sum(unary[i][assignment[i]] for i in range(size))
            actual += sum(costs[assignment[i]][assignment[j]] for i, j, costs in pairs)
            assert actual == expected


def test_k_project_selection_against_brute_monge():
    rng = random.Random(613894)
    for _ in range(5000):
        sizes = [rng.randrange(1, 5) for _ in range(rng.randrange(1, 5))]
        solver = KProjectSelection(sizes)
        unary = []
        for variable, size in enumerate(sizes):
            costs = [rng.randrange(-20, 21) for _ in range(size)]
            unary.append(costs)
            solver.add_unary_cost(variable, costs)
        pairs = []
        for first in range(len(sizes)):
            for second in range(first):
                if rng.randrange(2):
                    left = [rng.randrange(-10, 11) for _ in range(sizes[first])]
                    right = [rng.randrange(-10, 11) for _ in range(sizes[second])]
                    weight = rng.randrange(10)
                    costs = [
                        [left[x] + right[y] - weight * x * y for y in range(sizes[second])]
                        for x in range(sizes[first])
                    ]
                    pairs.append((first, second, costs))
                    solver.add_pair_cost(first, second, costs)
        expected = None
        for assignment in product(*(range(size) for size in sizes)):
            cost = sum(unary[i][assignment[i]] for i in range(len(sizes)))
            cost += sum(costs[assignment[i]][assignment[j]] for i, j, costs in pairs)
            if expected is None or cost < expected:
                expected = cost
        value, assignment = solver.min_cost()
        assert value == expected
        actual = sum(unary[i][assignment[i]] for i in range(len(sizes)))
        actual += sum(costs[assignment[i]][assignment[j]] for i, j, costs in pairs)
        assert actual == expected
