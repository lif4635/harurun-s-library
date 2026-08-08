"""998244353上の2次元NTTと2変数係数畳み込み。

行列`values[i][j]`を$x^i y^j$の係数として扱う。`ntt2d`と`intt2d`は
各辺長が2の冪である長方形listを破壊的に変換する。
"""

from library_codex.convolution.NTT998 import MOD, intt, ntt


def _shape(matrix):
    rows = len(matrix)
    if rows == 0:
        return 0, 0
    columns = len(matrix[0])
    if columns == 0:
        raise ValueError("matrix rows must be nonempty")
    for row in matrix:
        if len(row) != columns:
            raise ValueError("matrix must be rectangular")
    return rows, columns


def ntt2d(values):
    """2次元係数行列を破壊的に順変換し、同じ2次元listを返す。O(RC(log R+log C))。"""

    rows, columns = _shape(values)
    if rows == 0:
        return values
    for row in values:
        ntt(row)
    column = [0] * rows
    for index in range(columns):
        for row in range(rows):
            column[row] = values[row][index]
        ntt(column)
        for row in range(rows):
            values[row][index] = column[row]
    return values


def intt2d(values):
    """2次元周波数行列を破壊的に正規化済み逆変換して返す。O(RC(log R+log C))。"""

    rows, columns = _shape(values)
    if rows == 0:
        return values
    for row in values:
        intt(row)
    column = [0] * rows
    for index in range(columns):
        for row in range(rows):
            column[row] = values[row][index]
        intt(column)
        for row in range(rows):
            values[row][index] = column[row]
    return values


def multiply2d(first, second):
    r"""2つの2変数係数行列の積を`(R1+R2-1)x(C1+C2-1)`で返す。O(RC(log R+log C))。"""

    first_rows, first_columns = _shape(first)
    second_rows, second_columns = _shape(second)
    if first_rows == 0 or second_rows == 0:
        return []
    output_rows = first_rows + second_rows - 1
    output_columns = first_columns + second_columns - 1
    rows = 1 << (output_rows - 1).bit_length()
    columns = 1 << (output_columns - 1).bit_length()
    left = [[0] * columns for _ in range(rows)]
    right = [[0] * columns for _ in range(rows)]
    for row in range(first_rows):
        for column in range(first_columns):
            left[row][column] = first[row][column] % MOD
    for row in range(second_rows):
        for column in range(second_columns):
            right[row][column] = second[row][column] % MOD
    ntt2d(left)
    ntt2d(right)
    for row in range(rows):
        left_row = left[row]
        right_row = right[row]
        for column in range(columns):
            left_row[column] = left_row[column] * right_row[column] % MOD
    intt2d(left)
    return [row[:output_columns] for row in left[:output_rows]]
