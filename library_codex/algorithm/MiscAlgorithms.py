"""Compatibility imports for the former miscellaneous algorithm module."""

from library_codex.algorithm.ErdosGinzburgZiv import erdos_ginzburg_ziv_indices
from library_codex.algorithm.IntegerPartitions import (
    integer_partitions,
    integer_partitions_up_to,
)
from library_codex.algorithm.IntegerUtilities import (
    decimal_digit_count,
    exact_square_root,
    modular_power,
    nearest_congruent_at_least,
)
from library_codex.algorithm.ModularProgression import (
    split_modular_arithmetic_progression,
)


__all__ = [
    "decimal_digit_count",
    "erdos_ginzburg_ziv_indices",
    "exact_square_root",
    "integer_partitions",
    "integer_partitions_up_to",
    "modular_power",
    "nearest_congruent_at_least",
    "split_modular_arithmetic_progression",
]
