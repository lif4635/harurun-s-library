import importlib


def test_short_canonical_api_names_replace_long_aliases():
    cases = {
        "library_codex.algorithm.BitAlgorithms": (
            ("msb_index", "lsb_index"),
            ("most_significant_bit_index", "least_significant_bit_index"),
        ),
        "library_codex.algorithm.SequenceAlgorithms": (
            ("lis",),
            ("longest_increasing_subsequence",),
        ),
        "library_codex.combinatorics.Combination": (
            ("Comb", "comb"),
            ("Combination", "comb_large"),
        ),
        "library_codex.combinatorics.BinomialQueries": (
            ("comb_prefix_sums",),
            ("multipoint_binomial_prefix_sum", "multipoint_binomial_sum"),
        ),
        "library_codex.segment_tree.SegTree": (
            ("SegTree",),
            ("SegmentTree",),
        ),
        "library_codex.segment_tree.LazySegTree": (
            ("LazySegTree",),
            ("LazySegmentTree",),
        ),
        "library_codex.segment_tree.DualSegTree": (
            ("DualSegTree",),
            ("DualSegmentTree",),
        ),
        "library_codex.fps.IncreasingSequences": (
            ("count_increasing_sequences",),
            (
                "number_of_increasing_sequences_between",
                "NumberofIncreasingSequencesBetweenTwoSequences",
            ),
        ),
        "library_codex.graph_connectivity.StronglyConnectedComponents": (
            ("SCC", "scc"),
            ("StronglyConnectedComponents", "strongly_connected_components"),
        ),
        "library_codex.tree.TreeDistanceFrequency": (
            ("tree_distance_counts",),
            ("frequency_table_of_tree_distance", "FrequencyTableOfTreeDistance"),
        ),
    }
    for module_name, (current, removed) in cases.items():
        module = importlib.import_module(module_name)
        assert all(hasattr(module, name) for name in current)
        assert all(not hasattr(module, name) for name in removed)


def test_combination_variants_use_one_method_name():
    arbitrary = importlib.import_module(
        "library_codex.combinatorics.ArbitraryBinomial"
    )
    q_binomial = importlib.import_module("library_codex.combinatorics.QBinomial")
    for cls in (
        arbitrary.LargePrimeFactorial,
        arbitrary.PrimePowerBinomial,
        arbitrary.ArbitraryModBinomial,
        q_binomial.QBinomial,
    ):
        assert hasattr(cls, "C")
        assert not hasattr(cls, "binomial")
        assert not hasattr(cls, "nCr")
