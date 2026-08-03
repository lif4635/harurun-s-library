from pathlib import Path


SOURCES = (
    (
        "NachiaVivias/cp-library",
        Path("/tmp/codex-cplib-nachia/Cpp/Include/nachia"),
        ".hpp",
    ),
    (
        "tko919/library",
        Path("/tmp/codex-cplib-tko"),
        ".hpp",
    ),
    (
        "NyaanNyaan/library",
        Path("/tmp/codex-cplib-nyaan"),
        ".hpp",
    ),
    (
        "kemuniku/cplib",
        Path("/tmp/codex-cplib-kemuniku/src/cplib"),
        ".nim",
    ),
)

EXCLUDED_PARTS = {
    ".git",
    ".github",
    "Verify",
    "verify",
    "docs",
    "unused",
}

SUPPORT_CATEGORIES = {
    "atcoder",
    "develop",
    "internal",
    "modint",
    "old",
    "Template",
    "template",
    "tmpl",
}

# Language/runtime scaffolding that has no standalone PyPy algorithm to port.
# Keeping this explicit prevents utility headers from being mistaken for an
# unfinished mathematical feature.
SUPPORT_FILES = {
    ("NachiaVivias/cp-library", "array/csr-array.hpp"),
    ("NachiaVivias/cp-library", "graph/graph.hpp"),
    ("NachiaVivias/cp-library", "math-modulo/static-modint.hpp"),
    ("NachiaVivias/cp-library", "misc/fastio.hpp"),
    ("NachiaVivias/cp-library", "modulo/static-modint.hpp"),
    ("tko919/library", "Math/algebra.hpp"),
    ("tko919/library", "Math/bigint.hpp"),
    ("tko919/library", "Math/dynamic.hpp"),
    ("tko919/library", "Math/fastdiv.hpp"),
    ("tko919/library", "Math/hash.hpp"),
    ("tko919/library", "Math/modint.hpp"),
    ("tko919/library", "Utility/fastio.hpp"),
    ("tko919/library", "Utility/random.hpp"),
    ("tko919/library", "Utility/timer.hpp"),
    ("tko919/library", "Utility/visualizer.hpp"),
    ("NyaanNyaan/library", "graph/graph-template.hpp"),
    ("NyaanNyaan/library", "graph/static-graph.hpp"),
    ("NyaanNyaan/library", "math/bigint-all.hpp"),
    ("NyaanNyaan/library", "math/bigint-binary.hpp"),
    ("NyaanNyaan/library", "math/bigint-garner.hpp"),
    ("NyaanNyaan/library", "math/bigint-gcd.hpp"),
    ("NyaanNyaan/library", "math/bigint-rational.hpp"),
    ("NyaanNyaan/library", "math/bigint-to-hex.hpp"),
    ("NyaanNyaan/library", "math/bigint.hpp"),
    ("NyaanNyaan/library", "math-fast/vectorize-modint.hpp"),
    ("NyaanNyaan/library", "misc/all.hpp"),
    ("NyaanNyaan/library", "misc/fastio.hpp"),
    ("NyaanNyaan/library", "misc/rng.hpp"),
    ("NyaanNyaan/library", "misc/simd.hpp"),
    ("NyaanNyaan/library", "misc/timer.hpp"),
    ("NyaanNyaan/library", "misc/vector-pool.hpp"),
    ("kemuniku/cplib", "graph/graph.nim"),
    ("kemuniku/cplib", "graph/graph_debug.nim"),
    ("kemuniku/cplib", "math/baser.nim"),
    ("kemuniku/cplib", "math/float128.nim"),
    ("kemuniku/cplib", "math/inner_math.nim"),
    ("kemuniku/cplib", "math/int128.nim"),
    ("kemuniku/cplib", "utils/constants.nim"),
    ("kemuniku/cplib", "utils/itertools.nim"),
    ("kemuniku/cplib", "utils/list_procs.nim"),
    ("kemuniku/cplib", "utils/memo.nim"),
    ("kemuniku/cplib", "utils/random_helper.nim"),
    ("kemuniku/cplib", "utils/seqidx.nim"),
    ("kemuniku/cplib", "utils/sequtils2D.nim"),
}

# Geometry explicitly deferred by the user, including upstream files placed in
# non-geometry directories.
DEFERRED_GEOMETRY_FILES = {
    ("NyaanNyaan/library", "math/enumerate-convex.hpp"),
    ("NyaanNyaan/library", "shortest-path/dual-of-shortest-path.hpp"),
}

COVERED = {
    (
        "NachiaVivias/cp-library",
        "array/divisor-convolution.hpp",
    ): "arithmetic_convolution/ArithmeticConvolution.py",
    (
        "NachiaVivias/cp-library",
        "array/convex-min-plus-convolution.hpp",
    ): "optimization/Optimization.py",
    (
        "NachiaVivias/cp-library",
        "bit-convolution/set-power-series-power-projection.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "NachiaVivias/cp-library",
        "math/floor-of-kth-root.hpp",
    ): "number_theory/ModularRoot.py",
    (
        "NachiaVivias/cp-library",
        "linear-modulo/characteristic-polynomial.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NachiaVivias/cp-library",
        "linear-modulo/linear-equation.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NachiaVivias/cp-library",
        "linear-modulo/matrix-modulo.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NachiaVivias/cp-library",
        "graph/dynamic-connectivity.hpp",
    ): "graph_connectivity/OnlineDynamicConnectivity.py",
    (
        "NachiaVivias/cp-library",
        "tree/static-top-tree.hpp",
    ): "tree/StaticTopTree.py",
    (
        "tko919/library",
        "Convolution/divisor.hpp",
    ): "arithmetic_convolution/ArithmeticConvolution.py",
    (
        "tko919/library",
        "Algorithm/kprojectselection.hpp",
    ): "optimization/ProjectSelection.py",
    (
        "tko919/library",
        "Algorithm/monotoneminima.hpp",
    ): "optimization/Optimization.py",
    (
        "tko919/library",
        "Algorithm/projectselection.hpp",
    ): "optimization/ProjectSelection.py",
    (
        "tko919/library",
        "Convolution/convexminplus.hpp",
    ): "optimization/Optimization.py",
    (
        "tko919/library",
        "DataStructure/chtmonotone.hpp",
    ): "optimization/Optimization.py",
    (
        "tko919/library",
        "DataStructure/slopetrick.hpp",
    ): "optimization/SlopeTrick.py",
    (
        "tko919/library",
        "Convolution/subset.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "tko919/library",
        "Graph/bimatching.hpp",
    ): "graph_matching/BipartiteMatching.py",
    (
        "tko919/library",
        "Graph/linkcut.hpp",
    ): "tree/LinkCutTree.py",
    (
        "tko919/library",
        "Graph/statictoptree.hpp",
    ): "tree/StaticTopTree.py",
    (
        "tko919/library",
        "Graph/maxflow.hpp",
    ): "graph_flow/MaxFlow.py",
    (
        "tko919/library",
        "Graph/mincostflow.hpp",
    ): "graph_flow/MinCostBFlow.py",
    (
        "tko919/library",
        "Math/kthroot.hpp",
    ): "number_theory/ModularRoot.py",
    (
        "tko919/library",
        "Math/bbla.hpp",
    ): "linear_algebra/BlackBoxLinearAlgebra.py",
    (
        "tko919/library",
        "Math/charpoly.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "tko919/library",
        "Math/detaplusbx.hpp",
    ): "linear_algebra/PolynomialMatrix.py",
    (
        "tko919/library",
        "Math/gaussian.hpp",
    ): "math/NumberTheoryExtras.py",
    (
        "tko919/library",
        "Math/hafnian.hpp",
    ): "linear_algebra/AdvancedMatrix.py",
    (
        "tko919/library",
        "Math/linearequation.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "tko919/library",
        "Math/matrix.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "tko919/library",
        "Math/pfaffian.hpp",
    ): "linear_algebra/AdvancedMatrix.py",
    (
        "tko919/library",
        "Math/primitive.hpp",
    ): "number_theory/ModularRoot.py",
    (
        "tko919/library",
        "FPS/composition.hpp",
    ): "fps/PolynomialComposition.py",
    (
        "tko919/library",
        "FPS/compinv.hpp",
    ): "fps/PolynomialComposition.py",
    (
        "NyaanNyaan/library",
        "fps/fps-composition.hpp",
    ): "fps/PolynomialComposition.py",
    (
        "NyaanNyaan/library",
        "flow/flow-on-bipartite-graph.hpp",
    ): "graph_matching/BipartiteMatching.py",
    (
        "NyaanNyaan/library",
        "data-structure/line-container.hpp",
    ): "optimization/Optimization.py",
    (
        "NyaanNyaan/library",
        "data-structure/slope-trick.hpp",
    ): "optimization/SlopeTrick.py",
    (
        "NyaanNyaan/library",
        "data-structure/slope-trick-weighted.hpp",
    ): "optimization/SlopeTrick.py",
    (
        "NyaanNyaan/library",
        "dp/golden-section-search.hpp",
    ): "optimization/Optimization.py",
    (
        "NyaanNyaan/library",
        "dp/maximal-rectangle.hpp",
    ): "optimization/Optimization.py",
    (
        "NyaanNyaan/library",
        "dp/monotone-minima.hpp",
    ): "optimization/Optimization.py",
    (
        "NyaanNyaan/library",
        "fps/fps-composition-old.hpp",
    ): "fps/PolynomialComposition.py",
    (
        "NyaanNyaan/library",
        "fps/fps-compositional-inverse.hpp",
    ): "fps/PolynomialComposition.py",
    (
        "NyaanNyaan/library",
        "fps/fps-sqrt.hpp",
    ): "fps/FormalPowerSeries.py",
    (
        "NyaanNyaan/library",
        "fps/sample-point-shift.hpp",
    ): "polynomial/MultipointEvaluation.py",
    (
        "NyaanNyaan/library",
        "math-fast/subset-convolution.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "NyaanNyaan/library",
        "math/constexpr-primitive-root.hpp",
    ): "number_theory/ModularRoot.py",
    (
        "NyaanNyaan/library",
        "math/isqrt.hpp",
    ): "number_theory/ModularRoot.py",
    (
        "NyaanNyaan/library",
        "math/kth-root-integral.hpp",
    ): "number_theory/ModularRoot.py",
    (
        "NyaanNyaan/library",
        "math/primitive-root-ll.hpp",
    ): "number_theory/ModularRoot.py",
    (
        "NyaanNyaan/library",
        "matrix/black-box-linear-algebra.hpp",
    ): "linear_algebra/BlackBoxLinearAlgebra.py",
    (
        "NyaanNyaan/library",
        "matrix/characteristric-polynomial.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NyaanNyaan/library",
        "matrix/determinant-arbitrary-mod.hpp",
    ): "linear_algebra/AdvancedMatrix.py",
    (
        "NyaanNyaan/library",
        "matrix/f2-matrix.hpp",
    ): "linear_algebra/F2Matrix.py",
    (
        "NyaanNyaan/library",
        "matrix/gauss-elimination.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NyaanNyaan/library",
        "matrix/hafnian.hpp",
    ): "linear_algebra/AdvancedMatrix.py",
    (
        "NyaanNyaan/library",
        "matrix/inverse-matrix.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NyaanNyaan/library",
        "matrix/linear-equation.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NyaanNyaan/library",
        "matrix/linear-equation-hashmap.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NyaanNyaan/library",
        "matrix/matrix-tree.hpp",
    ): "linear_algebra/PolynomialMatrix.py",
    (
        "NyaanNyaan/library",
        "matrix/matrix.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NyaanNyaan/library",
        "matrix/matrix-fast.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NyaanNyaan/library",
        "matrix/polynomial-matrix-determinant.hpp",
    ): "linear_algebra/PolynomialMatrix.py",
    (
        "NyaanNyaan/library",
        "matrix/polynomial-matrix-prefix-prod.hpp",
    ): "linear_algebra/PolynomialMatrix.py",
    (
        "NyaanNyaan/library",
        "graph/offline-dynamic-connectivity.hpp",
    ): "graph_connectivity/OfflineDynamicConnectivity.py",
    (
        "NyaanNyaan/library",
        "lct/link-cut-base.hpp",
    ): "tree/LinkCutTree.py",
    (
        "NyaanNyaan/library",
        "lct/link-cut-tree.hpp",
    ): "tree/LinkCutTree.py",
    (
        "NyaanNyaan/library",
        "lct/link-cut-tree-lazy.hpp",
    ): "tree/LinkCutTree.py",
    (
        "NyaanNyaan/library",
        "lct/link-cut-tree-subtree.hpp",
    ): "tree/LinkCutTree.py",
    (
        "NyaanNyaan/library",
        "lct/link-cut-tree-subtree-add.hpp",
    ): "tree/LinkCutTree.py",
    (
        "NyaanNyaan/library",
        "multiplicative-function/divisor-multiple-transform.hpp",
    ): "arithmetic_convolution/ArithmeticConvolution.py",
    (
        "NyaanNyaan/library",
        "multiplicative-function/gcd-convolution.hpp",
    ): "arithmetic_convolution/ArithmeticConvolution.py",
    (
        "NyaanNyaan/library",
        "modulo/mod-kth-root.hpp",
    ): "number_theory/ModularRoot.py",
    (
        "NyaanNyaan/library",
        "modulo/mod-sqrt.hpp",
    ): "number_theory/ModularArithmetic.py",
    (
        "NyaanNyaan/library",
        "modulo/gauss-elimination-fast.hpp",
    ): "linear_algebra/Matrix.py",
    (
        "NyaanNyaan/library",
        "set-function/and-convolution.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "NyaanNyaan/library",
        "set-function/exp-of-set-power-series.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "NyaanNyaan/library",
        "set-function/or-convolution.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "NyaanNyaan/library",
        "set-function/polynomial-composite-set-power-series.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "NyaanNyaan/library",
        "set-function/subset-convolution.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "NyaanNyaan/library",
        "set-function/walsh-hadamard-transform.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "NyaanNyaan/library",
        "set-function/xor-convolution.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "NyaanNyaan/library",
        "set-function/zeta-mobius-transform.hpp",
    ): "bitwise_convolution/SetFunction.py",
    (
        "NyaanNyaan/library",
        "tree/static-top-tree-edge-based.hpp",
    ): "tree/StaticTopTree.py",
    (
        "NyaanNyaan/library",
        "tree/static-top-tree-vertex-based.hpp",
    ): "tree/StaticTopTree.py",
    (
        "kemuniku/cplib",
        "math/isqrt.nim",
    ): "number_theory/ModularRoot.py",
    (
        "kemuniku/cplib",
        "math/primitive_root.nim",
    ): "number_theory/ModularRoot.py",
    (
        "kemuniku/cplib",
        "matrix/matops.nim",
    ): "linear_algebra/Matrix.py",
    (
        "kemuniku/cplib",
        "matrix/matrix.nim",
    ): "linear_algebra/Matrix.py",
    (
        "kemuniku/cplib",
        "matrix/rolling_hash_2d.nim",
    ): "string/RollingHash2D.py",
    (
        "kemuniku/cplib",
        "matrix/static_matrix.nim",
    ): "linear_algebra/Matrix.py",
    (
        "kemuniku/cplib",
        "collections/slopetrick.nim",
    ): "optimization/SlopeTrick.py",
    (
        "NachiaVivias/cp-library",
        "array/cartesian-tree.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "NachiaVivias/cp-library",
        "tree/ahu-algorithm.hpp",
    ): "tree/TreeIsomorphism.py",
    (
        "NachiaVivias/cp-library",
        "tree/centroid-decomposition-binary-tree.hpp",
    ): "tree/CentroidDecomposition.py",
    (
        "NachiaVivias/cp-library",
        "tree/centroid-decomposition.hpp",
    ): "tree/CentroidDecomposition.py",
    (
        "NachiaVivias/cp-library",
        "tree/heavy-light-decomposition.hpp",
    ): "tree/HeavyLightDecomposition.py",
    (
        "NachiaVivias/cp-library",
        "tree/tree-center.hpp",
    ): "tree/TreeIsomorphism.py",
    (
        "NachiaVivias/cp-library",
        "tree/tree-centroid.hpp",
    ): "tree/TreeIsomorphism.py",
    (
        "NachiaVivias/cp-library",
        "tree/tree-diameter.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "NachiaVivias/cp-library",
        "tree/tree-dp.hpp",
    ): "tree/Rerooting.py",
    (
        "tko919/library",
        "Algorithm/cartesian.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "tko919/library",
        "Graph/auxiliarytree.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "tko919/library",
        "Graph/centroid.hpp",
    ): "tree/CentroidDecomposition.py",
    (
        "tko919/library",
        "Graph/cycledetect.hpp",
    ): "graph/CycleDetection.py",
    (
        "tko919/library",
        "Graph/diameter.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "tko919/library",
        "Graph/dmdecomp.hpp",
    ): "graph_matching/BipartiteMatching.py",
    (
        "tko919/library",
        "Graph/euler.hpp",
    ): "graph/EulerianTrail.py",
    (
        "tko919/library",
        "Graph/hld.hpp",
    ): "tree/HeavyLightDecomposition.py",
    (
        "tko919/library",
        "Graph/lca.hpp",
    ): "tree/HeavyLightDecomposition.py",
    (
        "tko919/library",
        "Graph/lowlink.hpp",
    ): "graph_connectivity/LowLink.py",
    (
        "tko919/library",
        "Graph/prufer.hpp",
    ): "tree/PruferCode.py",
    (
        "tko919/library",
        "Graph/rerooting.hpp",
    ): "tree/Rerooting.py",
    (
        "NyaanNyaan/library",
        "tree/auxiliary-tree.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "NyaanNyaan/library",
        "tree/cartesian-tree.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "NyaanNyaan/library",
        "tree/centroid-decomposition.hpp",
    ): "tree/CentroidDecomposition.py",
    (
        "NyaanNyaan/library",
        "tree/centroid.hpp",
    ): "tree/TreeIsomorphism.py",
    (
        "NyaanNyaan/library",
        "tree/convert-tree.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "NyaanNyaan/library",
        "tree/dsu-on-tree.hpp",
    ): "tree/DSUOnTree.py",
    (
        "NyaanNyaan/library",
        "tree/dynamic-diameter.hpp",
    ): "tree/DynamicDiameter.py",
    (
        "NyaanNyaan/library",
        "tree/euler-tour.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "NyaanNyaan/library",
        "tree/heavy-light-decomposition.hpp",
    ): "tree/HeavyLightDecomposition.py",
    (
        "NyaanNyaan/library",
        "tree/inclusion-tree.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "NyaanNyaan/library",
        "tree/process-of-merging-tree.hpp",
    ): "tree/TreeAlgorithms.py",
    (
        "NyaanNyaan/library",
        "tree/pruefer-code.hpp",
    ): "tree/PruferCode.py",
    (
        "NyaanNyaan/library",
        "tree/rerooting.hpp",
    ): "tree/Rerooting.py",
    (
        "NyaanNyaan/library",
        "tree/rooted-tree-hash.hpp",
    ): "tree/TreeIsomorphism.py",
    (
        "NyaanNyaan/library",
        "tree/tree-hash.hpp",
    ): "tree/TreeIsomorphism.py",
    (
        "NyaanNyaan/library",
        "tree/tree-query.hpp",
    ): "tree/HeavyLightDecomposition.py",
    (
        "kemuniku/cplib",
        "tree/cartesiantree.nim",
    ): "tree/TreeAlgorithms.py",
    (
        "kemuniku/cplib",
        "tree/diameter.nim",
    ): "tree/TreeAlgorithms.py",
    (
        "kemuniku/cplib",
        "tree/heavylightdecomposition.nim",
    ): "tree/HeavyLightDecomposition.py",
    (
        "kemuniku/cplib",
        "tree/prufer.nim",
    ): "tree/PruferCode.py",
    (
        "kemuniku/cplib",
        "tree/rerooting.nim",
    ): "tree/Rerooting.py",
    (
        "NachiaVivias/cp-library",
        "array/deque-operate-aggregation.hpp",
    ): "data_structure/SWAG.py",
    (
        "NachiaVivias/cp-library",
        "array/lazy-segtree.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "NachiaVivias/cp-library",
        "array/li-ciao-tree-flexible.hpp",
    ): "spatial_structure/LiChaoTree.py",
    (
        "NachiaVivias/cp-library",
        "array/segtree.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "NachiaVivias/cp-library",
        "array/wavelet-matrix.hpp",
    ): "range_query/WaveletMatrix.py",
    (
        "NachiaVivias/cp-library",
        "range-query/point-set-range-min.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "tko919/library",
        "DataStructure/2dbit.hpp",
    ): "fenwick_tree/FenwickTree.py",
    (
        "tko919/library",
        "DataStructure/bit.hpp",
    ): "fenwick_tree/FenwickTree.py",
    (
        "tko919/library",
        "DataStructure/dequeswag.hpp",
    ): "data_structure/SWAG.py",
    (
        "tko919/library",
        "DataStructure/disjointsparsetable.hpp",
    ): "range_query/DisjointSparseTable.py",
    (
        "tko919/library",
        "DataStructure/dualsegtree.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "tko919/library",
        "DataStructure/fastset.hpp",
    ): "ordered_set/FastSet.py",
    (
        "tko919/library",
        "DataStructure/lazysegtree.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "tko919/library",
        "DataStructure/lichaotree.hpp",
    ): "spatial_structure/LiChaoTree.py",
    (
        "tko919/library",
        "DataStructure/persistentarray.hpp",
    ): "sequence_structure/PersistentArray.py",
    (
        "tko919/library",
        "DataStructure/persistentunionfind.hpp",
    ): "union_find/PersistentUnionFind.py",
    (
        "tko919/library",
        "DataStructure/rollbackunionfind.hpp",
    ): "union_find/RollbackUnionFind.py",
    (
        "tko919/library",
        "DataStructure/segtree.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "tko919/library",
        "DataStructure/segtreebeats.hpp",
    ): "segment_tree/SegmentTreeBeats.py",
    (
        "tko919/library",
        "DataStructure/swag.hpp",
    ): "data_structure/SWAG.py",
    (
        "tko919/library",
        "DataStructure/unionfind.hpp",
    ): "union_find/UnionFind.py",
    (
        "tko919/library",
        "DataStructure/wavelet.hpp",
    ): "range_query/WaveletMatrix.py",
    (
        "tko919/library",
        "DataStructure/weightedunionfind.hpp",
    ): "union_find/UnionFind.py",
    (
        "NyaanNyaan/library",
        "data-structure/binary-indexed-tree.hpp",
    ): "fenwick_tree/FenwickTree.py",
    (
        "NyaanNyaan/library",
        "data-structure/binary-trie.hpp",
    ): "ordered_set/BinaryTrie.py",
    (
        "NyaanNyaan/library",
        "data-structure/dynamic-binary-indexed-tree.hpp",
    ): "fenwick_tree/FenwickTree.py",
    (
        "NyaanNyaan/library",
        "data-structure/dynamic-union-find.hpp",
    ): "union_find/UnionFind.py",
    (
        "NyaanNyaan/library",
        "data-structure/erasable-priority-queue.hpp",
    ): "data_structure/SWAG.py",
    (
        "NyaanNyaan/library",
        "data-structure/persistent-array.hpp",
    ): "sequence_structure/PersistentArray.py",
    (
        "NyaanNyaan/library",
        "data-structure/persistent-union-find.hpp",
    ): "union_find/PersistentUnionFind.py",
    (
        "NyaanNyaan/library",
        "data-structure/radix-heap.hpp",
    ): "sequence_structure/RadixHeap.py",
    (
        "NyaanNyaan/library",
        "data-structure/range-sum-range-add-bit.hpp",
    ): "fenwick_tree/FenwickTree.py",
    (
        "NyaanNyaan/library",
        "data-structure/rollback-union-find.hpp",
    ): "union_find/RollbackUnionFind.py",
    (
        "NyaanNyaan/library",
        "data-structure/slide-window-aggregation-deque.hpp",
    ): "data_structure/SWAG.py",
    (
        "NyaanNyaan/library",
        "data-structure/slide-window-aggregation.hpp",
    ): "data_structure/SWAG.py",
    (
        "NyaanNyaan/library",
        "data-structure/sparse-table.hpp",
    ): "range_query/DisjointSparseTable.py",
    (
        "NyaanNyaan/library",
        "data-structure/union-find-enumerate.hpp",
    ): "union_find/UnionFind.py",
    (
        "NyaanNyaan/library",
        "data-structure/union-find-with-potential.hpp",
    ): "union_find/UnionFind.py",
    (
        "NyaanNyaan/library",
        "data-structure/union-find.hpp",
    ): "union_find/UnionFind.py",
    (
        "NyaanNyaan/library",
        "data-structure/van-emde-boas-tree.hpp",
    ): "ordered_set/FastSet.py",
    (
        "NyaanNyaan/library",
        "data-structure/w-ary-tree.hpp",
    ): "ordered_set/FastSet.py",
    (
        "NyaanNyaan/library",
        "segment-tree/dynamic-li-chao-tree.hpp",
    ): "spatial_structure/LiChaoTree.py",
    (
        "NyaanNyaan/library",
        "segment-tree/li-chao-tree-abstruct.hpp",
    ): "spatial_structure/LiChaoTree.py",
    (
        "NyaanNyaan/library",
        "segment-tree/li-chao-tree.hpp",
    ): "spatial_structure/LiChaoTree.py",
    (
        "NyaanNyaan/library",
        "segment-tree/persistent-segment-tree.hpp",
    ): "segment_tree/PersistentSegmentTree.py",
    (
        "NyaanNyaan/library",
        "segment-tree/segment-tree-beats-abstract.hpp",
    ): "segment_tree/SegmentTreeBeats.py",
    (
        "NyaanNyaan/library",
        "segment-tree/segment-tree-beats.hpp",
    ): "segment_tree/SegmentTreeBeats.py",
    (
        "NyaanNyaan/library",
        "segment-tree/segment-tree.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "kemuniku/cplib",
        "collections/QSWAG.nim",
    ): "data_structure/SWAG.py",
    (
        "kemuniku/cplib",
        "collections/SWAG.nim",
    ): "data_structure/SWAG.py",
    (
        "kemuniku/cplib",
        "collections/binary_trie.nim",
    ): "ordered_set/BinaryTrie.py",
    (
        "kemuniku/cplib",
        "collections/deletable_heapqueue.nim",
    ): "data_structure/SWAG.py",
    (
        "kemuniku/cplib",
        "collections/fenwick2d.nim",
    ): "fenwick_tree/FenwickTree.py",
    (
        "kemuniku/cplib",
        "collections/lazysegtree.nim",
    ): "segment_tree/SegmentTree.py",
    (
        "kemuniku/cplib",
        "collections/lichaotree.nim",
    ): "spatial_structure/LiChaoTree.py",
    (
        "kemuniku/cplib",
        "collections/persistent_array.nim",
    ): "sequence_structure/PersistentArray.py",
    (
        "kemuniku/cplib",
        "collections/persistent_segtree.nim",
    ): "segment_tree/PersistentSegmentTree.py",
    (
        "kemuniku/cplib",
        "collections/persistent_unionfind.nim",
    ): "union_find/PersistentUnionFind.py",
    (
        "kemuniku/cplib",
        "collections/rollback_unionfind.nim",
    ): "union_find/RollbackUnionFind.py",
    (
        "kemuniku/cplib",
        "collections/segtree.nim",
    ): "segment_tree/SegmentTree.py",
    (
        "kemuniku/cplib",
        "collections/segtree_beats.nim",
    ): "segment_tree/SegmentTreeBeats.py",
    (
        "kemuniku/cplib",
        "collections/segtree_beats_template.nim",
    ): "segment_tree/SegmentTreeBeats.py",
    (
        "kemuniku/cplib",
        "collections/staticRMQ.nim",
    ): "range_query/StaticRMQ.py",
    (
        "kemuniku/cplib",
        "collections/tatyamset.nim",
    ): "ordered_set/FastSet.py",
    (
        "kemuniku/cplib",
        "collections/unionfind.nim",
    ): "union_find/UnionFind.py",
    (
        "kemuniku/cplib",
        "collections/waveletmatrix.nim",
    ): "range_query/WaveletMatrix.py",
    (
        "kemuniku/cplib",
        "collections/weightedunionfind.nim",
    ): "union_find/UnionFind.py",
    (
        "kemuniku/cplib",
        "collections/wordsizetree.nim",
    ): "ordered_set/FastSet.py",
    (
        "tko919/library",
        "DataStructure/dynamiclazysegtree.hpp",
    ): "segment_tree/DynamicSegmentTree.py",
    (
        "tko919/library",
        "DataStructure/dynamicsegtree.hpp",
    ): "segment_tree/DynamicSegmentTree.py",
    (
        "tko919/library",
        "DataStructure/persistentlazysegtree.hpp",
    ): "segment_tree/DynamicSegmentTree.py",
    (
        "NyaanNyaan/library",
        "segment-tree/dynamic-segment-tree.hpp",
    ): "segment_tree/DynamicSegmentTree.py",
    (
        "NyaanNyaan/library",
        "segment-tree/lazy-segment-tree-utility.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "NyaanNyaan/library",
        "segment-tree/lazy-segment-tree.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "NyaanNyaan/library",
        "segment-tree/range-weighted-add-range-sum-lazyseg.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "kemuniku/cplib",
        "collections/segtree_var.nim",
    ): "segment_tree/SegmentTree.py",
    (
        "tko919/library",
        "DataStructure/2dsegtree.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "tko919/library",
        "DataStructure/dynamicrectsum.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "tko919/library",
        "DataStructure/staticrectaddrectsum.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "tko919/library",
        "DataStructure/staticrectsum.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "NyaanNyaan/library",
        "data-structure-2d/2d-binary-indexed-tree.hpp",
    ): "fenwick_tree/FenwickTree.py",
    (
        "NyaanNyaan/library",
        "data-structure-2d/2d-cumulative-sum.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "NyaanNyaan/library",
        "data-structure-2d/2d-segment-tree.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "NyaanNyaan/library",
        "data-structure-2d/dynamic-binary-indexed-tree-2d.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "NyaanNyaan/library",
        "data-structure-2d/fenwick-tree-on-range-tree.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "NyaanNyaan/library",
        "data-structure-2d/fenwick-tree-on-wavelet-matrix.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "NyaanNyaan/library",
        "data-structure-2d/rectangle-add-rectangle-sum.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "NyaanNyaan/library",
        "data-structure-2d/rectangle-sum.hpp",
    ): "data_structure/RectangleQuery.py",
    (
        "NyaanNyaan/library",
        "data-structure-2d/wavelet-matrix.hpp",
    ): "range_query/WaveletMatrix.py",
    (
        "tko919/library",
        "DataStructure/hashmap.hpp",
    ): "data_structure/Collections.py",
    (
        "tko919/library",
        "DataStructure/linkedlist.hpp",
    ): "data_structure/Collections.py",
    (
        "tko919/library",
        "DataStructure/pointsetrangefreq.hpp",
    ): "data_structure/Collections.py",
    (
        "tko919/library",
        "DataStructure/rangeparalleluf.hpp",
    ): "union_find/UnionFind.py",
    (
        "tko919/library",
        "DataStructure/rangeunionset.hpp",
    ): "data_structure/Collections.py",
    (
        "tko919/library",
        "DataStructure/rbstset.hpp",
    ): "data_structure/Collections.py",
    (
        "NyaanNyaan/library",
        "data-structure/dynamic-bitset.hpp",
    ): "data_structure/Collections.py",
    (
        "NyaanNyaan/library",
        "data-structure/hash-map-variable-length.hpp",
    ): "data_structure/Collections.py",
    (
        "NyaanNyaan/library",
        "data-structure/parallel-union-find.hpp",
    ): "union_find/UnionFind.py",
    (
        "NyaanNyaan/library",
        "data-structure/persistent-queue.hpp",
    ): "data_structure/Collections.py",
    (
        "NyaanNyaan/library",
        "data-structure/range-union-find.hpp",
    ): "union_find/UnionFind.py",
    (
        "NyaanNyaan/library",
        "data-structure/segment-set.hpp",
    ): "data_structure/Collections.py",
    (
        "NyaanNyaan/library",
        "data-structure/sliding-window-minimum.hpp",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/avlset.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/avlset_old.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/avltreenode.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/avltreenode_old.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/bitset.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/bitvector.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/defaultdict.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/group_unionfind.nim",
    ): "union_find/UnionFind.py",
    (
        "kemuniku/cplib",
        "collections/hashset.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/hashtable.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/persistent_binary_trie.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/ppunionfind.nim",
    ): "union_find/UnionFind.py",
    (
        "kemuniku/cplib",
        "collections/rangeset.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/raw_ptr_avlset.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/root_rangesum.nim",
    ): "segment_tree/SegmentTree.py",
    (
        "kemuniku/cplib",
        "collections/rootvalue_unionfind.nim",
    ): "union_find/UnionFind.py",
    (
        "kemuniku/cplib",
        "collections/staticbitset.nim",
    ): "data_structure/Collections.py",
    (
        "kemuniku/cplib",
        "collections/topk_sum_heapq.nim",
    ): "data_structure/Collections.py",
    (
        "NachiaVivias/cp-library",
        "array/bbst-list.hpp",
    ): "sequence_structure/ImplicitTreap.py",
    (
        "NyaanNyaan/library",
        "data-structure/divide-interval.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "NyaanNyaan/library",
        "data-structure/square-root-decomposition.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "NyaanNyaan/library",
        "segment-tree/rbst-segment-tree.hpp",
    ): "sequence_structure/ImplicitTreap.py",
    (
        "NyaanNyaan/library",
        "segment-tree/rbst-sequence.hpp",
    ): "sequence_structure/ImplicitTreap.py",
    (
        "NyaanNyaan/library",
        "segment-tree/segment-tree-max-of-interval.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "kemuniku/cplib",
        "collections/range_reverse_array.nim",
    ): "sequence_structure/ImplicitTreap.py",
    (
        "kemuniku/cplib",
        "collections/range_reverse_array_monoid.nim",
    ): "sequence_structure/ImplicitTreap.py",
    (
        "kemuniku/cplib",
        "collections/range_reverse_dualsegtree.nim",
    ): "sequence_structure/ImplicitTreap.py",
    (
        "kemuniku/cplib",
        "collections/range_reverse_lazysegtree.nim",
    ): "sequence_structure/ImplicitTreap.py",
    (
        "kemuniku/cplib",
        "collections/segtree2d.nim",
    ): "data_structure/RectangleQuery.py",
    (
        "kemuniku/cplib",
        "collections/staticrangecount.nim",
    ): "range_query/WaveletMatrix.py",
    (
        "NachiaVivias/cp-library",
        "graph/connected-components.hpp",
    ): "graph/ShortestPath.py",
    (
        "NachiaVivias/cp-library",
        "graph/dijkstra.hpp",
    ): "graph/ShortestPath.py",
    (
        "NachiaVivias/cp-library",
        "graph/eulerian-trail.hpp",
    ): "graph/EulerianTrail.py",
    (
        "NachiaVivias/cp-library",
        "graph/strongly-connected-components.hpp",
    ): "graph_connectivity/StronglyConnectedComponents.py",
    (
        "NachiaVivias/cp-library",
        "graph/two-edge-connected-components.hpp",
    ): "graph_connectivity/TwoEdgeConnectedComponents.py",
    (
        "tko919/library",
        "Graph/scc.hpp",
    ): "graph_connectivity/StronglyConnectedComponents.py",
    (
        "NyaanNyaan/library",
        "graph/cycle-detection.hpp",
    ): "graph/CycleDetection.py",
    (
        "NyaanNyaan/library",
        "graph/functional-graph.hpp",
    ): "graph_connectivity/FunctionalGraph.py",
    (
        "NyaanNyaan/library",
        "graph/graph-utility.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "graph/kruskal.hpp",
    ): "graph_spanning/MinimumSpanningTree.py",
    (
        "NyaanNyaan/library",
        "graph/lowlink.hpp",
    ): "graph_connectivity/LowLink.py",
    (
        "NyaanNyaan/library",
        "graph/namori.hpp",
    ): "graph_connectivity/NamoriDecomposition.py",
    (
        "NyaanNyaan/library",
        "graph/strongly-connected-components.hpp",
    ): "graph_connectivity/StronglyConnectedComponents.py",
    (
        "NyaanNyaan/library",
        "graph/topological-sort.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "graph/two-edge-connected-components.hpp",
    ): "graph_connectivity/TwoEdgeConnectedComponents.py",
    (
        "NyaanNyaan/library",
        "lct/lazy-reversible-bbst-base.hpp",
    ): "tree/LinkCutTree.py",
    (
        "NyaanNyaan/library",
        "lct/reversible-bbst-base.hpp",
    ): "tree/LinkCutTree.py",
    (
        "NyaanNyaan/library",
        "lct/splay-base.hpp",
    ): "tree/LinkCutTree.py",
    (
        "NyaanNyaan/library",
        "lct/splay-lazy-reversible.hpp",
    ): "tree/LinkCutTree.py",
    (
        "NyaanNyaan/library",
        "lct/splay-reversible.hpp",
    ): "tree/LinkCutTree.py",
    (
        "NyaanNyaan/library",
        "shortest-path/bellman-ford.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "shortest-path/bfs-restore.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "shortest-path/bfs01.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "shortest-path/dijkstra-abstruct.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "shortest-path/dijkstra-fast.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "shortest-path/dijkstra-radix-heap.hpp",
    ): "shortest_path/DijkstraRadixHeap.py",
    (
        "NyaanNyaan/library",
        "shortest-path/dijkstra-with-restore.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "shortest-path/dijkstra.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "shortest-path/restore-shortest-path.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "shortest-path/warshall-floyd.hpp",
    ): "graph/ShortestPath.py",
    (
        "kemuniku/cplib",
        "graph/SCC.nim",
    ): "graph_connectivity/StronglyConnectedComponents.py",
    (
        "kemuniku/cplib",
        "graph/bellmanford.nim",
    ): "graph/ShortestPath.py",
    (
        "kemuniku/cplib",
        "graph/bipartite_graph.nim",
    ): "graph/ShortestPath.py",
    (
        "kemuniku/cplib",
        "graph/dijkstra.nim",
    ): "graph/ShortestPath.py",
    (
        "kemuniku/cplib",
        "graph/functional_graph.nim",
    ): "graph_connectivity/FunctionalGraph.py",
    (
        "kemuniku/cplib",
        "graph/kruskal.nim",
    ): "graph_spanning/MinimumSpanningTree.py",
    (
        "kemuniku/cplib",
        "graph/namori_forest.nim",
    ): "graph_connectivity/NamoriDecomposition.py",
    (
        "kemuniku/cplib",
        "graph/namori_graph.nim",
    ): "graph_connectivity/NamoriDecomposition.py",
    (
        "kemuniku/cplib",
        "graph/restore_shortest_path_from_prev.nim",
    ): "graph/ShortestPath.py",
    (
        "kemuniku/cplib",
        "graph/topologicalsort.nim",
    ): "graph/ShortestPath.py",
    (
        "kemuniku/cplib",
        "graph/warshall_floyd.nim",
    ): "graph/ShortestPath.py",
    (
        "NachiaVivias/cp-library",
        "graph/biconnected-components.hpp",
    ): "graph_connectivity/BiconnectedComponents.py",
    (
        "tko919/library",
        "Graph/blockcut.hpp",
    ): "graph_connectivity/BiconnectedComponents.py",
    (
        "NyaanNyaan/library",
        "graph/biconnected-components.hpp",
    ): "graph_connectivity/BiconnectedComponents.py",
    (
        "NyaanNyaan/library",
        "tree/block-cut-tree.hpp",
    ): "graph_connectivity/BiconnectedComponents.py",
    (
        "NachiaVivias/cp-library",
        "graph/chromatic-number.hpp",
    ): "graph/GraphEnumeration.py",
    (
        "NachiaVivias/cp-library",
        "graph/count-c4.hpp",
    ): "graph/GraphEnumeration.py",
    (
        "tko919/library",
        "Graph/chromatic.hpp",
    ): "graph/GraphEnumeration.py",
    (
        "tko919/library",
        "Graph/enumcliques.hpp",
    ): "graph/GraphEnumeration.py",
    (
        "tko919/library",
        "Graph/enumtriangle.hpp",
    ): "graph/GraphEnumeration.py",
    (
        "tko919/library",
        "Graph/maxindependentset.hpp",
    ): "graph/GraphEnumeration.py",
    (
        "NyaanNyaan/library",
        "graph/chromatic-number.hpp",
    ): "graph/GraphEnumeration.py",
    (
        "NyaanNyaan/library",
        "graph/max-independent-set.hpp",
    ): "graph/GraphEnumeration.py",
    (
        "NachiaVivias/cp-library",
        "graph/bipartite-edge-coloring.hpp",
    ): "graph_enumeration/GraphProperties.py",
    (
        "NachiaVivias/cp-library",
        "graph/chordal-graph-recognizer.hpp",
    ): "graph_enumeration/GraphProperties.py",
    (
        "NachiaVivias/cp-library",
        "graph/k-shortest-path-directed.hpp",
    ): "shortest_path/KShortestPaths.py",
    (
        "NachiaVivias/cp-library",
        "graph/k-shortest-path-undirected.hpp",
    ): "shortest_path/KShortestPaths.py",
    (
        "tko919/library",
        "Graph/edgecoloring.hpp",
    ): "graph_enumeration/GraphProperties.py",
    (
        "tko919/library",
        "Graph/hungarian.hpp",
    ): "graph/GraphOptimization.py",
    (
        "tko919/library",
        "Graph/steiner.hpp",
    ): "graph/GraphOptimization.py",
    (
        "NyaanNyaan/library",
        "graph/minimum-cost-arborescence.hpp",
    ): "graph/GraphOptimization.py",
    (
        "kemuniku/cplib",
        "graph/maxk_dijkstra.nim",
    ): "graph/GraphOptimization.py",
    (
        "kemuniku/cplib",
        "graph/steiner_tree.nim",
    ): "graph/GraphOptimization.py",
    (
        "kemuniku/cplib",
        "graph/tsp.nim",
    ): "graph/GraphOptimization.py",
    (
        "tko919/library",
        "Graph/general.hpp",
    ): "graph/GraphMatching.py",
    (
        "tko919/library",
        "Math/twosat.hpp",
    ): "graph/GraphMatching.py",
    (
        "NyaanNyaan/library",
        "math/two-sat.hpp",
    ): "graph/GraphMatching.py",
    (
        "kemuniku/cplib",
        "graph/dag_minimum_path_cover.nim",
    ): "graph/GraphMatching.py",
    (
        "kemuniku/cplib",
        "graph/dynamic_bipartite.nim",
    ): "graph/GraphMatching.py",
    (
        "NyaanNyaan/library",
        "graph/dimension-expanded-graph.hpp",
    ): "graph/ExpandedGraph.py",
    (
        "kemuniku/cplib",
        "graph/grid_to_graph.nim",
    ): "graph/ExpandedGraph.py",
    (
        "kemuniku/cplib",
        "graph/range_edge_graph.nim",
    ): "graph/ExpandedGraph.py",
    (
        "kemuniku/cplib",
        "graph/reverse_edge.nim",
    ): "graph/ExpandedGraph.py",
    (
        "NachiaVivias/cp-library",
        "counting/chromatic-polynomial.hpp",
    ): "graph_enumeration/GraphCounting.py",
    (
        "NachiaVivias/cp-library",
        "counting/directed-spanning-trees.hpp",
    ): "graph_enumeration/GraphCounting.py",
    (
        "NachiaVivias/cp-library",
        "counting/euler-cycles.hpp",
    ): "graph_enumeration/GraphCounting.py",
    (
        "tko919/library",
        "Graph/chromaticpoly.hpp",
    ): "graph_enumeration/GraphCounting.py",
    (
        "tko919/library",
        "Graph/counteuler.hpp",
    ): "graph_enumeration/GraphCounting.py",
    (
        "tko919/library",
        "Graph/countspanning.hpp",
    ): "graph_enumeration/GraphCounting.py",
    (
        "NachiaVivias/cp-library",
        "graph/dfs-tree.hpp",
    ): "graph/ShortestPath.py",
    (
        "NyaanNyaan/library",
        "tree/frequency-table-of-tree-distance.hpp",
    ): "tree/TreeDistanceFrequency.py",
    (
        "tko919/library",
        "Graph/contour.hpp",
    ): "tree/CentroidDecomposition.py",
    (
        "tko919/library",
        "Graph/bipolar.hpp",
    ): "graph_spanning/GraphOrdering.py",
    (
        "tko919/library",
        "Graph/opttoposort.hpp",
    ): "graph_spanning/GraphOrdering.py",
    (
        "tko919/library",
        "Graph/shortestpathremedge.hpp",
    ): "graph_spanning/GraphOrdering.py",
    (
        "NachiaVivias/cp-library",
        "graph/incremental-scc-offline.hpp",
    ): "graph_connectivity/AdvancedConnectivity.py",
    (
        "NachiaVivias/cp-library",
        "graph/three-edge-connected-components.hpp",
    ): "graph_connectivity/AdvancedConnectivity.py",
    # Equivalent string implementations across the four reference libraries.
    **{
        ("tko919/library", path): target
        for path, target in {
            "String/ahocorasick.hpp": "string/AhoCorasick.py",
            "String/manacher.hpp": "string/Manacher.py",
            "String/palindromictree.hpp": "string/PalindromicTree.py",
            "String/prefixsubstrlcs.hpp": "string/PrefixSubstringLCS.py",
            "String/rollinghash.hpp": "string/RollingHash.py",
            "String/suffixarray.hpp": "string/SuffixArray.py",
            "String/suffixautomaton.hpp": "string/SuffixAutomaton.py",
            "String/trie.hpp": "string/Trie.py",
            "String/zalgo.hpp": "string/ZAlgorithm.py",
            "Algorithm/wildcardpatternmatching.hpp": "string/WildcardPatternMatching.py",
        }.items()
    },
    **{
        ("NyaanNyaan/library", path): target
        for path, target in {
            "string/aho-corasick.hpp": "string/AhoCorasick.py",
            "string/manacher.hpp": "string/Manacher.py",
            "string/number-of-subsequences.hpp": "string/Subsequence.py",
            "string/rolling-hash-2d.hpp": "string/RollingHash2D.py",
            "string/rolling-hash-on-segment-tree.hpp": "string/DynamicRollingHash.py",
            "string/rolling-hash.hpp": "string/RollingHash.py",
            "string/run-enumerate.hpp": "string/RunEnumeration.py",
            "string/run-length-encoding.hpp": "string/RunLengthEncoding.py",
            "string/string-search.hpp": "string/StringSearch.py",
            "string/suffix-array.hpp": "string/SuffixArray.py",
            "string/suffix-automaton.hpp": "string/SuffixAutomaton.py",
            "string/trie.hpp": "string/Trie.py",
            "string/wildcard-pattern-matching.hpp": "string/WildcardPatternMatching.py",
            "string/z-algorithm.hpp": "string/ZAlgorithm.py",
        }.items()
    },
    **{
        ("kemuniku/cplib", path): target
        for path, target in {
            "str/can_reverse_hash_string.nim": "string/RollingHash.py",
            "str/compressed_trie.nim": "string/CompressedTrie.py",
            "str/hash_string.nim": "string/RollingHash.py",
            "str/lcp_naive.nim": "string/StringSearch.py",
            "str/lcs.nim": "string/LongestCommonSubsequence.py",
            "str/manacher.nim": "string/Manacher.py",
            "str/merged_static_string.nim": "string/StaticString.py",
            "str/palindromic_tree.nim": "string/PalindromicTree.py",
            "str/rolling_hash.nim": "string/RollingHash.py",
            "str/run_length_encode.nim": "string/RunLengthEncoding.py",
            "str/static_string.nim": "string/StaticString.py",
            "str/zalgorithm.nim": "string/ZAlgorithm.py",
        }.items()
    },
    # Convolution backends with the same public mathematical operation.
    **{
        ("tko919/library", path): target
        for path, target in {
            "Convolution/arbitrary.hpp": "convolution/NTT.py",
            "Convolution/bitwise.hpp": "bitwise_convolution/SetFunction.py",
            "Convolution/fft.hpp": "convolution/NTT.py",
            "Convolution/ntt.hpp": "convolution/NTT.py",
        }.items()
    },
    **{
        ("NyaanNyaan/library", path): "convolution/NTT.py"
        for path in (
            "ntt/arbitrary-ntt-mod18446744069414584321.hpp",
            "ntt/arbitrary-ntt.hpp",
            "ntt/complex-fft.hpp",
            "ntt/convolution-large.hpp",
            "ntt/cooley-tukey-ntt.hpp",
            "ntt/karatsuba.hpp",
            "ntt/ntt-64bit.hpp",
            "ntt/ntt-avx2.hpp",
            "ntt/ntt-cpp11.hpp",
            "ntt/ntt-sse42.hpp",
            "ntt/ntt.hpp",
        )
    },
    **{
        ("kemuniku/cplib", path): target
        for path, target in {
            "convolution/convolution.nim": "convolution/NTT.py",
            "convolution/ntt.nim": "convolution/NTT.py",
            "convolution/xor_convolution.nim": "bitwise_convolution/SetFunction.py",
        }.items()
    },
    # FPS core, recurrence, evaluation and interpolation equivalents.
    **{
        ("tko919/library", path): target
        for path, target in {
            "FPS/arbitraryfps.hpp": "fps/FormalPowerSeries.py",
            "FPS/berlekampmassey.hpp": "combinatorial_series/LinearRecurrence.py",
            "FPS/fps.hpp": "fps/FormalPowerSeries.py",
            "FPS/interpolate.hpp": "polynomial/MultipointEvaluation.py",
            "FPS/multieval.hpp": "polynomial/MultipointEvaluation.py",
            "FPS/nthterm.hpp": "combinatorial_series/LinearRecurrence.py",
            "FPS/prodofpolys.hpp": "fps/FormalPowerSeries.py",
            "FPS/samplepointshift.hpp": "polynomial/MultipointEvaluation.py",
        }.items()
    },
    **{
        ("NyaanNyaan/library", path): target
        for path, target in {
            "fps/arbitrary-fps.hpp": "fps/FormalPowerSeries.py",
            "fps/berlekamp-massey.hpp": "combinatorial_series/LinearRecurrence.py",
            "fps/fast-interpolate.hpp": "polynomial/MultipointEvaluation.py",
            "fps/fast-multieval.hpp": "polynomial/MultipointEvaluation.py",
            "fps/formal-power-series.hpp": "fps/FormalPowerSeries.py",
            "fps/fps-utility.hpp": "fps/FormalPowerSeries.py",
            "fps/kitamasa.hpp": "combinatorial_series/LinearRecurrence.py",
            "fps/lagrange-interpolation-point.hpp": "polynomial/MultipointEvaluation.py",
            "fps/multipoint-evaluation.hpp": "polynomial/MultipointEvaluation.py",
            "fps/nth-term.hpp": "combinatorial_series/LinearRecurrence.py",
            "fps/ntt-friendly-fps.hpp": "fps/FormalPowerSeries.py",
            "fps/polynomial-interpolation.hpp": "polynomial/MultipointEvaluation.py",
            "fps/taylor-shift.hpp": "fps/FormalPowerSeries.py",
        }.items()
    },
    # Factorization feature equivalents (sieve-only files remain pending).
    **{
        ("NyaanNyaan/library", path): "prime/Factorization.py"
        for path in (
            "prime/factor-enumerate.hpp",
            "prime/fast-factorize.hpp",
            "prime/miller-rabin.hpp",
        )
    },
    **{
        ("kemuniku/cplib", path): "prime/Factorization.py"
        for path in (
            "math/divisor.nim",
            "math/euler_phi.nim",
            "math/isprime.nim",
            "math/primefactor.nim",
        )
    },
    **{
        ("tko919/library", path): target
        for path, target in {
            "Algorithm/fibonacci.hpp": "algorithm/Fibonacci.py",
            "Algorithm/maximalrect.hpp": "optimization/Optimization.py",
            "Algorithm/mo.hpp": "algorithm/RangeQueries.py",
        }.items()
    },
    **{
        ("NyaanNyaan/library", path): target
        for path, target in {
            "dp/inversion-counting.hpp": "algorithm/SequenceAlgorithms.py",
            "dp/knapsack01.hpp": "algorithm/DynamicProgramming.py",
            "dp/longest-increasing-sequence.hpp": "algorithm/SequenceAlgorithms.py",
            "misc/compress.hpp": "algorithm/SequenceAlgorithms.py",
            "misc/doubling.hpp": "algorithm/Doubling.py",
            "misc/interval-union.hpp": "algorithm/SequenceAlgorithms.py",
            "misc/mo-fast.hpp": "algorithm/RangeQueries.py",
            "misc/mo.hpp": "algorithm/RangeQueries.py",
        }.items()
    },
    **{
        ("kemuniku/cplib", path): target
        for path, target in {
            "utils/binary_search.nim": "algorithm/Search.py",
            "utils/inversion_number.nim": "algorithm/SequenceAlgorithms.py",
            "utils/knapsack.nim": "algorithm/DynamicProgramming.py",
            "utils/lis.nim": "algorithm/SequenceAlgorithms.py",
        }.items()
    },
    (
        "NachiaVivias/cp-library",
        "set/subset-sum.hpp",
    ): "algorithm/DynamicProgramming.py",
    (
        "NachiaVivias/cp-library",
        "set/dsu-fast.hpp",
    ): "union_find/UnionFind.py",
    (
        "NachiaVivias/cp-library",
        "set/dsu.hpp",
    ): "union_find/UnionFind.py",
    (
        "NachiaVivias/cp-library",
        "set/word-size-tree.hpp",
    ): "ordered_set/FastSet.py",
    **{
        ("NyaanNyaan/library", path): "data_structure/Collections.py"
        for path in (
            "hashmap/hashmap-base.hpp",
            "hashmap/hashmap-unerasable.hpp",
            "hashmap/hashmap.hpp",
            "hashmap/hashset.hpp",
        )
    },
    **{
        ("NyaanNyaan/library", path): "sequence_structure/ImplicitTreap.py"
        for path in (
            "rbst/lazy-reversible-rbst.hpp",
            "rbst/rbst-base.hpp",
            "rbst/treap.hpp",
        )
    },
    (
        "NyaanNyaan/library",
        "shortest-path/dijkstra-skew-heap.hpp",
    ): "graph/ShortestPath.py",
    **{
        ("NachiaVivias/cp-library", path): target
        for path, target in {
            "math/combination.hpp": "math/Combinatorics.py",
            "math/counting-primes.hpp": "prime/Sieve.py",
            "math/ext-gcd.hpp": "math/Combinatorics.py",
            "math/prime-sieve-explicit.hpp": "prime/Sieve.py",
            "multi-dimensional/grid-adj-4.hpp": "graph/ExpandedGraph.py",
            "multi-dimensional/grid-adj-8.hpp": "graph/ExpandedGraph.py",
            "multi-dimensional/grid-adj.hpp": "graph/ExpandedGraph.py",
            "multi-dimensional/two-d-rectangle-query.hpp": "data_structure/RectangleQuery.py",
        }.items()
    },
    **{
        ("tko919/library", path): target
        for path, target in {
            "Math/F2vector.hpp": "linear_algebra/F2Matrix.py",
            "Math/comb.hpp": "math/Combinatorics.py",
            "Math/countsquarefree.hpp": "prime/Sieve.py",
            "Math/enumquotient.hpp": "math/Combinatorics.py",
            "Math/floorsum.hpp": "math/Combinatorics.py",
            "Math/lpftable.hpp": "prime/Sieve.py",
            "Math/lucydp.hpp": "prime/Sieve.py",
            "Math/miller.hpp": "prime/Factorization.py",
            "Math/mobius.hpp": "prime/Sieve.py",
            "Math/pollard.hpp": "prime/Factorization.py",
            "Math/sieve.hpp": "prime/Sieve.py",
            "Math/totient.hpp": "prime/Sieve.py",
        }.items()
    },
    **{
        ("NyaanNyaan/library", path): target
        for path, target in {
            "math/enumerate-quotient.hpp": "math/Combinatorics.py",
            "math/f2.hpp": "linear_algebra/F2Matrix.py",
            "math/floor-sum.hpp": "math/Combinatorics.py",
            "math/gray-code.hpp": "math/Combinatorics.py",
            "math/inv-mod.hpp": "math/Combinatorics.py",
            "math/sweep-restore.hpp": "linear_algebra/Matrix.py",
            "math/sweep.hpp": "linear_algebra/Matrix.py",
            "math-fast/gcd.hpp": "math/Combinatorics.py",
            "math-fast/inv-o1.hpp": "math/Combinatorics.py",
            "math-fast/inv.hpp": "math/Combinatorics.py",
            "modulo/binomial-table.hpp": "math/Combinatorics.py",
            "modulo/binomial.hpp": "math/Combinatorics.py",
            "modulo/factorial.hpp": "math/Combinatorics.py",
            "multiplicative-function/count-square-free.hpp": "prime/Sieve.py",
            "multiplicative-function/prime-counting-faster.hpp": "prime/Sieve.py",
            "multiplicative-function/prime-counting-o2d3.hpp": "prime/Sieve.py",
            "multiplicative-function/prime-counting.hpp": "prime/Sieve.py",
            "prime/osak.hpp": "prime/Sieve.py",
            "prime/prime-enumerate.hpp": "prime/Sieve.py",
            "prime/prime-sieve.hpp": "prime/Sieve.py",
        }.items()
    },
    **{
        ("kemuniku/cplib", path): target
        for path, target in {
            "math/combination.nim": "math/Combinatorics.py",
            "math/ext_gcd.nim": "math/Combinatorics.py",
            "math/inv_gcd.nim": "math/Combinatorics.py",
            "math/osa_k.nim": "prime/Sieve.py",
            "utils/cumsum2d.nim": "data_structure/RectangleQuery.py",
            "utils/grid_searcher.nim": "graph/ExpandedGraph.py",
            "utils/gridutils.nim": "graph/ExpandedGraph.py",
            "utils/imos2d.nim": "data_structure/RectangleQuery.py",
        }.items()
    },
    **{
        ("tko919/library", path): "convolution/AdvancedConvolution.py"
        for path in (
            "Convolution/multivariate.hpp",
            "Convolution/multivariatecyclic.hpp",
        )
    },
    **{
        ("NyaanNyaan/library", path): "convolution/AdvancedConvolution.py"
        for path in (
            "fps/fft2d.hpp",
            "fps/middle-product.hpp",
            "ntt/chirp-z.hpp",
            "ntt/multidimensional-ntt.hpp",
            "ntt/multiplicative-convolution-mod-p.hpp",
            "ntt/multivariate-circular-convolution.hpp",
            "ntt/multivariate-multiplication.hpp",
            "ntt/rader-ntt.hpp",
        )
    },
    (
        "NyaanNyaan/library",
        "ntt/schoenhage-strassen-radix2.hpp",
    ): "convolution/NTT.py",
    (
        "NyaanNyaan/library",
        "fps/fps-composition-fast-old.hpp",
    ): "fps/PolynomialComposition.py",
    **{
        ("tko919/library", path): "convolution/PolynomialAlgorithms.py"
        for path in (
            "FPS/findroots.hpp",
            "FPS/prefixsumofpowers.hpp",
            "FPS/resultant.hpp",
            "FPS/sumofpowers.hpp",
        )
    },
    **{
        ("NyaanNyaan/library", path): "convolution/PolynomialAlgorithms.py"
        for path in (
            "fps/fualhuber.hpp",
            "fps/mod-pow.hpp",
            "fps/partial-fraction-decomposition.hpp",
            "fps/polynomial-gcd.hpp",
            "fps/root-finding.hpp",
        )
    },
    **{
        ("tko919/library", path): "convolution/SeriesSequences.py"
        for path in (
            "FPS/eulertransform.hpp",
            "FPS/famous.hpp",
            "FPS/mobius.hpp",
        )
    },
    **{
        ("NyaanNyaan/library", path): "convolution/SeriesSequences.py"
        for path in (
            "fps/fps-circular.hpp",
            "fps/fps-famous-series.hpp",
            "fps/pascal-matrix.hpp",
            "fps/sparse-fps.hpp",
        )
    },
    (
        "NyaanNyaan/library",
        "fps/inversion-formula.hpp",
    ): "fps/FormalPowerSeries.py",
    **{
        ("NyaanNyaan/library", path): target
        for path, target in {
            "math/affine-transformation.hpp": "math/Structures.py",
            "math/grundy-number.hpp": "math/Structures.py",
            "math/rational.hpp": "math/Structures.py",
            "math/stern-brocot-tree.hpp": "math/Structures.py",
            "math-fast/binary-search.hpp": "algorithm/Search.py",
            "math-fast/radix-sort.hpp": "algorithm/Sorting.py",
            "misc/bitset-find-prev.hpp": "data_structure/Collections.py",
        }.items()
    },
    **{
        ("tko919/library", path): "math/Structures.py"
        for path in (
            "Math/fraction.hpp",
            "Math/sternbrocot.hpp",
        )
    },
    **{
        ("kemuniku/cplib", path): target
        for path, target in {
            "math/fractions.nim": "math/Structures.py",
            "math/mex_naive.nim": "math/Structures.py",
            "math/stern_brocot_tree.nim": "math/Structures.py",
            "math/xor_basis.nim": "math/Structures.py",
            "utils/bititers.nim": "algorithm/BitAlgorithms.py",
            "utils/kth_element.nim": "algorithm/Search.py",
        }.items()
    },
    (
        "tko919/library",
        "DataStructure/manhattanmst.hpp",
    ): "graph_spanning/MinimumSpanningTree.py",
    (
        "tko919/library",
        "DataStructure/unionrect.hpp",
    ): "data_structure/AdvancedCollections.py",
    (
        "NyaanNyaan/library",
        "data-structure/skew-heap.hpp",
    ): "data_structure/AdvancedCollections.py",
    (
        "NachiaVivias/cp-library",
        "range-query/range-add-range-min.hpp",
    ): "segment_tree/SegmentTree.py",
    (
        "NachiaVivias/cp-library",
        "set/decremental-predecessor-query.hpp",
    ): "ordered_set/FastSet.py",
    (
        "NachiaVivias/cp-library",
        "string/persistent-string.hpp",
    ): "string/PersistentString.py",
    (
        "NachiaVivias/cp-library",
        "math/rational-number-search.hpp",
    ): "math/NumberTheoryExtras.py",
    **{
        ("NyaanNyaan/library", path): target
        for path, target in {
            "math/garner.hpp": "number_theory/ChineseRemainder.py",
            "math/gaussian-integer.hpp": "math/NumberTheoryExtras.py",
            "math/two-square.hpp": "math/NumberTheoryExtras.py",
            "misc/int_div.hpp": "math/NumberTheoryExtras.py",
            "modulo/fastpow.hpp": "math/NumberTheoryExtras.py",
            "modulo/mod-log.hpp": "number_theory/ModularArithmetic.py",
            "modulo/quadratic-equation.hpp": "math/NumberTheoryExtras.py",
            "modulo/tetration.hpp": "math/NumberTheoryExtras.py",
        }.items()
    },
    (
        "tko919/library",
        "Math/twosquare.hpp",
    ): "math/NumberTheoryExtras.py",
    **{
        ("NachiaVivias/cp-library", path): target
        for path, target in {
            "bit/bit-operations.hpp": "algorithm/BitAlgorithms.py",
            "misc/sorting.hpp": "algorithm/Sorting.py",
            "set/enumerate-paritions.hpp": "combinatorics/IntegerPartitions.py",
        }.items()
    },
    **{
        ("kemuniku/cplib", path): target
        for path, target in {
            "graph/merge_tree.nim": "graph_spanning/MergeTree.py",
            "math/nearest_equiv.nim": "algorithm/IntegerUtilities.py",
            "math/powmod.nim": "algorithm/IntegerUtilities.py",
            "math/sqrt_heuristic_for_floor_sum.nim": "algorithm/ModularProgression.py",
            "utils/mo.nim": "algorithm/RangeQueries.py",
        }.items()
    },
    (
        "NachiaVivias/cp-library",
        "array/concave-min-plus-convolution.hpp",
    ): "optimization/AdvancedDP.py",
    **{
        ("tko919/library", path): "optimization/AdvancedDP.py"
        for path in (
            "Algorithm/mongedp.hpp",
            "Algorithm/rollbackmo.hpp",
        )
    },
    **{
        ("NyaanNyaan/library", path): "optimization/AdvancedDP.py"
        for path in (
            "dp/branch-and-bound.hpp",
            "dp/concave-min-plus-convolution.hpp",
            "dp/monge-d-edge-shortest-path-enumerate.hpp",
            "dp/monge-d-edge-shortest-path.hpp",
            "dp/monge-shortest-path.hpp",
        )
    },
    (
        "NyaanNyaan/library",
        "math/sat-solver.hpp",
    ): "algebra/SATSolver.py",
    **{
        ("NyaanNyaan/library", path): "game/GameTheory.py"
        for path in (
            "game/impartial-game.hpp",
            "game/partisan-game.hpp",
            "game/surreal-number.hpp",
        )
    },
    (
        "tko919/library",
        "Algorithm/matroid.hpp",
    ): "optimization/Matroid.py",
    **{
        ("NyaanNyaan/library", path): "heuristic/Heuristics.py"
        for path in (
            "marathon/log_table.hpp",
            "marathon/multi-armed-bandit.hpp",
            "marathon/sa-manager.hpp",
            "marathon/simulated-annealing.hpp",
            "marathon/top-k.hpp",
        )
    },
    **{
        ("NyaanNyaan/library", path): "random/RandomGraph.py"
        for path in (
            "random_graph/gen.hpp",
            "random_graph/graph.hpp",
            "random_graph/random.hpp",
        )
    },
    **{
        ("NyaanNyaan/library", path): "math/AlgebraExtras.py"
        for path in (
            "math/float-binomial.hpp",
            "math/rational-binomial.hpp",
            "math/semiring-linear-recursive.hpp",
            "math/semiring.hpp",
        )
    },
    **{
        ("tko919/library", path): "math/AlgebraExtras.py"
        for path in (
            "Math/invsum.hpp",
            "Math/pisano.hpp",
            "Math/powertable.hpp",
            "Math/qbinom.hpp",
        )
    },
    (
        "NachiaVivias/cp-library",
        "math/erdos-ginzburg-ziv-task.hpp",
    ): "combinatorics/ErdosGinzburgZiv.py",
    (
        "NyaanNyaan/library",
        "math/elementary-function.hpp",
    ): "number_theory/Elementary.py",
    (
        "NyaanNyaan/library",
        "misc/base64.hpp",
    ): "algorithm/Base64Integers.py",
    (
        "NyaanNyaan/library",
        "set-function/enumerate-set.hpp",
    ): "algorithm/BitAlgorithms.py",
    (
        "tko919/library",
        "Convolution/relax.hpp",
    ): "fps/OnlineFormalPowerSeries.py",
    **{
        ("NyaanNyaan/library", path): "fps/OnlineFormalPowerSeries.py"
        for path in (
            "fps/differential-equation.hpp",
            "fps/newton-method.hpp",
            "fps/online-fps.hpp",
            "ntt/relaxed-convolution.hpp",
        )
    },
    **{
        ("NyaanNyaan/library", path): "data_structure/AdvancedOrdered.py"
        for path in (
            "orderedmap/orderedmap-base.hpp",
            "orderedmap/orderedmap.hpp",
        )
    },
    (
        "tko919/library",
        "DataStructure/persistentrbstset.hpp",
    ): "data_structure/AdvancedOrdered.py",
    (
        "NachiaVivias/cp-library",
        "tree/incremental-forest.hpp",
    ): "tree/IncrementalForest.py",
    **{
        ("NyaanNyaan/library", path): "data_structure/RectangleQuery.py"
        for path in (
            "data-structure-2d/abstract-range-tree.hpp",
            "data-structure-2d/segment-tree-on-range-tree.hpp",
            "data-structure-2d/segment-tree-on-wavelet-matrix.hpp",
        )
    },
    (
        "NyaanNyaan/library",
        "data-structure/line-container-2d.hpp",
    ): "data_structure/LinearOptimization.py",
    (
        "tko919/library",
        "DataStructure/rangelinearaddrangemin.hpp",
    ): "data_structure/LinearOptimization.py",
    (
        "NachiaVivias/cp-library",
        "array/point-update-lex-sort.hpp",
    ): "algorithm/SequenceOrdering.py",
    (
        "NachiaVivias/cp-library",
        "permutation/simplify-permitation-subgroup.hpp",
    ): "algorithm/PermutationGroup.py",
    **{
        ("tko919/library", path): "convolution/AdvancedSeries.py"
        for path in (
            "FPS/compexp.hpp",
            "FPS/interpolategeom.hpp",
            "FPS/multievalgeom.hpp",
            "FPS/prefixsumofpoly.hpp",
            "FPS/prodoffrkx.hpp",
            "FPS/sumofRationals.hpp",
            "FPS/sumofpolyexp.hpp",
        )
    },
    (
        "tko919/library",
        "FPS/powenum.hpp",
    ): "convolution/AdvancedSeries.py",
    (
        "NyaanNyaan/library",
        "fps/pow-enumerate.hpp",
    ): "convolution/AdvancedSeries.py",
    (
        "NyaanNyaan/library",
        "fps/dual-fps.hpp",
    ): "convolution/FPSWrappers.py",
    (
        "NyaanNyaan/library",
        "fps/fps-fraction.hpp",
    ): "convolution/FPSWrappers.py",
    **{
        (name, path): "combinatorial_series/PRecursive.py"
        for name, path in (
            ("tko919/library", "FPS/p-recursive.hpp"),
            ("NyaanNyaan/library", "fps/find-p-recursive.hpp"),
        )
    },
    (
        "NyaanNyaan/library",
        "fps/composite-exp.hpp",
    ): "convolution/AdvancedSeries.py",
    (
        "NyaanNyaan/library",
        "fps/sum-of-exponential-times-poly.hpp",
    ): "convolution/AdvancedSeries.py",
    (
        "NyaanNyaan/library",
        "fps/multivariate-fps.hpp",
    ): "fps/MultivariateFPS.py",
    (
        "NyaanNyaan/library",
        "fps/stirling-matrix.hpp",
    ): "combinatorial_series/StirlingMatrix.py",
    (
        "NyaanNyaan/library",
        "math/rational-fps.hpp",
    ): "rational/RationalFormalPowerSeries.py",
    (
        "NyaanNyaan/library",
        "math/stern-brocot-tree-binary-search.hpp",
    ): "rational/FractionSearch.py",
    **{
        ("NyaanNyaan/library", path): "linear_algebra/Strassen.py"
        for path in (
            "math-fast/mat-prod-strassen.hpp",
            "modulo/strassen.hpp",
        )
    },
    (
        "tko919/library",
        "FPS/factlarge.hpp",
    ): "combinatorics/ArbitraryBinomial.py",
    (
        "tko919/library",
        "Math/binomquery.hpp",
    ): "combinatorics/ArbitraryBinomial.py",
    (
        "tko919/library",
        "Math/stirlingquery.hpp",
    ): "combinatorics/BinomialQueries.py",
    **{
        ("NyaanNyaan/library", path): "combinatorics/ArbitraryBinomial.py"
        for path in (
            "modulo/arbitrary-mod-binomial-large.hpp",
            "modulo/arbitrary-mod-binomial.hpp",
        )
    },
    (
        "NyaanNyaan/library",
        "modulo/multipoint-binomial-sum.hpp",
    ): "combinatorics/BinomialQueries.py",
    **{
        (name, path): "number_theory/MultiplicativeFunctions.py"
        for name, path in (
            ("tko919/library", "Math/dirichlet.hpp"),
            ("tko919/library", "Math/multiplicative.hpp"),
            ("tko919/library", "Math/multiplicative2.hpp"),
            ("NyaanNyaan/library", "multiplicative-function/enamurate-multiplicative-function.hpp"),
            ("NyaanNyaan/library", "multiplicative-function/enumerate-sum-of-multiplicative-function.hpp"),
            ("NyaanNyaan/library", "multiplicative-function/mf-famous-series.hpp"),
            ("NyaanNyaan/library", "multiplicative-function/sum-of-multiplicative-function.hpp"),
            ("NyaanNyaan/library", "multiplicative-function/sum-of-totient.hpp"),
        )
    },
    **{
        (name, path): "game/Nimber.py"
        for name, path in (
            ("tko919/library", "Math/nimber.hpp"),
            ("NyaanNyaan/library", "math/nimber.hpp"),
            ("NyaanNyaan/library", "math/nimber-to-field.hpp"),
        )
    },
    (
        "tko919/library",
        "Math/partizangame.hpp",
    ): "game/PartizanGame.py",
    (
        "tko919/library",
        "Math/scarysum.hpp",
    ): "number_theory/FloorPolynomialSum.py",
    **{
        ("tko919/library", path): "polynomial/PolynomialFactorization.py"
        for path in (
            "FPS/factorize.hpp",
            "FPS/halfgcd.hpp",
        )
    },
    (
        "tko919/library",
        "FPS/incseqcount.hpp",
    ): "fps/IncreasingSequences.py",
    (
        "tko919/library",
        "Graph/generalweightedmatching.hpp",
    ): "graph_matching/GeneralWeightedMatching.py",
    (
        "NachiaVivias/cp-library",
        "range-query/range-add-count-top-k.hpp",
    ): "data_structure/AdvancedRangeStructures.py",
    (
        "tko919/library",
        "DataStructure/lazykdtree.hpp",
    ): "data_structure/AdvancedRangeStructures.py",
    (
        "tko919/library",
        "DataStructure/sortablesegtree.hpp",
    ): "data_structure/AdvancedRangeStructures.py",
    **{
        (name, path): "segment_tree/RangeLIS.py"
        for name, path in (
            ("NachiaVivias/cp-library", "range-query/range-lis.hpp"),
            ("tko919/library", "DataStructure/rangelis.hpp"),
        )
    },
    (
        "NyaanNyaan/library",
        "tree/dynamic-rerooting.hpp",
    ): "tree/DynamicRerooting.py",
}


def source_files(root, suffix):
    result = []
    for path in root.rglob("*" + suffix):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        result.append(relative)
    result.sort(key=lambda path: path.as_posix())
    return result


def build_inventory():
    lines = [
        "# Reference source inventory",
        "",
        "4ライブラリの機能和集合を完了判定するための全ソース目録です。",
        "`[ ]` は未監査、`[x]` は `library` または `library_codex` の対応先と検証を確認済み、",
        "`[-]` は言語固有support、`[~]` はユーザー指定で保留中の Geometry を表します。",
        "このファイルは `tools/build_reference_inventory.py` で再生成できます。",
        "",
    ]
    total = 0
    support = 0
    for name, root, suffix in SOURCES:
        files = source_files(root, suffix)
        total += len(files)
        lines.append("## " + name)
        lines.append("")
        current_category = None
        for path in files:
            category = path.parts[0] if len(path.parts) > 1 else "root"
            if category != current_category:
                lines.append("### " + category)
                lines.append("")
                current_category = category
            covered_by = COVERED.get((name, path.as_posix()))
            if covered_by is not None:
                marker = "[x]"
                note = f" — `{covered_by}`"
            elif (name, path.as_posix()) in DEFERRED_GEOMETRY_FILES or category in {
                "geometry", "Geometry"
            }:
                marker = "[~]"
                note = " — Geometry（ユーザー指定で保留）"
            elif (name, path.as_posix()) in SUPPORT_FILES or category in SUPPORT_CATEGORIES:
                marker = "[-]"
                note = " — language support; feature audit is carried by consumers"
                support += 1
            else:
                marker = "[ ]"
                note = ""
            lines.append(f"- {marker} `{path.as_posix()}`{note}")
        lines.append("")
    lines.insert(
        7,
        f"現在の列挙数: **{total} files**（うちsupport暫定分類 {support} files）。",
    )
    lines.insert(8, "")
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "REFERENCE_INVENTORY.md"
    output.write_text(build_inventory())
