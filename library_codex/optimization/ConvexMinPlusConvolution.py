"""凸列を含むmin-plus畳み込みを高速に計算する。"""

from library_codex.optimization.MonotoneMinima import monotone_minima

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

