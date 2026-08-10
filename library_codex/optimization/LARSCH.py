"""Monge 型の下三角行列について、行を順に受け取って最小列を求める。"""


class _ColumnMap:
    __slots__ = ("parent", "columns")

    def __init__(self, parent=None, columns=None):
        self.parent = parent
        self.columns = columns

    def map(self, column):
        current = self
        while current is not None:
            if current.columns is not None:
                column = current.columns[column]
            current = current.parent
        return column


class _Evaluator:
    __slots__ = ("value", "scale", "offset", "column_map")

    def __init__(self, value, scale=1, offset=0, column_map=None):
        self.value = value
        self.scale = scale
        self.offset = offset
        self.column_map = column_map

    def __call__(self, row, column):
        row = self.scale * row + self.offset
        if self.column_map is not None:
            column = self.column_map.map(column)
        return self.value(row, column)


class _ReduceRows:
    __slots__ = ("size", "evaluate", "row", "state", "reduced")

    def __init__(self, size, evaluate):
        self.size = size
        self.evaluate = evaluate
        self.row = 0
        self.state = 0
        reduced_size = size >> 1
        if reduced_size:
            odd_rows = _Evaluator(
                evaluate.value,
                evaluate.scale << 1,
                evaluate.scale + evaluate.offset,
                evaluate.column_map,
            )
            self.reduced = _ReduceColumns(reduced_size, odd_rows)
        else:
            self.reduced = None

    def reset(self):
        self.row = 0
        self.state = 0
        if self.reduced is not None:
            self.reduced.reset()

    def get_argmin(self):
        row = self.row
        if row >= self.size:
            raise IndexError("all row minima have already been returned")
        self.row = row + 1
        evaluate = self.evaluate
        if row & 1:
            if evaluate(row, self.state) <= evaluate(row, row):
                return self.state
            return row

        previous = self.state
        if row + 1 == self.size:
            following = self.size - 1
        else:
            following = self.reduced.get_argmin()
        self.state = following
        best = previous
        for column in range(previous + 1, following + 1):
            if evaluate(row, column) < evaluate(row, best):
                best = column
        return best


class _ReduceColumns:
    __slots__ = (
        "size", "evaluate", "row", "columns", "column_map", "reduced"
    )

    def __init__(self, size, evaluate):
        self.size = size
        self.evaluate = evaluate
        self.row = 0
        self.columns = []
        self.column_map = _ColumnMap(evaluate.column_map, self.columns)
        mapped = _Evaluator(
            evaluate.value,
            evaluate.scale,
            evaluate.offset,
            self.column_map,
        )
        self.reduced = _ReduceRows(size, mapped)

    def reset(self):
        self.row = 0
        self.columns.clear()
        self.reduced.reset()

    def _push(self, column, row):
        columns = self.columns
        evaluate = self.evaluate
        while columns:
            length = len(columns)
            if length == row:
                break
            previous = columns[-1]
            if evaluate(length - 1, column) >= evaluate(
                length - 1, previous
            ):
                break
            columns.pop()
        if len(columns) != self.size:
            columns.append(column)

    def get_argmin(self):
        row = self.row
        if row >= self.size:
            raise IndexError("all row minima have already been returned")
        self.row = row + 1
        if row == 0:
            self.columns.clear()
            self.columns.append(0)
        else:
            self._push(2 * row - 1, row)
            self._push(2 * row, row)
        return self.columns[self.reduced.get_argmin()]


class LARSCH:
    """下三角Monge行列のrow 0, 1, ...のargminをオンラインに返す。"""

    __slots__ = ("size", "_rows")

    def __init__(self, size, value):
        if size < 0:
            raise ValueError("size must be nonnegative")
        self.size = size
        self._rows = _ReduceRows(size, _Evaluator(value))

    def get_argmin(self):
        """次の行について、最小値を取る最小の列番号を返す。"""
        return self._rows.get_argmin()

    def reset(self):
        """次の呼出しがrow 0から再開するように内部状態を戻す。"""
        self._rows.reset()
