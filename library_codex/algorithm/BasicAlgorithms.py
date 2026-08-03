"""Compatibility imports for the former all-in-one algorithm module.

New code should import from the focused modules directly.  This file is kept
only so existing submissions do not stop importing after the split.
"""

from library_codex.algorithm.BitAlgorithms import (
    bit_indices,
    least_significant_bit_index,
    most_significant_bit_index,
    popcount,
    submasks,
    supermasks,
)
from library_codex.algorithm.Doubling import Doubling
from library_codex.algorithm.DynamicProgramming import (
    knapsack_01,
    knapsack_01_max,
    subset_sum_possible,
    subset_sum_restore,
)
from library_codex.algorithm.Fibonacci import fibonacci
from library_codex.algorithm.RangeQueries import Mo
from library_codex.algorithm.Search import (
    binary_search_float,
    binary_search_int,
    kth_element,
)
from library_codex.algorithm.SequenceAlgorithms import (
    coordinate_compress,
    inversion_count,
    longest_increasing_subsequence,
    merge_intervals,
)
from library_codex.algorithm.Sorting import (
    bucket_sort,
    bucket_sort_permutation,
    ensure_permutation,
    permute,
    permute_in_place,
    radix_sort_nonnegative,
)


__all__ = [
    "Doubling",
    "Mo",
    "binary_search_float",
    "binary_search_int",
    "bit_indices",
    "bucket_sort",
    "bucket_sort_permutation",
    "coordinate_compress",
    "ensure_permutation",
    "fibonacci",
    "inversion_count",
    "knapsack_01",
    "knapsack_01_max",
    "kth_element",
    "least_significant_bit_index",
    "longest_increasing_subsequence",
    "merge_intervals",
    "most_significant_bit_index",
    "permute",
    "permute_in_place",
    "popcount",
    "radix_sort_nonnegative",
    "submasks",
    "subset_sum_possible",
    "subset_sum_restore",
    "supermasks",
]
