"""凸多角形の各頂点から最も遠い頂点を、全頂点分まとめて求める。"""

from library_codex.optimization.SMAWK import smawk


def furthest_neighbors(points):
    """凸多角形の頂点順に、最遠の頂点の入力添字を返す。O(N)時間・領域。"""
    points = list(points)
    n = len(points)
    if n <= 1:
        return [0] * n
    doubled = points + points

    def value(row, column):
        if column <= row:
            return row - column
        if column >= row + n:
            return 1
        x, y = points[row]
        a, b = doubled[column]
        dx = x - a
        dy = y - b
        return -(dx * dx + dy * dy)

    return [column % n for column in smawk(n, 2 * n - 1, value)]
