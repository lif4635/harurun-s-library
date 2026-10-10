"""Monge性を持つ行列の各行最小位置を高速に求める。"""

def monotone_minima(rows, columns, value=None, compare=None):
    if rows < 0 or columns <= 0:
        raise ValueError('rows must be nonnegative and columns positive')
    if compare is None:
        if value is None:
            raise ValueError('value or compare must be supplied')

        def compare(row, first, second):
            return value(row, first) <= value(row, second)
    result = [0] * rows
    stack = [(0, rows, 0, columns)]
    while stack:
        (row_begin, row_end, column_begin, column_end) = stack.pop()
        if row_begin == row_end:
            continue
        row = row_begin + row_end >> 1
        best = column_begin
        for column in range(column_begin + 1, column_end):
            if not compare(row, best, column):
                best = column
        result[row] = best
        stack.append((row + 1, row_end, best, column_end))
        stack.append((row_begin, row, column_begin, best + 1))
    return result
'凸列または凹列を含むmin-plus畳み込みを高速に計算する。'

def minplus_conv(arbitrary, convex, return_argmin=False):
    """一般列と凸列のmin-plus畳み込みを高速に計算する。"""
    if not arbitrary or not convex:
        return ([], []) if return_argmin else []
    arbitrary_size = len(arbitrary)
    convex_size = len(convex)
    output_size = arbitrary_size + convex_size - 1

    def compare(total, first, second):
        first_convex_index = total - first
        second_convex_index = total - second
        if not 0 <= first_convex_index < convex_size:
            return False
        if not 0 <= second_convex_index < convex_size:
            return True
        return arbitrary[first] + convex[first_convex_index] <= arbitrary[second] + convex[second_convex_index]
    arbitrary_indices = monotone_minima(output_size, arbitrary_size, compare=compare)
    values = [arbitrary[index] + convex[total - index] for (total, index) in enumerate(arbitrary_indices)]
    if not return_argmin:
        return values
    convex_indices = [total - index for (total, index) in enumerate(arbitrary_indices)]
    return (values, convex_indices)

def minplus_conv_convex(first, second):
    """2つの凸列のmin-plus畳み込みを線形時間で計算する。"""
    if not first or not second:
        return []
    first_difference = [first[index + 1] - first[index] for index in range(len(first) - 1)]
    second_difference = [second[index + 1] - second[index] for index in range(len(second) - 1)]
    left = 0
    right = 0
    result = [first[0] + second[0]]
    while left < len(first_difference) or right < len(second_difference):
        if right == len(second_difference) or (left < len(first_difference) and first_difference[left] < second_difference[right]):
            difference = first_difference[left]
            left += 1
        else:
            difference = second_difference[right]
            right += 1
        result.append(result[-1] + difference)
    return result

def _convolution_min_plus_convolution_concave_prefix(a, b, count, offset, step, result, indices):
    candidates = []
    ends = []
    for row in range(count):
        while ends and ends[-1] <= row:
            ends.pop()
            candidates.pop()
        if row < len(a):
            value = a[row]
            if not candidates or value + b[0] < a[candidates[-1]] + b[row - candidates[-1]]:
                end = count
                while candidates:
                    old = candidates[-1]
                    end = ends[-1]
                    if value + b[end - 1 - row] < a[old] + b[end - 1 - old]:
                        candidates.pop()
                        ends.pop()
                        end = count
                    else:
                        left = row + 1
                        right = end - 1
                        while left < right:
                            middle = left + right >> 1
                            if value + b[middle - row] < a[old] + b[middle - old]:
                                left = middle + 1
                            else:
                                right = middle
                        end = left
                        break
                candidates.append(row)
                ends.append(end)
        column = candidates[-1]
        value = a[column] + b[row - column]
        target = offset + step * row
        if value < result[target]:
            result[target] = value
            if indices is not None:
                indices[target] = row - column if step == 1 else len(b) - 1 - row + column

def minplus_conv_concave(arbitrary, concave, return_argmin=False):
    """一般列と、隣接差分が広義単調減少する凹列のmin-plus畳み込みを返す。"""
    if not arbitrary or not concave:
        return ([], []) if return_argmin else []
    n = len(arbitrary)
    m = len(concave)
    result = [arbitrary[0] + value for value in concave]
    result.extend((value + concave[-1] for value in arbitrary[1:]))
    indices = list(range(m)) + [m - 1] * (n - 1) if return_argmin else None
    reversed_concave = concave[::-1]
    for start in range(0, n, m):
        block = arbitrary[start:start + m]
        _convolution_min_plus_convolution_concave_prefix(block, concave, m, start, 1, result, indices)
        if len(block) > 1:
            _convolution_min_plus_convolution_concave_prefix(block[::-1], reversed_concave, len(block) - 1, start + m + len(block) - 2, -1, result, indices)
    return (result, indices) if return_argmin else result
import sys
read = sys.stdin.buffer.readline
(n, m) = map(int, read().split())
a = list(map(int, read().split()))
b = list(map(int, read().split()))
print(' '.join(map(str, minplus_conv_concave(b, a))))
