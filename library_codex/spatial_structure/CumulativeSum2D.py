"""静的な二次元gridの任意の半開矩形和をO(1)で返す累積和。"""

class CumulativeSum2D:
    __slots__ = ("height", "width", "data")

    def __init__(self, matrix):
        matrix = [list(row) for row in matrix]
        height = len(matrix)
        width = len(matrix[0]) if height else 0
        if any(len(row) != width for row in matrix):
            raise ValueError("matrix must be rectangular")
        data = [[0] * (width + 1) for _ in range(height + 1)]
        for row in range(height):
            running = 0
            source = matrix[row]
            previous = data[row]
            target = data[row + 1]
            for column in range(width):
                running += source[column]
                target[column + 1] = previous[column + 1] + running
        self.height = height
        self.width = width
        self.data = data

    def sum(self, top, left, bottom, right):
        data = self.data
        return (
            data[bottom][right]
            - data[top][right]
            - data[bottom][left]
            + data[top][left]
        )

    prod = sum
