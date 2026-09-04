import random

from library_codex.optimization.MaximalRectangle import (
    maximal_rectangle,
    maximal_rectangle_binary,
)


def test_maximal_rectangle_histogram_against_brute():
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


def test_maximal_rectangle_binary_against_prefix_sum():
    rng = random.Random(981734)
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
