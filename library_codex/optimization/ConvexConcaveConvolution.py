"""凸・凹列とのmin-plusまたはmax-plus畳み込みを計算する。"""

from library_codex.optimization.MonotoneMinima import monotone_minima

def convex_min_plus_convolution(convex, arbitrary, return_argmin=False):
    """Min-plus convolution where ``convex`` has nondecreasing differences."""
    if not convex or not arbitrary:
        return ([], []) if return_argmin else []
    first_size = len(convex)
    second_size = len(arbitrary)

    def compare(output, first, second):
        first_convex = output - first
        second_convex = output - second
        if not 0 <= first_convex < first_size:
            return False
        if not 0 <= second_convex < first_size:
            return True
        return convex[first_convex] + arbitrary[first] <= (
            convex[second_convex] + arbitrary[second]
        )

    indices = monotone_minima(
        first_size + second_size - 1, second_size, compare=compare
    )
    values = [convex[output - index] + arbitrary[index]
              for output, index in enumerate(indices)]
    if not return_argmin:
        return values
    convex_indices = [output - index for output, index in enumerate(indices)]
    return values, convex_indices

def concave_max_plus_convolution(concave, arbitrary, return_argmax=False):
    negated_convex = [-value for value in concave]
    negated_arbitrary = [-value for value in arbitrary]
    result = convex_min_plus_convolution(
        negated_convex, negated_arbitrary, return_argmax
    )
    if return_argmax:
        values, indices = result
        return [-value for value in values], indices
    return [-value for value in result]

