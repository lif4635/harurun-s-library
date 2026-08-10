"""Totally monotone な行列の各行の最小列を線形回数の比較で求める。"""


def smawk(rows, columns, value=None, better=None):
    """各行の左端の最小列を返す。行列要素は callback で遅延評価する。"""
    if rows < 0 or columns < 0:
        raise ValueError("matrix dimensions must be nonnegative")
    if rows == 0:
        return []
    if columns == 0:
        raise ValueError("a nonempty row set needs at least one column")
    if better is None:
        if value is None:
            raise ValueError("value or better must be supplied")

        def better(row, candidate, current):
            return value(row, candidate) < value(row, current)

    answer = [0] * rows
    stack = [(list(range(rows)), list(range(columns)), 0)]
    while stack:
        row_ids, column_ids, phase = stack.pop()
        if phase == 0:
            reduced = []
            for column in column_ids:
                while reduced:
                    row = row_ids[len(reduced) - 1]
                    if not better(row, column, reduced[-1]):
                        break
                    reduced.pop()
                if len(reduced) < len(row_ids):
                    reduced.append(column)
            stack.append((row_ids, reduced, 1))
            odd_rows = row_ids[1::2]
            if odd_rows:
                stack.append((odd_rows, reduced, 0))
            continue

        positions = {
            column: index for index, column in enumerate(column_ids)
        }
        for index in range(0, len(row_ids), 2):
            row = row_ids[index]
            left = 0 if index == 0 else positions[answer[row_ids[index - 1]]]
            right = (
                len(column_ids) - 1
                if index + 1 == len(row_ids)
                else positions[answer[row_ids[index + 1]]]
            )
            best = column_ids[left]
            for position in range(left + 1, right + 1):
                candidate = column_ids[position]
                if better(row, candidate, best):
                    best = candidate
            answer[row] = best
    return answer
