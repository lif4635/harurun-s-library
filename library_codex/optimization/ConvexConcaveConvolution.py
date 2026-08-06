"""凹列とのmax-plus畳み込みを計算する。"""

from library_codex.optimization.ConvexMinPlusConvolution import (
    convex_min_plus_convolution,
)

def concave_max_plus_convolution(concave, arbitrary, return_argmax=False):
    negated_convex = [-value for value in concave]
    negated_arbitrary = [-value for value in arbitrary]
    result = convex_min_plus_convolution(
        negated_arbitrary, negated_convex, return_argmax
    )
    if return_argmax:
        values, indices = result
        return [-value for value in values], indices
    return [-value for value in result]
