"""二次元gridの一点更新と半開矩形monoid積を扱うSegment Tree。"""

class SegmentTree2D:
    __slots__ = (
        "height", "width", "row_size", "column_size", "data", "op", "identity"
    )

    def __init__(self, matrix, op, identity):
        matrix = [list(row) for row in matrix]
        height = len(matrix)
        width = len(matrix[0]) if height else 0
        if any(len(row) != width for row in matrix):
            raise ValueError("matrix must be rectangular")
        row_size = 1 << (height - 1).bit_length() if height else 1
        column_size = 1 << (width - 1).bit_length() if width else 1
        data = [
            [identity] * (column_size << 1)
            for _ in range(row_size << 1)
        ]
        for row in range(height):
            target = data[row + row_size]
            target[column_size : column_size + width] = matrix[row]
            for node in range(column_size - 1, 0, -1):
                target[node] = op(target[node << 1], target[node << 1 | 1])
        for row in range(row_size - 1, 0, -1):
            target = data[row]
            first = data[row << 1]
            second = data[row << 1 | 1]
            for column in range(1, column_size << 1):
                target[column] = op(first[column], second[column])
        self.height = height
        self.width = width
        self.row_size = row_size
        self.column_size = column_size
        self.data = data
        self.op = op
        self.identity = identity

    def set(self, row, column, value):
        row_node = row + self.row_size
        column_node = column + self.column_size
        data = self.data
        op = self.op
        data[row_node][column_node] = value
        node = column_node >> 1
        while node:
            data[row_node][node] = op(
                data[row_node][node << 1],
                data[row_node][node << 1 | 1],
            )
            node >>= 1
        row_node >>= 1
        while row_node:
            column_node = column + self.column_size
            data[row_node][column_node] = op(
                data[row_node << 1][column_node],
                data[row_node << 1 | 1][column_node],
            )
            node = column_node >> 1
            while node:
                data[row_node][node] = op(
                    data[row_node][node << 1],
                    data[row_node][node << 1 | 1],
                )
                node >>= 1
            row_node >>= 1

    def get(self, row, column):
        return self.data[row + self.row_size][column + self.column_size]

    def tolist(self):
        """現在のgridを行ごとのlistとして返す。O(HW)。"""
        offset = self.column_size
        return [
            self.data[row + self.row_size][offset:offset + self.width]
            for row in range(self.height)
        ]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "SegmentTree2D(%r)" % self.tolist()

    def _column_prod(self, row_node, left, right):
        left += self.column_size
        right += self.column_size
        result = self.identity
        op = self.op
        data = self.data[row_node]
        while left < right:
            if left & 1:
                result = op(result, data[left])
                left += 1
            if right & 1:
                right -= 1
                result = op(result, data[right])
            left >>= 1
            right >>= 1
        return result

    def prod(self, top, left, bottom, right):
        top += self.row_size
        bottom += self.row_size
        result = self.identity
        op = self.op
        while top < bottom:
            if top & 1:
                result = op(result, self._column_prod(top, left, right))
                top += 1
            if bottom & 1:
                bottom -= 1
                result = op(result, self._column_prod(bottom, left, right))
            top >>= 1
            bottom >>= 1
        return result

    query = prod
