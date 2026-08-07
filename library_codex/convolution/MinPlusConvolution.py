"""凸列を含むmin-plus畳み込みを高速に計算する。"""

from library_codex.optimization.MonotoneMinima import monotone_minima


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
        return (
            arbitrary[first] + convex[first_convex_index]
            <= arbitrary[second] + convex[second_convex_index]
        )

    arbitrary_indices = monotone_minima(
        output_size, arbitrary_size, compare=compare
    )
    values = [
        arbitrary[index] + convex[total - index]
        for total, index in enumerate(arbitrary_indices)
    ]
    if not return_argmin:
        return values
    convex_indices = [
        total - index for total, index in enumerate(arbitrary_indices)
    ]
    return values, convex_indices


def minplus_conv_convex(first, second):
    """2つの凸列のmin-plus畳み込みを線形時間で計算する。"""
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
