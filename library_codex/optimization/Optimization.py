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


def convex_min_plus_convolution(arbitrary, convex):
    if not arbitrary or not convex:
        return []
    first_size = len(arbitrary)
    second_size = len(convex)
    output_size = first_size + second_size - 1

    def compare(row, first, second):
        first_index = row - first
        second_index = row - second
        if not 0 <= first_index < second_size:
            return False
        if not 0 <= second_index < second_size:
            return True
        return (
            arbitrary[first] + convex[first_index]
            <= arbitrary[second] + convex[second_index]
        )

    indices = monotone_minima(
        output_size, first_size, compare=compare
    )
    return [
        arbitrary[index] + convex[row - index]
        for row, index in enumerate(indices)
    ]


def convex_convex_min_plus_convolution(first, second):
    if not first or not second:
        return []
    first_difference = [
        first[index + 1] - first[index]
        for index in range(len(first) - 1)
    ]
    second_difference = [
        second[index + 1] - second[index]
        for index in range(len(second) - 1)
    ]
    left = 0
    right = 0
    result = [first[0] + second[0]]
    while left < len(first_difference) or right < len(second_difference):
        if right == len(second_difference) or (
            left < len(first_difference)
            and first_difference[left] < second_difference[right]
        ):
            difference = first_difference[left]
            left += 1
        else:
            difference = second_difference[right]
            right += 1
        result.append(result[-1] + difference)
    return result


class MonotoneConvexHullTrick:
    __slots__ = ("lines", "direction", "sign")

    def __init__(self, minimize=True, increasing_slopes=True):
        self.lines = []
        self.direction = 1 if increasing_slopes else -1
        self.sign = 1 if minimize else -1

    @staticmethod
    def _obsolete(first, second, third):
        return (
            (first[1] - second[1]) * (third[0] - second[0])
            <= (second[1] - third[1]) * (second[0] - first[0])
        )

    def add_line(self, slope, intercept):
        slope *= self.direction
        intercept *= self.sign
        lines = self.lines
        if lines and slope < lines[-1][0]:
            raise ValueError("slopes must be added in the declared order")
        if lines and slope == lines[-1][0]:
            if lines[-1][1] <= intercept:
                return
            lines.pop()
        line = (slope, intercept)
        while len(lines) >= 2 and self._obsolete(
            lines[-2], lines[-1], line
        ):
            lines.pop()
        lines.append(line)

    add = add_line

    def query(self, point):
        lines = self.lines
        if not lines:
            raise ValueError("line container is empty")
        point *= self.direction * self.sign
        left = 0
        right = len(lines) - 1
        while left < right:
            middle = (left + right) >> 1
            first = lines[middle][0] * point + lines[middle][1]
            second = lines[middle + 1][0] * point + lines[middle + 1][1]
            if first <= second:
                right = middle
            else:
                left = middle + 1
        line = lines[left]
        return (line[0] * point + line[1]) * self.sign

    get = query


class LineContainer:
    __slots__ = ("tree",)

    def __init__(
        self, minimize=True, left=-(1 << 63), right=1 << 63
    ):
        from library_codex.data_structure.LiChaoTree import DynamicLiChaoTree

        self.tree = DynamicLiChaoTree(left, right, minimize)

    def add_line(self, slope, intercept):
        self.tree.add_line(slope, intercept)

    add = add_line

    def query(self, point):
        return self.tree.query(point)

    get = query


def maximal_rectangle(heights):
    stack = []
    best = 0
    for index in range(len(heights) + 1):
        height = heights[index] if index < len(heights) else 0
        start = index
        while stack and stack[-1][0] >= height:
            previous, start = stack.pop()
            best = max(best, previous * (index - start))
        stack.append((height, start))
    return best


def maximal_rectangle_binary(matrix, truthy=True):
    if not matrix:
        return 0
    width = len(matrix[0])
    heights = [0] * width
    result = 0
    for row in matrix:
        if len(row) != width:
            raise ValueError("matrix rows must have equal length")
        for column, value in enumerate(row):
            if bool(value) == truthy:
                heights[column] += 1
            else:
                heights[column] = 0
        result = max(result, maximal_rectangle(heights))
    return result


def golden_section_search(function, left, right, minimize=True):
    if left > right:
        raise ValueError("left must not exceed right")
    before = left - 1
    smaller = 1
    larger = 2
    while larger < right - left + 2:
        smaller, larger = larger, smaller + larger
    point = before + larger - smaller
    boundary = before + larger
    point_value = function(point)
    while before + boundary != point * 2:
        other = before + boundary - point
        if other > right:
            move_boundary = True
        else:
            other_value = function(other)
            move_boundary = (
                point_value < other_value
                if minimize
                else point_value > other_value
            )
        if move_boundary:
            boundary = before
            before = other
        else:
            before = point
            point = other
            point_value = other_value
    return point, point_value


MonotoneMinima = monotone_minima
MinPlusConvolution_arbitrary_convex = convex_min_plus_convolution
MinPlusConvolution_convex_convex = convex_convex_min_plus_convolution
ConvexHullTrickAddMonotone = MonotoneConvexHullTrick
MinLineContainer = LineContainer
MaximalRectangle = maximal_rectangle
