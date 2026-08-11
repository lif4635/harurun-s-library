"""行・列とも昇順の整数matrixから、順位で要素を選ぶ。"""

from bisect import bisect_left, bisect_right


def _shape(matrix):
    rows = len(matrix)
    columns = len(matrix[0]) if rows else 0
    if any(len(row) != columns for row in matrix):
        raise ValueError("matrix rows must have equal length")
    return rows, columns


def _count_le(matrix, value, rows, columns):
    row = rows - 1
    column = 0
    count = 0
    while row >= 0 and column < columns:
        if matrix[row][column] <= value:
            count += row + 1
            column += 1
        else:
            row -= 1
    return count


def kth(matrix, k):
    """matrix全要素を昇順に並べたときのk番目の値を返す。"""
    rows, columns = _shape(matrix)
    if not 0 <= k < rows * columns:
        raise IndexError("k is outside the matrix")
    lower = matrix[0][0]
    upper = matrix[-1][-1]
    while lower < upper:
        middle = (lower + upper) // 2
        if _count_le(matrix, middle, rows, columns) > k:
            upper = middle
        else:
            lower = middle + 1
    return lower


def take(matrix, k):
    """先頭k要素が各rowから何個来るか、row優先の同値順で返す。"""
    rows, columns = _shape(matrix)
    total = rows * columns
    if not 0 <= k <= total:
        raise IndexError("k is outside the matrix")
    if k == 0:
        return [0] * rows
    if k == total:
        return [columns] * rows

    boundary = kth(matrix, k - 1)
    counts = [bisect_left(row, boundary) for row in matrix]
    remaining = k - sum(counts)
    for index, row in enumerate(matrix):
        equal = bisect_right(row, boundary) - counts[index]
        selected = min(equal, remaining)
        counts[index] += selected
        remaining -= selected
        if remaining == 0:
            break
    return counts
