"""Compatibility imports for the former miscellaneous algorithm module."""

from library_codex.combinatorics.ErdosGinzburgZiv import erdos_ginzburg_ziv_indices
from library_codex.combinatorics.IntegerPartitions import (
    integer_partitions,
    integer_partitions_up_to,
)
from library_codex.algorithm.ModularProgression import (
    split_mod_progression,
)


__all__ = [
    "erdos_ginzburg_ziv_indices",
    "integer_partitions",
    "integer_partitions_up_to",
    "split_mod_progression",
]
