"""Monge性を持つ行列の各行最小位置を高速に求める。"""

def monotone_minima(rows, columns, value=None, compare=None):
    if rows < 0 or columns <= 0:
        raise ValueError("rows must be nonnegative and columns positive")
    if compare is None:
        if value is None:
            raise ValueError("value or compare must be supplied")

        def compare(row, first, second):
            return value(row, first) <= value(row, second)

    result = [0] * rows
    stack = [(0, rows, 0, columns)]
    while stack:
        row_begin, row_end, column_begin, column_end = stack.pop()
        if row_begin == row_end:
            continue
        row = (row_begin + row_end) >> 1
        best = column_begin
        for column in range(column_begin + 1, column_end):
            if not compare(row, best, column):
                best = column
        result[row] = best
        stack.append((row + 1, row_end, best, column_end))
        stack.append((row_begin, row, column_begin, best + 1))
    return result

