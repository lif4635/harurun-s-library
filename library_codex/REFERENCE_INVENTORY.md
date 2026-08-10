# Reference source inventory

4ライブラリの機能和集合を完了判定するための全ソース目録です。
`[ ]` は未監査、`[x]` は `library` または `library_codex` の対応先と検証を確認済み、
`[-]` は言語固有support、`[~]` はユーザー指定で保留中の Geometry を表します。
このファイルは `tools/build_reference_inventory.py` で再生成できます。

現在の列挙数: **792 files**（うちsupport暫定分類 92 files）。

## NachiaVivias/cp-library

### array

- [x] `array/bbst-list.hpp` — `sequence_structure/ImplicitTreap.py`
- [x] `array/cartesian-tree.hpp` — `sequence_structure/CartesianTree.py`
- [x] `array/concave-min-plus-convolution.hpp` — `optimization/AdvancedDP.py`
- [x] `array/convex-min-plus-convolution.hpp` — `optimization/Optimization.py`
- [-] `array/csr-array.hpp` — language support; feature audit is carried by consumers
- [x] `array/deque-operate-aggregation.hpp` — `data_structure/SWAG.py`
- [x] `array/divisor-convolution.hpp` — `arithmetic_convolution/ArithmeticConvolution.py`
- [x] `array/lazy-segtree.hpp` — `segment_tree/SegTree.py`
- [x] `array/li-ciao-tree-flexible.hpp` — `spatial_structure/LiChaoTree.py`
- [x] `array/point-update-lex-sort.hpp` — `algorithm/SequenceOrdering.py`
- [x] `array/segtree.hpp` — `segment_tree/SegTree.py`
- [x] `array/wavelet-matrix.hpp` — `range_query/WaveletMatrix.py`
### bit-convolution

- [x] `bit-convolution/set-power-series-power-projection.hpp` — `bitwise_convolution/SetFunction.py`
### bit

- [x] `bit/bit-operations.hpp` — `algorithm/BitAlgorithms.py`
### counting

- [x] `counting/chromatic-polynomial.hpp` — `graph_enumeration/GraphCounting.py`
- [x] `counting/directed-spanning-trees.hpp` — `graph_enumeration/GraphCounting.py`
- [x] `counting/euler-cycles.hpp` — `graph_enumeration/GraphCounting.py`
### geometry

- [~] `geometry/delaunay-triangulation.hpp` — Geometry（ユーザー指定で保留）
- [~] `geometry/veci2.hpp` — Geometry（ユーザー指定で保留）
### graph

- [x] `graph/biconnected-components.hpp` — `graph_connectivity/BiconnectedComponents.py`
- [x] `graph/bipartite-edge-coloring.hpp` — `graph_enumeration/GraphProperties.py`
- [x] `graph/chordal-graph-recognizer.hpp` — `graph_enumeration/GraphProperties.py`
- [x] `graph/chromatic-number.hpp` — `graph/GraphEnumeration.py`
- [x] `graph/connected-components.hpp` — `graph/ShortestPath.py`
- [x] `graph/count-c4.hpp` — `graph/GraphEnumeration.py`
- [x] `graph/dfs-tree.hpp` — `graph/ShortestPath.py`
- [x] `graph/dijkstra.hpp` — `graph/ShortestPath.py`
- [x] `graph/dynamic-connectivity.hpp` — `graph_connectivity/OnlineDynamicConnectivity.py`
- [x] `graph/eulerian-trail.hpp` — `graph/EulerianTrail.py`
- [-] `graph/graph.hpp` — language support; feature audit is carried by consumers
- [x] `graph/incremental-scc-offline.hpp` — `graph_connectivity/AdvancedConnectivity.py`
- [x] `graph/k-shortest-path-directed.hpp` — `shortest_path/KShortestPaths.py`
- [x] `graph/k-shortest-path-undirected.hpp` — `shortest_path/KShortestPaths.py`
- [x] `graph/strongly-connected-components.hpp` — `graph_connectivity/StronglyConnectedComponents.py`
- [x] `graph/three-edge-connected-components.hpp` — `graph_connectivity/AdvancedConnectivity.py`
- [x] `graph/two-edge-connected-components.hpp` — `graph_connectivity/TwoEdgeConnectedComponents.py`
### linear-modulo

- [x] `linear-modulo/characteristic-polynomial.hpp` — `linear_algebra/Matrix.py`
- [x] `linear-modulo/linear-equation.hpp` — `linear_algebra/Matrix.py`
- [x] `linear-modulo/matrix-modulo.hpp` — `linear_algebra/Matrix.py`
### math-modulo

- [-] `math-modulo/static-modint.hpp` — language support; feature audit is carried by consumers
### math

- [x] `math/combination.hpp` — `math/Combinatorics.py`
- [x] `math/counting-primes.hpp` — `prime/Sieve.py`
- [x] `math/erdos-ginzburg-ziv-task.hpp` — `combinatorics/ErdosGinzburgZiv.py`
- [x] `math/ext-gcd.hpp` — `math/Combinatorics.py`
- [x] `math/floor-of-kth-root.hpp` — `number_theory/ModularRoot.py`
- [x] `math/prime-sieve-explicit.hpp` — `prime/Sieve.py`
- [x] `math/rational-number-search.hpp` — `math/NumberTheoryExtras.py`
### misc

- [-] `misc/fastio.hpp` — language support; feature audit is carried by consumers
- [x] `misc/sorting.hpp` — `algorithm/Sorting.py`
### modulo

- [-] `modulo/static-modint.hpp` — language support; feature audit is carried by consumers
### multi-dimensional

- [x] `multi-dimensional/grid-adj-4.hpp` — `graph/ExpandedGraph.py`
- [x] `multi-dimensional/grid-adj-8.hpp` — `graph/ExpandedGraph.py`
- [x] `multi-dimensional/grid-adj.hpp` — `graph/ExpandedGraph.py`
- [x] `multi-dimensional/two-d-rectangle-query.hpp` — `data_structure/RectangleQuery.py`
### permutation

- [x] `permutation/simplify-permitation-subgroup.hpp` — `algorithm/PermutationGroup.py`
### range-query

- [x] `range-query/point-set-range-min.hpp` — `segment_tree/SegTree.py`
- [x] `range-query/range-add-count-top-k.hpp` — `data_structure/AdvancedRangeStructures.py`
- [x] `range-query/range-add-range-min.hpp` — `segment_tree/SegTree.py`
- [x] `range-query/range-lis.hpp` — `segment_tree/RangeLIS.py`
### set

- [x] `set/decremental-predecessor-query.hpp` — `ordered_set/FastSet.py`
- [x] `set/dsu-fast.hpp` — `union_find/UnionFind.py`
- [x] `set/dsu.hpp` — `union_find/UnionFind.py`
- [x] `set/enumerate-paritions.hpp` — `combinatorics/IntegerPartitions.py`
- [x] `set/subset-sum.hpp` — `algorithm/DynamicProgramming.py`
- [x] `set/word-size-tree.hpp` — `ordered_set/FastSet.py`
### string

- [x] `string/persistent-string.hpp` — `string/PersistentString.py`
### tree

- [x] `tree/ahu-algorithm.hpp` — `tree/TreeIsomorphism.py`
- [x] `tree/centroid-decomposition-binary-tree.hpp` — `tree/CentroidDecomposition.py`
- [x] `tree/centroid-decomposition.hpp` — `tree/CentroidDecomposition.py`
- [x] `tree/heavy-light-decomposition.hpp` — `tree/HeavyLightDecomposition.py`
- [x] `tree/incremental-forest.hpp` — `tree/IncrementalForest.py`
- [x] `tree/static-top-tree.hpp` — `tree/StaticTopTree.py`
- [x] `tree/tree-center.hpp` — `tree/TreeIsomorphism.py`
- [x] `tree/tree-centroid.hpp` — `tree/TreeIsomorphism.py`
- [x] `tree/tree-diameter.hpp` — `tree/TreeAlgorithms.py`
- [x] `tree/tree-dp.hpp` — `tree/Rerooting.py`

## tko919/library

### Algorithm

- [x] `Algorithm/cartesian.hpp` — `sequence_structure/CartesianTree.py`
- [x] `Algorithm/fibonacci.hpp` — `algorithm/Fibonacci.py`
- [x] `Algorithm/kprojectselection.hpp` — `optimization/ProjectSelection.py`
- [x] `Algorithm/matroid.hpp` — `optimization/Matroid.py`
- [x] `Algorithm/maximalrect.hpp` — `optimization/Optimization.py`
- [x] `Algorithm/mo.hpp` — `algorithm/RangeQueries.py`
- [x] `Algorithm/mongedp.hpp` — `optimization/AdvancedDP.py`
- [x] `Algorithm/monotoneminima.hpp` — `optimization/Optimization.py`
- [x] `Algorithm/projectselection.hpp` — `optimization/ProjectSelection.py`
- [x] `Algorithm/rollbackmo.hpp` — `optimization/AdvancedDP.py`
- [x] `Algorithm/wildcardpatternmatching.hpp` — `string/WildcardPatternMatching.py`
### Convolution

- [x] `Convolution/arbitrary.hpp` — `convolution/NTT.py`
- [x] `Convolution/bitwise.hpp` — `bitwise_convolution/SetFunction.py`
- [x] `Convolution/convexminplus.hpp` — `optimization/Optimization.py`
- [x] `Convolution/divisor.hpp` — `arithmetic_convolution/ArithmeticConvolution.py`
- [x] `Convolution/fft.hpp` — `convolution/NTT.py`
- [x] `Convolution/multivariate.hpp` — `convolution/AdvancedConvolution.py`
- [x] `Convolution/multivariatecyclic.hpp` — `convolution/AdvancedConvolution.py`
- [x] `Convolution/ntt.hpp` — `convolution/NTT.py`
- [x] `Convolution/relax.hpp` — `fps/OnlineFormalPowerSeries.py`
- [x] `Convolution/subset.hpp` — `bitwise_convolution/SetFunction.py`
### DataStructure

- [x] `DataStructure/2dbit.hpp` — `fenwick_tree/BIT.py`
- [x] `DataStructure/2dsegtree.hpp` — `data_structure/RectangleQuery.py`
- [x] `DataStructure/bit.hpp` — `fenwick_tree/BIT.py`
- [x] `DataStructure/chtmonotone.hpp` — `optimization/Optimization.py`
- [x] `DataStructure/dequeswag.hpp` — `data_structure/SWAG.py`
- [x] `DataStructure/disjointsparsetable.hpp` — `range_query/DisjointSparseTable.py`
- [x] `DataStructure/dualsegtree.hpp` — `segment_tree/SegTree.py`
- [x] `DataStructure/dynamiclazysegtree.hpp` — `segment_tree/DynamicSegmentTree.py`
- [x] `DataStructure/dynamicrectsum.hpp` — `data_structure/RectangleQuery.py`
- [x] `DataStructure/dynamicsegtree.hpp` — `segment_tree/DynamicSegmentTree.py`
- [x] `DataStructure/fastset.hpp` — `ordered_set/FastSet.py`
- [x] `DataStructure/hashmap.hpp` — `data_structure/Collections.py`
- [x] `DataStructure/lazykdtree.hpp` — `data_structure/AdvancedRangeStructures.py`
- [x] `DataStructure/lazysegtree.hpp` — `segment_tree/SegTree.py`
- [x] `DataStructure/lichaotree.hpp` — `spatial_structure/LiChaoTree.py`
- [x] `DataStructure/linkedlist.hpp` — `data_structure/Collections.py`
- [x] `DataStructure/manhattanmst.hpp` — `graph_spanning/MinimumSpanningTree.py`
- [x] `DataStructure/persistentarray.hpp` — `sequence_structure/PersistentArray.py`
- [x] `DataStructure/persistentlazysegtree.hpp` — `segment_tree/DynamicSegmentTree.py`
- [x] `DataStructure/persistentrbstset.hpp` — `data_structure/AdvancedOrdered.py`
- [x] `DataStructure/persistentunionfind.hpp` — `union_find/PersistentUnionFind.py`
- [x] `DataStructure/pointsetrangefreq.hpp` — `data_structure/Collections.py`
- [x] `DataStructure/rangelinearaddrangemin.hpp` — `data_structure/LinearOptimization.py`
- [x] `DataStructure/rangelis.hpp` — `segment_tree/RangeLIS.py`
- [x] `DataStructure/rangeparalleluf.hpp` — `union_find/UnionFind.py`
- [x] `DataStructure/rangeunionset.hpp` — `data_structure/Collections.py`
- [x] `DataStructure/rbstset.hpp` — `data_structure/Collections.py`
- [x] `DataStructure/rollbackunionfind.hpp` — `union_find/RollbackUnionFind.py`
- [x] `DataStructure/segtree.hpp` — `segment_tree/SegTree.py`
- [x] `DataStructure/segtreebeats.hpp` — `segment_tree/SegmentTreeBeats.py`
- [x] `DataStructure/slopetrick.hpp` — `optimization/SlopeTrick.py`
- [x] `DataStructure/sortablesegtree.hpp` — `data_structure/AdvancedRangeStructures.py`
- [x] `DataStructure/staticrectaddrectsum.hpp` — `data_structure/RectangleQuery.py`
- [x] `DataStructure/staticrectsum.hpp` — `data_structure/RectangleQuery.py`
- [x] `DataStructure/swag.hpp` — `data_structure/SWAG.py`
- [x] `DataStructure/unionfind.hpp` — `union_find/UnionFind.py`
- [x] `DataStructure/unionrect.hpp` — `data_structure/AdvancedCollections.py`
- [x] `DataStructure/wavelet.hpp` — `range_query/WaveletMatrix.py`
- [x] `DataStructure/weightedunionfind.hpp` — `union_find/UnionFind.py`
### FPS

- [x] `FPS/arbitraryfps.hpp` — `fps/FormalPowerSeries.py`
- [x] `FPS/berlekampmassey.hpp` — `combinatorial_series/LinearRecurrence.py`
- [x] `FPS/compexp.hpp` — `convolution/AdvancedSeries.py`
- [x] `FPS/compinv.hpp` — `fps/PolynomialComposition.py`
- [x] `FPS/composition.hpp` — `fps/PolynomialComposition.py`
- [x] `FPS/eulertransform.hpp` — `convolution/SeriesSequences.py`
- [x] `FPS/factlarge.hpp` — `combinatorics/ArbitraryBinomial.py`
- [x] `FPS/factorize.hpp` — `polynomial/PolynomialFactorization.py`
- [x] `FPS/famous.hpp` — `convolution/SeriesSequences.py`
- [x] `FPS/findroots.hpp` — `convolution/PolynomialAlgorithms.py`
- [x] `FPS/fps.hpp` — `fps/FormalPowerSeries.py`
- [x] `FPS/halfgcd.hpp` — `polynomial/PolynomialFactorization.py`
- [x] `FPS/incseqcount.hpp` — `fps/IncreasingSequences.py`
- [x] `FPS/interpolate.hpp` — `polynomial/MultipointEvaluation.py`
- [x] `FPS/interpolategeom.hpp` — `convolution/AdvancedSeries.py`
- [x] `FPS/mobius.hpp` — `convolution/SeriesSequences.py`
- [x] `FPS/multieval.hpp` — `polynomial/MultipointEvaluation.py`
- [x] `FPS/multievalgeom.hpp` — `convolution/AdvancedSeries.py`
- [x] `FPS/nthterm.hpp` — `combinatorial_series/LinearRecurrence.py`
- [x] `FPS/p-recursive.hpp` — `combinatorial_series/PRecursive.py`
- [x] `FPS/powenum.hpp` — `convolution/AdvancedSeries.py`
- [x] `FPS/prefixsumofpoly.hpp` — `convolution/AdvancedSeries.py`
- [x] `FPS/prefixsumofpowers.hpp` — `convolution/PolynomialAlgorithms.py`
- [x] `FPS/prodoffrkx.hpp` — `convolution/AdvancedSeries.py`
- [x] `FPS/prodofpolys.hpp` — `fps/FormalPowerSeries.py`
- [x] `FPS/resultant.hpp` — `convolution/PolynomialAlgorithms.py`
- [x] `FPS/samplepointshift.hpp` — `polynomial/MultipointEvaluation.py`
- [x] `FPS/sumofRationals.hpp` — `convolution/AdvancedSeries.py`
- [x] `FPS/sumofpolyexp.hpp` — `convolution/AdvancedSeries.py`
- [x] `FPS/sumofpowers.hpp` — `convolution/PolynomialAlgorithms.py`
### Geometry

- [~] `Geometry/Enclosing.hpp` — Geometry（ユーザー指定で保留）
- [~] `Geometry/FracCoord.hpp` — Geometry（ユーザー指定で保留）
- [~] `Geometry/geometry.hpp` — Geometry（ユーザー指定で保留）
- [~] `Geometry/intCoord.hpp` — Geometry（ユーザー指定で保留）
### Graph

- [x] `Graph/auxiliarytree.hpp` — `tree/TreeAlgorithms.py`
- [x] `Graph/bimatching.hpp` — `graph_matching/BipartiteMatching.py`
- [x] `Graph/bipolar.hpp` — `graph_spanning/GraphOrdering.py`
- [x] `Graph/blockcut.hpp` — `graph_connectivity/BiconnectedComponents.py`
- [x] `Graph/centroid.hpp` — `tree/CentroidDecomposition.py`
- [x] `Graph/chromatic.hpp` — `graph/GraphEnumeration.py`
- [x] `Graph/chromaticpoly.hpp` — `graph_enumeration/GraphCounting.py`
- [x] `Graph/contour.hpp` — `tree/CentroidDecomposition.py`
- [x] `Graph/counteuler.hpp` — `graph_enumeration/GraphCounting.py`
- [x] `Graph/countspanning.hpp` — `graph_enumeration/GraphCounting.py`
- [x] `Graph/cycledetect.hpp` — `graph/CycleDetection.py`
- [x] `Graph/diameter.hpp` — `tree/TreeAlgorithms.py`
- [x] `Graph/dmdecomp.hpp` — `graph_matching/BipartiteMatching.py`
- [x] `Graph/edgecoloring.hpp` — `graph_enumeration/GraphProperties.py`
- [x] `Graph/enumcliques.hpp` — `graph/GraphEnumeration.py`
- [x] `Graph/enumtriangle.hpp` — `graph/GraphEnumeration.py`
- [x] `Graph/euler.hpp` — `graph/EulerianTrail.py`
- [x] `Graph/general.hpp` — `graph/GraphMatching.py`
- [x] `Graph/generalweightedmatching.hpp` — `graph_matching/GeneralWeightedMatching.py`
- [x] `Graph/hld.hpp` — `tree/HeavyLightDecomposition.py`
- [x] `Graph/hungarian.hpp` — `graph/GraphOptimization.py`
- [x] `Graph/lca.hpp` — `tree/LCA.py`
- [x] `Graph/linkcut.hpp` — `tree/LinkCutTree.py`
- [x] `Graph/lowlink.hpp` — `graph_connectivity/LowLink.py`
- [x] `Graph/maxflow.hpp` — `graph_flow/MaxFlow.py`
- [x] `Graph/maxindependentset.hpp` — `graph/GraphEnumeration.py`
- [x] `Graph/mincostflow.hpp` — `graph_flow/MinCostBFlow.py`
- [x] `Graph/opttoposort.hpp` — `graph_spanning/GraphOrdering.py`
- [x] `Graph/prufer.hpp` — `tree/PruferCode.py`
- [x] `Graph/rerooting.hpp` — `tree/Rerooting.py`
- [x] `Graph/scc.hpp` — `graph_connectivity/StronglyConnectedComponents.py`
- [x] `Graph/shortestpathremedge.hpp` — `graph_spanning/GraphOrdering.py`
- [x] `Graph/statictoptree.hpp` — `tree/StaticTopTree.py`
- [x] `Graph/steiner.hpp` — `graph/GraphOptimization.py`
### Math

- [x] `Math/F2vector.hpp` — `linear_algebra/F2Matrix.py`
- [-] `Math/algebra.hpp` — language support; feature audit is carried by consumers
- [x] `Math/bbla.hpp` — `linear_algebra/BlackBoxLinearAlgebra.py`
- [-] `Math/bigint.hpp` — language support; feature audit is carried by consumers
- [x] `Math/binomquery.hpp` — `combinatorics/ArbitraryBinomial.py`
- [x] `Math/charpoly.hpp` — `linear_algebra/Matrix.py`
- [x] `Math/comb.hpp` — `math/Combinatorics.py`
- [x] `Math/countsquarefree.hpp` — `prime/Sieve.py`
- [x] `Math/detaplusbx.hpp` — `linear_algebra/PolynomialMatrix.py`
- [x] `Math/dirichlet.hpp` — `number_theory/MultiplicativeFunctions.py`
- [-] `Math/dynamic.hpp` — language support; feature audit is carried by consumers
- [x] `Math/enumquotient.hpp` — `math/Combinatorics.py`
- [-] `Math/fastdiv.hpp` — language support; feature audit is carried by consumers
- [x] `Math/floorsum.hpp` — `math/Combinatorics.py`
- [x] `Math/fraction.hpp` — `math/Structures.py`
- [x] `Math/gaussian.hpp` — `math/NumberTheoryExtras.py`
- [x] `Math/hafnian.hpp` — `linear_algebra/AdvancedMatrix.py`
- [-] `Math/hash.hpp` — language support; feature audit is carried by consumers
- [x] `Math/invsum.hpp` — `math/AlgebraExtras.py`
- [x] `Math/kthroot.hpp` — `number_theory/ModularRoot.py`
- [x] `Math/linearequation.hpp` — `linear_algebra/Matrix.py`
- [x] `Math/lpftable.hpp` — `prime/Sieve.py`
- [x] `Math/lucydp.hpp` — `prime/Sieve.py`
- [x] `Math/matrix.hpp` — `linear_algebra/Matrix.py`
- [x] `Math/miller.hpp` — `prime/Factorization.py`
- [x] `Math/mobius.hpp` — `prime/Sieve.py`
- [-] `Math/modint.hpp` — language support; feature audit is carried by consumers
- [x] `Math/multiplicative.hpp` — `number_theory/MultiplicativeFunctions.py`
- [x] `Math/multiplicative2.hpp` — `number_theory/MultiplicativeFunctions.py`
- [x] `Math/nimber.hpp` — `game/Nimber.py`
- [x] `Math/partizangame.hpp` — `game/PartizanGame.py`
- [x] `Math/pfaffian.hpp` — `linear_algebra/AdvancedMatrix.py`
- [x] `Math/pisano.hpp` — `math/AlgebraExtras.py`
- [x] `Math/pollard.hpp` — `prime/Factorization.py`
- [x] `Math/powertable.hpp` — `math/AlgebraExtras.py`
- [x] `Math/primitive.hpp` — `number_theory/ModularRoot.py`
- [x] `Math/qbinom.hpp` — `math/AlgebraExtras.py`
- [x] `Math/scarysum.hpp` — `number_theory/FloorPolynomialSum.py`
- [x] `Math/sieve.hpp` — `prime/Sieve.py`
- [x] `Math/sternbrocot.hpp` — `math/Structures.py`
- [x] `Math/stirlingquery.hpp` — `combinatorics/BinomialQueries.py`
- [x] `Math/totient.hpp` — `prime/Sieve.py`
- [x] `Math/twosat.hpp` — `graph/GraphMatching.py`
- [x] `Math/twosquare.hpp` — `math/NumberTheoryExtras.py`
### String

- [x] `String/ahocorasick.hpp` — `string/AhoCorasick.py`
- [x] `String/manacher.hpp` — `string/Manacher.py`
- [x] `String/palindromictree.hpp` — `string/PalindromicTree.py`
- [x] `String/prefixsubstrlcs.hpp` — `string/PrefixSubstringLCS.py`
- [x] `String/rollinghash.hpp` — `string/RollingHash.py`
- [x] `String/suffixarray.hpp` — `string/SuffixArray.py`
- [x] `String/suffixautomaton.hpp` — `string/SuffixAutomaton.py`
- [x] `String/trie.hpp` — `string/Trie.py`
- [x] `String/zalgo.hpp` — `string/ZAlgorithm.py`
### Template

- [-] `Template/template.hpp` — language support; feature audit is carried by consumers
### Utility

- [-] `Utility/fastio.hpp` — language support; feature audit is carried by consumers
- [-] `Utility/random.hpp` — language support; feature audit is carried by consumers
- [-] `Utility/timer.hpp` — language support; feature audit is carried by consumers
- [-] `Utility/visualizer.hpp` — language support; feature audit is carried by consumers

## NyaanNyaan/library

### atcoder

- [-] `atcoder/convolution.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/dsu.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/fenwicktree.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/internal_bit.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/internal_csr.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/internal_math.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/internal_queue.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/internal_scc.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/internal_type_traits.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/lazysegtree.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/math.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/maxflow.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/mincostflow.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/modint.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/scc.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/segtree.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/string.hpp` — language support; feature audit is carried by consumers
- [-] `atcoder/twosat.hpp` — language support; feature audit is carried by consumers
### data-structure-2d

- [x] `data-structure-2d/2d-binary-indexed-tree.hpp` — `fenwick_tree/BIT.py`
- [x] `data-structure-2d/2d-cumulative-sum.hpp` — `data_structure/RectangleQuery.py`
- [x] `data-structure-2d/2d-segment-tree.hpp` — `data_structure/RectangleQuery.py`
- [x] `data-structure-2d/abstract-range-tree.hpp` — `data_structure/RectangleQuery.py`
- [x] `data-structure-2d/dynamic-binary-indexed-tree-2d.hpp` — `data_structure/RectangleQuery.py`
- [x] `data-structure-2d/fenwick-tree-on-range-tree.hpp` — `data_structure/RectangleQuery.py`
- [x] `data-structure-2d/fenwick-tree-on-wavelet-matrix.hpp` — `data_structure/RectangleQuery.py`
- [x] `data-structure-2d/rectangle-add-rectangle-sum.hpp` — `data_structure/RectangleQuery.py`
- [x] `data-structure-2d/rectangle-sum.hpp` — `data_structure/RectangleQuery.py`
- [x] `data-structure-2d/segment-tree-on-range-tree.hpp` — `data_structure/RectangleQuery.py`
- [x] `data-structure-2d/segment-tree-on-wavelet-matrix.hpp` — `data_structure/RectangleQuery.py`
- [x] `data-structure-2d/wavelet-matrix.hpp` — `range_query/WaveletMatrix.py`
### data-structure

- [x] `data-structure/binary-indexed-tree.hpp` — `fenwick_tree/BIT.py`
- [x] `data-structure/binary-trie.hpp` — `ordered_set/BinaryTrie.py`
- [x] `data-structure/divide-interval.hpp` — `segment_tree/SegTree.py`
- [x] `data-structure/dynamic-binary-indexed-tree.hpp` — `fenwick_tree/BIT.py`
- [x] `data-structure/dynamic-bitset.hpp` — `data_structure/Collections.py`
- [x] `data-structure/dynamic-union-find.hpp` — `union_find/UnionFind.py`
- [x] `data-structure/erasable-priority-queue.hpp` — `data_structure/SWAG.py`
- [x] `data-structure/hash-map-variable-length.hpp` — `data_structure/Collections.py`
- [x] `data-structure/line-container-2d.hpp` — `data_structure/LinearOptimization.py`
- [x] `data-structure/line-container.hpp` — `optimization/Optimization.py`
- [x] `data-structure/parallel-union-find.hpp` — `union_find/UnionFind.py`
- [x] `data-structure/persistent-array.hpp` — `sequence_structure/PersistentArray.py`
- [x] `data-structure/persistent-queue.hpp` — `data_structure/Collections.py`
- [x] `data-structure/persistent-union-find.hpp` — `union_find/PersistentUnionFind.py`
- [x] `data-structure/radix-heap.hpp` — `sequence_structure/RadixHeap.py`
- [x] `data-structure/range-sum-range-add-bit.hpp` — `fenwick_tree/BIT.py`
- [x] `data-structure/range-union-find.hpp` — `union_find/UnionFind.py`
- [x] `data-structure/rollback-union-find.hpp` — `union_find/RollbackUnionFind.py`
- [x] `data-structure/segment-set.hpp` — `data_structure/Collections.py`
- [x] `data-structure/skew-heap.hpp` — `data_structure/AdvancedCollections.py`
- [x] `data-structure/slide-window-aggregation-deque.hpp` — `data_structure/SWAG.py`
- [x] `data-structure/slide-window-aggregation.hpp` — `data_structure/SWAG.py`
- [x] `data-structure/sliding-window-minimum.hpp` — `data_structure/Collections.py`
- [x] `data-structure/slope-trick-weighted.hpp` — `optimization/SlopeTrick.py`
- [x] `data-structure/slope-trick.hpp` — `optimization/SlopeTrick.py`
- [x] `data-structure/sparse-table.hpp` — `range_query/DisjointSparseTable.py`
- [x] `data-structure/square-root-decomposition.hpp` — `segment_tree/SegTree.py`
- [x] `data-structure/union-find-enumerate.hpp` — `union_find/UnionFind.py`
- [x] `data-structure/union-find-with-potential.hpp` — `union_find/UnionFind.py`
- [x] `data-structure/union-find.hpp` — `union_find/UnionFind.py`
- [x] `data-structure/van-emde-boas-tree.hpp` — `ordered_set/FastSet.py`
- [x] `data-structure/w-ary-tree.hpp` — `ordered_set/FastSet.py`
### dp

- [x] `dp/branch-and-bound.hpp` — `optimization/AdvancedDP.py`
- [x] `dp/concave-min-plus-convolution.hpp` — `optimization/AdvancedDP.py`
- [x] `dp/golden-section-search.hpp` — `optimization/Optimization.py`
- [x] `dp/inversion-counting.hpp` — `algorithm/SequenceAlgorithms.py`
- [x] `dp/knapsack01.hpp` — `algorithm/DynamicProgramming.py`
- [x] `dp/longest-increasing-sequence.hpp` — `algorithm/SequenceAlgorithms.py`
- [x] `dp/maximal-rectangle.hpp` — `optimization/Optimization.py`
- [x] `dp/monge-d-edge-shortest-path-enumerate.hpp` — `optimization/AdvancedDP.py`
- [x] `dp/monge-d-edge-shortest-path.hpp` — `optimization/AdvancedDP.py`
- [x] `dp/monge-shortest-path.hpp` — `optimization/AdvancedDP.py`
- [x] `dp/monotone-minima.hpp` — `optimization/Optimization.py`
### flow

- [x] `flow/flow-on-bipartite-graph.hpp` — `graph_matching/BipartiteMatching.py`
### fps

- [x] `fps/arbitrary-fps.hpp` — `fps/FormalPowerSeries.py`
- [x] `fps/berlekamp-massey.hpp` — `combinatorial_series/LinearRecurrence.py`
- [x] `fps/composite-exp.hpp` — `convolution/AdvancedSeries.py`
- [x] `fps/differential-equation.hpp` — `fps/OnlineFormalPowerSeries.py`
- [x] `fps/dual-fps.hpp` — `convolution/FPSWrappers.py`
- [x] `fps/fast-interpolate.hpp` — `polynomial/MultipointEvaluation.py`
- [x] `fps/fast-multieval.hpp` — `polynomial/MultipointEvaluation.py`
- [x] `fps/fft2d.hpp` — `convolution/AdvancedConvolution.py`
- [x] `fps/find-p-recursive.hpp` — `combinatorial_series/PRecursive.py`
- [x] `fps/formal-power-series.hpp` — `fps/FormalPowerSeries.py`
- [x] `fps/fps-circular.hpp` — `convolution/SeriesSequences.py`
- [x] `fps/fps-composition-fast-old.hpp` — `fps/PolynomialComposition.py`
- [x] `fps/fps-composition-old.hpp` — `fps/PolynomialComposition.py`
- [x] `fps/fps-composition.hpp` — `fps/PolynomialComposition.py`
- [x] `fps/fps-compositional-inverse.hpp` — `fps/PolynomialComposition.py`
- [x] `fps/fps-famous-series.hpp` — `convolution/SeriesSequences.py`
- [x] `fps/fps-fraction.hpp` — `convolution/FPSWrappers.py`
- [x] `fps/fps-sqrt.hpp` — `fps/FormalPowerSeries.py`
- [x] `fps/fps-utility.hpp` — `fps/FormalPowerSeries.py`
- [x] `fps/fualhuber.hpp` — `convolution/PolynomialAlgorithms.py`
- [x] `fps/inversion-formula.hpp` — `fps/FormalPowerSeries.py`
- [x] `fps/kitamasa.hpp` — `combinatorial_series/LinearRecurrence.py`
- [x] `fps/lagrange-interpolation-point.hpp` — `polynomial/MultipointEvaluation.py`
- [x] `fps/middle-product.hpp` — `convolution/AdvancedConvolution.py`
- [x] `fps/mod-pow.hpp` — `convolution/PolynomialAlgorithms.py`
- [x] `fps/multipoint-evaluation.hpp` — `polynomial/MultipointEvaluation.py`
- [x] `fps/multivariate-fps.hpp` — `fps/MultivariateFPS.py`
- [x] `fps/newton-method.hpp` — `fps/OnlineFormalPowerSeries.py`
- [x] `fps/nth-term.hpp` — `combinatorial_series/LinearRecurrence.py`
- [x] `fps/ntt-friendly-fps.hpp` — `fps/FormalPowerSeries.py`
- [x] `fps/online-fps.hpp` — `fps/OnlineFormalPowerSeries.py`
- [x] `fps/partial-fraction-decomposition.hpp` — `convolution/PolynomialAlgorithms.py`
- [x] `fps/pascal-matrix.hpp` — `convolution/SeriesSequences.py`
- [x] `fps/polynomial-gcd.hpp` — `convolution/PolynomialAlgorithms.py`
- [x] `fps/polynomial-interpolation.hpp` — `polynomial/MultipointEvaluation.py`
- [x] `fps/pow-enumerate.hpp` — `convolution/AdvancedSeries.py`
- [x] `fps/root-finding.hpp` — `convolution/PolynomialAlgorithms.py`
- [x] `fps/sample-point-shift.hpp` — `polynomial/MultipointEvaluation.py`
- [x] `fps/sparse-fps.hpp` — `convolution/SeriesSequences.py`
- [x] `fps/stirling-matrix.hpp` — `combinatorial_series/StirlingMatrix.py`
- [x] `fps/sum-of-exponential-times-poly.hpp` — `convolution/AdvancedSeries.py`
- [x] `fps/taylor-shift.hpp` — `fps/FormalPowerSeries.py`
### game

- [x] `game/impartial-game.hpp` — `game/GameTheory.py`
- [x] `game/partisan-game.hpp` — `game/GameTheory.py`
- [x] `game/surreal-number.hpp` — `game/GameTheory.py`
### geometry

- [~] `geometry/circle.hpp` — Geometry（ユーザー指定で保留）
- [~] `geometry/geometry-base.hpp` — Geometry（ユーザー指定で保留）
- [~] `geometry/integer-geometry.hpp` — Geometry（ユーザー指定で保留）
- [~] `geometry/line.hpp` — Geometry（ユーザー指定で保留）
- [~] `geometry/polygon.hpp` — Geometry（ユーザー指定で保留）
- [~] `geometry/segment.hpp` — Geometry（ユーザー指定で保留）
### graph

- [x] `graph/biconnected-components.hpp` — `graph_connectivity/BiconnectedComponents.py`
- [x] `graph/chromatic-number.hpp` — `graph/GraphEnumeration.py`
- [x] `graph/cycle-detection.hpp` — `graph/CycleDetection.py`
- [x] `graph/dimension-expanded-graph.hpp` — `graph/ExpandedGraph.py`
- [x] `graph/functional-graph.hpp` — `graph_connectivity/FunctionalGraph.py`
- [-] `graph/graph-template.hpp` — language support; feature audit is carried by consumers
- [x] `graph/graph-utility.hpp` — `graph/ShortestPath.py`
- [x] `graph/kruskal.hpp` — `graph_spanning/MinimumSpanningTree.py`
- [x] `graph/lowlink.hpp` — `graph_connectivity/LowLink.py`
- [x] `graph/max-independent-set.hpp` — `graph/GraphEnumeration.py`
- [x] `graph/minimum-cost-arborescence.hpp` — `graph/GraphOptimization.py`
- [x] `graph/namori.hpp` — `graph_connectivity/NamoriDecomposition.py`
- [x] `graph/offline-dynamic-connectivity.hpp` — `graph_connectivity/OfflineDynamicConnectivity.py`
- [-] `graph/static-graph.hpp` — language support; feature audit is carried by consumers
- [x] `graph/strongly-connected-components.hpp` — `graph_connectivity/StronglyConnectedComponents.py`
- [x] `graph/topological-sort.hpp` — `graph/ShortestPath.py`
- [x] `graph/two-edge-connected-components.hpp` — `graph_connectivity/TwoEdgeConnectedComponents.py`
### hashmap

- [x] `hashmap/hashmap-base.hpp` — `data_structure/Collections.py`
- [x] `hashmap/hashmap-unerasable.hpp` — `data_structure/Collections.py`
- [x] `hashmap/hashmap.hpp` — `data_structure/Collections.py`
- [x] `hashmap/hashset.hpp` — `data_structure/Collections.py`
### internal

- [-] `internal/internal-hash-function.hpp` — language support; feature audit is carried by consumers
- [-] `internal/internal-hash.hpp` — language support; feature audit is carried by consumers
- [-] `internal/internal-math.hpp` — language support; feature audit is carried by consumers
- [-] `internal/internal-seed.hpp` — language support; feature audit is carried by consumers
- [-] `internal/internal-type-traits.hpp` — language support; feature audit is carried by consumers
### lct

- [x] `lct/lazy-reversible-bbst-base.hpp` — `tree/LinkCutTree.py`
- [x] `lct/link-cut-base.hpp` — `tree/LinkCutTree.py`
- [x] `lct/link-cut-tree-lazy.hpp` — `tree/LinkCutTree.py`
- [x] `lct/link-cut-tree-subtree-add.hpp` — `tree/LinkCutTree.py`
- [x] `lct/link-cut-tree-subtree.hpp` — `tree/LinkCutTree.py`
- [x] `lct/link-cut-tree.hpp` — `tree/LinkCutTree.py`
- [x] `lct/reversible-bbst-base.hpp` — `tree/LinkCutTree.py`
- [x] `lct/splay-base.hpp` — `tree/LinkCutTree.py`
- [x] `lct/splay-lazy-reversible.hpp` — `tree/LinkCutTree.py`
- [x] `lct/splay-reversible.hpp` — `tree/LinkCutTree.py`
### marathon

- [x] `marathon/log_table.hpp` — `heuristic/Heuristics.py`
- [x] `marathon/multi-armed-bandit.hpp` — `heuristic/Heuristics.py`
- [x] `marathon/sa-manager.hpp` — `heuristic/Heuristics.py`
- [x] `marathon/simulated-annealing.hpp` — `heuristic/Heuristics.py`
- [x] `marathon/top-k.hpp` — `heuristic/Heuristics.py`
### math-fast

- [x] `math-fast/binary-search.hpp` — `algorithm/Search.py`
- [x] `math-fast/gcd.hpp` — `math/Combinatorics.py`
- [x] `math-fast/inv-o1.hpp` — `math/Combinatorics.py`
- [x] `math-fast/inv.hpp` — `math/Combinatorics.py`
- [x] `math-fast/mat-prod-strassen.hpp` — `linear_algebra/Strassen.py`
- [x] `math-fast/radix-sort.hpp` — `algorithm/Sorting.py`
- [x] `math-fast/subset-convolution.hpp` — `bitwise_convolution/SetFunction.py`
- [-] `math-fast/vectorize-modint.hpp` — language support; feature audit is carried by consumers
### math

- [x] `math/affine-transformation.hpp` — `math/Structures.py`
- [-] `math/bigint-all.hpp` — language support; feature audit is carried by consumers
- [-] `math/bigint-binary.hpp` — language support; feature audit is carried by consumers
- [-] `math/bigint-garner.hpp` — language support; feature audit is carried by consumers
- [-] `math/bigint-gcd.hpp` — language support; feature audit is carried by consumers
- [-] `math/bigint-rational.hpp` — language support; feature audit is carried by consumers
- [-] `math/bigint-to-hex.hpp` — language support; feature audit is carried by consumers
- [-] `math/bigint.hpp` — language support; feature audit is carried by consumers
- [x] `math/constexpr-primitive-root.hpp` — `number_theory/ModularRoot.py`
- [x] `math/elementary-function.hpp` — `number_theory/Elementary.py`
- [~] `math/enumerate-convex.hpp` — Geometry（ユーザー指定で保留）
- [x] `math/enumerate-quotient.hpp` — `math/Combinatorics.py`
- [x] `math/f2.hpp` — `linear_algebra/F2Matrix.py`
- [x] `math/float-binomial.hpp` — `math/AlgebraExtras.py`
- [x] `math/floor-sum.hpp` — `math/Combinatorics.py`
- [x] `math/garner.hpp` — `number_theory/ChineseRemainder.py`
- [x] `math/gaussian-integer.hpp` — `math/NumberTheoryExtras.py`
- [x] `math/gray-code.hpp` — `math/Combinatorics.py`
- [x] `math/grundy-number.hpp` — `math/Structures.py`
- [x] `math/inv-mod.hpp` — `math/Combinatorics.py`
- [x] `math/isqrt.hpp` — `number_theory/ModularRoot.py`
- [x] `math/kth-root-integral.hpp` — `number_theory/ModularRoot.py`
- [x] `math/nimber-to-field.hpp` — `game/Nimber.py`
- [x] `math/nimber.hpp` — `game/Nimber.py`
- [x] `math/primitive-root-ll.hpp` — `number_theory/ModularRoot.py`
- [x] `math/rational-binomial.hpp` — `math/AlgebraExtras.py`
- [x] `math/rational-fps.hpp` — `rational/RationalFormalPowerSeries.py`
- [x] `math/rational.hpp` — `math/Structures.py`
- [x] `math/sat-solver.hpp` — `algebra/SATSolver.py`
- [x] `math/semiring-linear-recursive.hpp` — `math/AlgebraExtras.py`
- [x] `math/semiring.hpp` — `math/AlgebraExtras.py`
- [x] `math/stern-brocot-tree-binary-search.hpp` — `rational/FractionSearch.py`
- [x] `math/stern-brocot-tree.hpp` — `math/Structures.py`
- [x] `math/sweep-restore.hpp` — `linear_algebra/Matrix.py`
- [x] `math/sweep.hpp` — `linear_algebra/Matrix.py`
- [x] `math/two-sat.hpp` — `graph/GraphMatching.py`
- [x] `math/two-square.hpp` — `math/NumberTheoryExtras.py`
### matrix

- [x] `matrix/black-box-linear-algebra.hpp` — `linear_algebra/BlackBoxLinearAlgebra.py`
- [x] `matrix/characteristric-polynomial.hpp` — `linear_algebra/Matrix.py`
- [x] `matrix/determinant-arbitrary-mod.hpp` — `linear_algebra/AdvancedMatrix.py`
- [x] `matrix/f2-matrix.hpp` — `linear_algebra/F2Matrix.py`
- [x] `matrix/gauss-elimination.hpp` — `linear_algebra/Matrix.py`
- [x] `matrix/hafnian.hpp` — `linear_algebra/AdvancedMatrix.py`
- [x] `matrix/inverse-matrix.hpp` — `linear_algebra/Matrix.py`
- [x] `matrix/linear-equation-hashmap.hpp` — `linear_algebra/Matrix.py`
- [x] `matrix/linear-equation.hpp` — `linear_algebra/Matrix.py`
- [x] `matrix/matrix-fast.hpp` — `linear_algebra/Matrix.py`
- [x] `matrix/matrix-tree.hpp` — `linear_algebra/PolynomialMatrix.py`
- [x] `matrix/matrix.hpp` — `linear_algebra/Matrix.py`
- [x] `matrix/polynomial-matrix-determinant.hpp` — `linear_algebra/PolynomialMatrix.py`
- [x] `matrix/polynomial-matrix-prefix-prod.hpp` — `linear_algebra/PolynomialMatrix.py`
### misc

- [-] `misc/all.hpp` — language support; feature audit is carried by consumers
- [x] `misc/base64.hpp` — `algorithm/Base64Integers.py`
- [x] `misc/bitset-find-prev.hpp` — `data_structure/Collections.py`
- [x] `misc/compress.hpp` — `algorithm/SequenceAlgorithms.py`
- [x] `misc/doubling.hpp` — `algorithm/Doubling.py`
- [-] `misc/fastio.hpp` — language support; feature audit is carried by consumers
- [x] `misc/int_div.hpp` — `math/NumberTheoryExtras.py`
- [x] `misc/interval-union.hpp` — `algorithm/SequenceAlgorithms.py`
- [x] `misc/mo-fast.hpp` — `algorithm/RangeQueries.py`
- [x] `misc/mo.hpp` — `algorithm/RangeQueries.py`
- [-] `misc/rng.hpp` — language support; feature audit is carried by consumers
- [-] `misc/simd.hpp` — language support; feature audit is carried by consumers
- [-] `misc/timer.hpp` — language support; feature audit is carried by consumers
- [-] `misc/vector-pool.hpp` — language support; feature audit is carried by consumers
### modint

- [-] `modint/adjunction-modint.hpp` — language support; feature audit is carried by consumers
- [-] `modint/arbitrary-modint.hpp` — language support; feature audit is carried by consumers
- [-] `modint/arbitrary-montgomery-modint.hpp` — language support; feature audit is carried by consumers
- [-] `modint/barrett-reduction.hpp` — language support; feature audit is carried by consumers
- [-] `modint/modint-2-61m1.hpp` — language support; feature audit is carried by consumers
- [-] `modint/modint-cpp11.hpp` — language support; feature audit is carried by consumers
- [-] `modint/modint.hpp` — language support; feature audit is carried by consumers
- [-] `modint/montgomery-modint.hpp` — language support; feature audit is carried by consumers
- [-] `modint/simd-montgomery.hpp` — language support; feature audit is carried by consumers
- [-] `modint/vectorize-modint.hpp` — language support; feature audit is carried by consumers
### modulo

- [x] `modulo/arbitrary-mod-binomial-large.hpp` — `combinatorics/ArbitraryBinomial.py`
- [x] `modulo/arbitrary-mod-binomial.hpp` — `combinatorics/ArbitraryBinomial.py`
- [x] `modulo/binomial-table.hpp` — `math/Combinatorics.py`
- [x] `modulo/binomial.hpp` — `math/Combinatorics.py`
- [x] `modulo/factorial.hpp` — `math/Combinatorics.py`
- [x] `modulo/fastpow.hpp` — `math/NumberTheoryExtras.py`
- [x] `modulo/gauss-elimination-fast.hpp` — `linear_algebra/Matrix.py`
- [x] `modulo/mod-kth-root.hpp` — `number_theory/ModularRoot.py`
- [x] `modulo/mod-log.hpp` — `number_theory/ModularArithmetic.py`
- [x] `modulo/mod-sqrt.hpp` — `number_theory/ModularArithmetic.py`
- [x] `modulo/multipoint-binomial-sum.hpp` — `combinatorics/BinomialQueries.py`
- [x] `modulo/quadratic-equation.hpp` — `math/NumberTheoryExtras.py`
- [x] `modulo/strassen.hpp` — `linear_algebra/Strassen.py`
- [x] `modulo/tetration.hpp` — `math/NumberTheoryExtras.py`
### multiplicative-function

- [x] `multiplicative-function/count-square-free.hpp` — `prime/Sieve.py`
- [x] `multiplicative-function/divisor-multiple-transform.hpp` — `arithmetic_convolution/ArithmeticConvolution.py`
- [x] `multiplicative-function/enamurate-multiplicative-function.hpp` — `number_theory/MultiplicativeFunctions.py`
- [x] `multiplicative-function/enumerate-sum-of-multiplicative-function.hpp` — `number_theory/MultiplicativeFunctions.py`
- [x] `multiplicative-function/gcd-convolution.hpp` — `arithmetic_convolution/ArithmeticConvolution.py`
- [x] `multiplicative-function/mf-famous-series.hpp` — `number_theory/MultiplicativeFunctions.py`
- [x] `multiplicative-function/prime-counting-faster.hpp` — `prime/Sieve.py`
- [x] `multiplicative-function/prime-counting-o2d3.hpp` — `prime/Sieve.py`
- [x] `multiplicative-function/prime-counting.hpp` — `prime/Sieve.py`
- [x] `multiplicative-function/sum-of-multiplicative-function.hpp` — `number_theory/MultiplicativeFunctions.py`
- [x] `multiplicative-function/sum-of-totient.hpp` — `number_theory/MultiplicativeFunctions.py`
### ntt

- [x] `ntt/arbitrary-ntt-mod18446744069414584321.hpp` — `convolution/NTT.py`
- [x] `ntt/arbitrary-ntt.hpp` — `convolution/NTT.py`
- [x] `ntt/chirp-z.hpp` — `convolution/AdvancedConvolution.py`
- [x] `ntt/complex-fft.hpp` — `convolution/NTT.py`
- [x] `ntt/convolution-large.hpp` — `convolution/NTT.py`
- [x] `ntt/cooley-tukey-ntt.hpp` — `convolution/NTT.py`
- [x] `ntt/karatsuba.hpp` — `convolution/NTT.py`
- [x] `ntt/multidimensional-ntt.hpp` — `convolution/AdvancedConvolution.py`
- [x] `ntt/multiplicative-convolution-mod-p.hpp` — `convolution/AdvancedConvolution.py`
- [x] `ntt/multivariate-circular-convolution.hpp` — `convolution/AdvancedConvolution.py`
- [x] `ntt/multivariate-multiplication.hpp` — `convolution/AdvancedConvolution.py`
- [x] `ntt/ntt-64bit.hpp` — `convolution/NTT.py`
- [x] `ntt/ntt-avx2.hpp` — `convolution/NTT.py`
- [x] `ntt/ntt-cpp11.hpp` — `convolution/NTT.py`
- [x] `ntt/ntt-sse42.hpp` — `convolution/NTT.py`
- [x] `ntt/ntt.hpp` — `convolution/NTT.py`
- [x] `ntt/rader-ntt.hpp` — `convolution/AdvancedConvolution.py`
- [x] `ntt/relaxed-convolution.hpp` — `fps/OnlineFormalPowerSeries.py`
- [x] `ntt/schoenhage-strassen-radix2.hpp` — `convolution/NTT.py`
### orderedmap

- [x] `orderedmap/orderedmap-base.hpp` — `data_structure/AdvancedOrdered.py`
- [x] `orderedmap/orderedmap.hpp` — `data_structure/AdvancedOrdered.py`
### prime

- [x] `prime/factor-enumerate.hpp` — `prime/Factorization.py`
- [x] `prime/fast-factorize.hpp` — `prime/Factorization.py`
- [x] `prime/miller-rabin.hpp` — `prime/Factorization.py`
- [x] `prime/osak.hpp` — `prime/Sieve.py`
- [x] `prime/prime-enumerate.hpp` — `prime/Sieve.py`
- [x] `prime/prime-sieve.hpp` — `prime/Sieve.py`
### random_graph

- [x] `random_graph/gen.hpp` — `random/RandomGraph.py`
- [x] `random_graph/graph.hpp` — `random/RandomGraph.py`
- [x] `random_graph/random.hpp` — `random/RandomGraph.py`
### rbst

- [x] `rbst/lazy-reversible-rbst.hpp` — `sequence_structure/ImplicitTreap.py`
- [x] `rbst/rbst-base.hpp` — `sequence_structure/ImplicitTreap.py`
- [x] `rbst/treap.hpp` — `sequence_structure/ImplicitTreap.py`
### segment-tree

- [x] `segment-tree/dynamic-li-chao-tree.hpp` — `spatial_structure/LiChaoTree.py`
- [x] `segment-tree/dynamic-segment-tree.hpp` — `segment_tree/DynamicSegmentTree.py`
- [x] `segment-tree/lazy-segment-tree-utility.hpp` — `segment_tree/SegTree.py`
- [x] `segment-tree/lazy-segment-tree.hpp` — `segment_tree/SegTree.py`
- [x] `segment-tree/li-chao-tree-abstruct.hpp` — `spatial_structure/LiChaoTree.py`
- [x] `segment-tree/li-chao-tree.hpp` — `spatial_structure/LiChaoTree.py`
- [x] `segment-tree/persistent-segment-tree.hpp` — `segment_tree/PersistentSegmentTree.py`
- [x] `segment-tree/range-weighted-add-range-sum-lazyseg.hpp` — `segment_tree/SegTree.py`
- [x] `segment-tree/rbst-segment-tree.hpp` — `sequence_structure/ImplicitTreap.py`
- [x] `segment-tree/rbst-sequence.hpp` — `sequence_structure/ImplicitTreap.py`
- [x] `segment-tree/segment-tree-beats-abstract.hpp` — `segment_tree/SegmentTreeBeats.py`
- [x] `segment-tree/segment-tree-beats.hpp` — `segment_tree/SegmentTreeBeats.py`
- [x] `segment-tree/segment-tree-max-of-interval.hpp` — `segment_tree/SegTree.py`
- [x] `segment-tree/segment-tree.hpp` — `segment_tree/SegTree.py`
### set-function

- [x] `set-function/and-convolution.hpp` — `bitwise_convolution/SetFunction.py`
- [x] `set-function/enumerate-set.hpp` — `algorithm/BitAlgorithms.py`
- [x] `set-function/exp-of-set-power-series.hpp` — `bitwise_convolution/SetFunction.py`
- [x] `set-function/or-convolution.hpp` — `bitwise_convolution/SetFunction.py`
- [x] `set-function/polynomial-composite-set-power-series.hpp` — `bitwise_convolution/SetFunction.py`
- [x] `set-function/subset-convolution.hpp` — `bitwise_convolution/SetFunction.py`
- [x] `set-function/walsh-hadamard-transform.hpp` — `bitwise_convolution/SetFunction.py`
- [x] `set-function/xor-convolution.hpp` — `bitwise_convolution/SetFunction.py`
- [x] `set-function/zeta-mobius-transform.hpp` — `bitwise_convolution/SetFunction.py`
### shortest-path

- [x] `shortest-path/bellman-ford.hpp` — `graph/ShortestPath.py`
- [x] `shortest-path/bfs-restore.hpp` — `graph/ShortestPath.py`
- [x] `shortest-path/bfs01.hpp` — `graph/ShortestPath.py`
- [x] `shortest-path/dijkstra-abstruct.hpp` — `graph/ShortestPath.py`
- [x] `shortest-path/dijkstra-fast.hpp` — `graph/ShortestPath.py`
- [x] `shortest-path/dijkstra-radix-heap.hpp` — `shortest_path/DijkstraRadixHeap.py`
- [x] `shortest-path/dijkstra-skew-heap.hpp` — `graph/ShortestPath.py`
- [x] `shortest-path/dijkstra-with-restore.hpp` — `graph/ShortestPath.py`
- [x] `shortest-path/dijkstra.hpp` — `graph/ShortestPath.py`
- [~] `shortest-path/dual-of-shortest-path.hpp` — Geometry（ユーザー指定で保留）
- [x] `shortest-path/restore-shortest-path.hpp` — `graph/ShortestPath.py`
- [x] `shortest-path/warshall-floyd.hpp` — `graph/ShortestPath.py`
### string

- [x] `string/aho-corasick.hpp` — `string/AhoCorasick.py`
- [x] `string/manacher.hpp` — `string/Manacher.py`
- [x] `string/number-of-subsequences.hpp` — `string/Subsequence.py`
- [x] `string/rolling-hash-2d.hpp` — `string/RollingHash2D.py`
- [x] `string/rolling-hash-on-segment-tree.hpp` — `string/DynamicRollingHash.py`
- [x] `string/rolling-hash.hpp` — `string/RollingHash.py`
- [x] `string/run-enumerate.hpp` — `string/RunEnumeration.py`
- [x] `string/run-length-encoding.hpp` — `string/RunLengthEncoding.py`
- [x] `string/string-search.hpp` — `string/StringSearch.py`
- [x] `string/suffix-array.hpp` — `string/SuffixArray.py`
- [x] `string/suffix-automaton.hpp` — `string/SuffixAutomaton.py`
- [x] `string/trie.hpp` — `string/Trie.py`
- [x] `string/wildcard-pattern-matching.hpp` — `string/WildcardPatternMatching.py`
- [x] `string/z-algorithm.hpp` — `string/ZAlgorithm.py`
### template

- [-] `template/bitop.hpp` — language support; feature audit is carried by consumers
- [-] `template/debug.hpp` — language support; feature audit is carried by consumers
- [-] `template/inout.hpp` — language support; feature audit is carried by consumers
- [-] `template/macro.hpp` — language support; feature audit is carried by consumers
- [-] `template/template.hpp` — language support; feature audit is carried by consumers
- [-] `template/util.hpp` — language support; feature audit is carried by consumers
### tree

- [x] `tree/auxiliary-tree.hpp` — `tree/TreeAlgorithms.py`
- [x] `tree/block-cut-tree.hpp` — `graph_connectivity/BiconnectedComponents.py`
- [x] `tree/cartesian-tree.hpp` — `sequence_structure/CartesianTree.py`
- [x] `tree/centroid-decomposition.hpp` — `tree/CentroidDecomposition.py`
- [x] `tree/centroid.hpp` — `tree/TreeIsomorphism.py`
- [x] `tree/convert-tree.hpp` — `tree/TreeAlgorithms.py`
- [x] `tree/dsu-on-tree.hpp` — `tree/DSUOnTree.py`
- [x] `tree/dynamic-diameter.hpp` — `tree/DynamicDiameter.py`
- [x] `tree/dynamic-rerooting.hpp` — `tree/DynamicRerooting.py`
- [x] `tree/euler-tour.hpp` — `tree/TreeAlgorithms.py`
- [x] `tree/frequency-table-of-tree-distance.hpp` — `tree/TreeDistanceFrequency.py`
- [x] `tree/heavy-light-decomposition.hpp` — `tree/HeavyLightDecomposition.py`
- [x] `tree/inclusion-tree.hpp` — `tree/TreeAlgorithms.py`
- [x] `tree/process-of-merging-tree.hpp` — `tree/TreeAlgorithms.py`
- [x] `tree/pruefer-code.hpp` — `tree/PruferCode.py`
- [x] `tree/rerooting.hpp` — `tree/Rerooting.py`
- [x] `tree/rooted-tree-hash.hpp` — `tree/TreeIsomorphism.py`
- [x] `tree/static-top-tree-edge-based.hpp` — `tree/StaticTopTree.py`
- [x] `tree/static-top-tree-vertex-based.hpp` — `tree/StaticTopTree.py`
- [x] `tree/tree-hash.hpp` — `tree/TreeIsomorphism.py`
- [x] `tree/tree-query.hpp` — `tree/HeavyLightDecomposition.py`

## kemuniku/cplib

### collections

- [x] `collections/QSWAG.nim` — `data_structure/SWAG.py`
- [x] `collections/SWAG.nim` — `data_structure/SWAG.py`
- [x] `collections/avlset.nim` — `data_structure/Collections.py`
- [x] `collections/avlset_old.nim` — `data_structure/Collections.py`
- [x] `collections/avltreenode.nim` — `data_structure/Collections.py`
- [x] `collections/avltreenode_old.nim` — `data_structure/Collections.py`
- [x] `collections/binary_trie.nim` — `ordered_set/BinaryTrie.py`
- [x] `collections/bitset.nim` — `data_structure/Collections.py`
- [x] `collections/bitvector.nim` — `data_structure/Collections.py`
- [x] `collections/defaultdict.nim` — `data_structure/Collections.py`
- [x] `collections/deletable_heapqueue.nim` — `data_structure/SWAG.py`
- [x] `collections/fenwick2d.nim` — `fenwick_tree/BIT.py`
- [x] `collections/group_unionfind.nim` — `union_find/UnionFind.py`
- [x] `collections/hashset.nim` — `data_structure/Collections.py`
- [x] `collections/hashtable.nim` — `data_structure/Collections.py`
- [x] `collections/lazysegtree.nim` — `segment_tree/SegTree.py`
- [x] `collections/lichaotree.nim` — `spatial_structure/LiChaoTree.py`
- [x] `collections/persistent_array.nim` — `sequence_structure/PersistentArray.py`
- [x] `collections/persistent_binary_trie.nim` — `data_structure/Collections.py`
- [x] `collections/persistent_segtree.nim` — `segment_tree/PersistentSegmentTree.py`
- [x] `collections/persistent_unionfind.nim` — `union_find/PersistentUnionFind.py`
- [x] `collections/ppunionfind.nim` — `union_find/UnionFind.py`
- [x] `collections/range_reverse_array.nim` — `sequence_structure/ImplicitTreap.py`
- [x] `collections/range_reverse_array_monoid.nim` — `sequence_structure/ImplicitTreap.py`
- [x] `collections/range_reverse_dualsegtree.nim` — `sequence_structure/ImplicitTreap.py`
- [x] `collections/range_reverse_lazysegtree.nim` — `sequence_structure/ImplicitTreap.py`
- [x] `collections/rangeset.nim` — `data_structure/Collections.py`
- [x] `collections/raw_ptr_avlset.nim` — `data_structure/Collections.py`
- [x] `collections/rollback_unionfind.nim` — `union_find/RollbackUnionFind.py`
- [x] `collections/root_rangesum.nim` — `segment_tree/SegTree.py`
- [x] `collections/rootvalue_unionfind.nim` — `union_find/UnionFind.py`
- [x] `collections/segtree.nim` — `segment_tree/SegTree.py`
- [x] `collections/segtree2d.nim` — `data_structure/RectangleQuery.py`
- [x] `collections/segtree_beats.nim` — `segment_tree/SegmentTreeBeats.py`
- [x] `collections/segtree_beats_template.nim` — `segment_tree/SegmentTreeBeats.py`
- [x] `collections/segtree_var.nim` — `segment_tree/SegTree.py`
- [x] `collections/slopetrick.nim` — `optimization/SlopeTrick.py`
- [x] `collections/staticRMQ.nim` — `range_query/StaticRMQ.py`
- [x] `collections/staticbitset.nim` — `data_structure/Collections.py`
- [x] `collections/staticrangecount.nim` — `range_query/WaveletMatrix.py`
- [x] `collections/tatyamset.nim` — `ordered_set/FastSet.py`
- [x] `collections/topk_sum_heapq.nim` — `data_structure/Collections.py`
- [x] `collections/unionfind.nim` — `union_find/UnionFind.py`
- [x] `collections/waveletmatrix.nim` — `range_query/WaveletMatrix.py`
- [x] `collections/weightedunionfind.nim` — `union_find/UnionFind.py`
- [x] `collections/wordsizetree.nim` — `ordered_set/FastSet.py`
### convolution

- [x] `convolution/convolution.nim` — `convolution/NTT.py`
- [x] `convolution/ntt.nim` — `convolution/NTT.py`
- [x] `convolution/xor_convolution.nim` — `bitwise_convolution/SetFunction.py`
### geometry

- [~] `geometry/angle.nim` — Geometry（ユーザー指定で保留）
- [~] `geometry/argsort.nim` — Geometry（ユーザー指定で保留）
- [~] `geometry/base.nim` — Geometry（ユーザー指定で保留）
- [~] `geometry/ccw.nim` — Geometry（ユーザー指定で保留）
- [~] `geometry/distance.nim` — Geometry（ユーザー指定で保留）
- [~] `geometry/intersect.nim` — Geometry（ユーザー指定で保留）
- [~] `geometry/polygon.nim` — Geometry（ユーザー指定で保留）
- [~] `geometry/projection.nim` — Geometry（ユーザー指定で保留）
### graph

- [x] `graph/SCC.nim` — `graph_connectivity/StronglyConnectedComponents.py`
- [x] `graph/bellmanford.nim` — `graph/ShortestPath.py`
- [x] `graph/bipartite_graph.nim` — `graph/ShortestPath.py`
- [x] `graph/dag_minimum_path_cover.nim` — `graph/GraphMatching.py`
- [x] `graph/dijkstra.nim` — `graph/ShortestPath.py`
- [x] `graph/dynamic_bipartite.nim` — `graph/GraphMatching.py`
- [x] `graph/functional_graph.nim` — `graph_connectivity/FunctionalGraph.py`
- [-] `graph/graph.nim` — language support; feature audit is carried by consumers
- [-] `graph/graph_debug.nim` — language support; feature audit is carried by consumers
- [x] `graph/grid_to_graph.nim` — `graph/ExpandedGraph.py`
- [x] `graph/kruskal.nim` — `graph_spanning/MinimumSpanningTree.py`
- [x] `graph/maxk_dijkstra.nim` — `graph/GraphOptimization.py`
- [x] `graph/merge_tree.nim` — `graph_spanning/MergeTree.py`
- [x] `graph/namori_forest.nim` — `graph_connectivity/NamoriDecomposition.py`
- [x] `graph/namori_graph.nim` — `graph_connectivity/NamoriDecomposition.py`
- [x] `graph/range_edge_graph.nim` — `graph/ExpandedGraph.py`
- [x] `graph/restore_shortest_path_from_prev.nim` — `graph/ShortestPath.py`
- [x] `graph/reverse_edge.nim` — `graph/ExpandedGraph.py`
- [x] `graph/steiner_tree.nim` — `graph/GraphOptimization.py`
- [x] `graph/topologicalsort.nim` — `graph/ShortestPath.py`
- [x] `graph/tsp.nim` — `graph/GraphOptimization.py`
- [x] `graph/warshall_floyd.nim` — `graph/ShortestPath.py`
### math

- [-] `math/baser.nim` — language support; feature audit is carried by consumers
- [x] `math/combination.nim` — `math/Combinatorics.py`
- [x] `math/divisor.nim` — `prime/Factorization.py`
- [x] `math/euler_phi.nim` — `prime/Factorization.py`
- [x] `math/ext_gcd.nim` — `math/Combinatorics.py`
- [-] `math/float128.nim` — language support; feature audit is carried by consumers
- [x] `math/fractions.nim` — `math/Structures.py`
- [-] `math/inner_math.nim` — language support; feature audit is carried by consumers
- [-] `math/int128.nim` — language support; feature audit is carried by consumers
- [x] `math/inv_gcd.nim` — `math/Combinatorics.py`
- [x] `math/isprime.nim` — `prime/Factorization.py`
- [x] `math/isqrt.nim` — `number_theory/ModularRoot.py`
- [x] `math/mex_naive.nim` — `math/Structures.py`
- [x] `math/nearest_equiv.nim` — `algorithm/IntegerUtilities.py`
- [x] `math/osa_k.nim` — `prime/Sieve.py`
- [x] `math/powmod.nim` — `algorithm/IntegerUtilities.py`
- [x] `math/primefactor.nim` — `prime/Factorization.py`
- [x] `math/primitive_root.nim` — `number_theory/ModularRoot.py`
- [x] `math/sqrt_heuristic_for_floor_sum.nim` — `algorithm/ModularProgression.py`
- [x] `math/stern_brocot_tree.nim` — `math/Structures.py`
- [x] `math/xor_basis.nim` — `math/Structures.py`
### matrix

- [x] `matrix/matops.nim` — `linear_algebra/Matrix.py`
- [x] `matrix/matrix.nim` — `linear_algebra/Matrix.py`
- [x] `matrix/rolling_hash_2d.nim` — `string/RollingHash2D.py`
- [x] `matrix/static_matrix.nim` — `linear_algebra/Matrix.py`
### modint

- [-] `modint/barrett_impl.nim` — language support; feature audit is carried by consumers
- [-] `modint/exp_modint.nim` — language support; feature audit is carried by consumers
- [-] `modint/modint.nim` — language support; feature audit is carried by consumers
- [-] `modint/montgomery_impl.nim` — language support; feature audit is carried by consumers
### str

- [x] `str/can_reverse_hash_string.nim` — `string/RollingHash.py`
- [x] `str/compressed_trie.nim` — `string/CompressedTrie.py`
- [x] `str/hash_string.nim` — `string/RollingHash.py`
- [x] `str/lcp_naive.nim` — `string/StringSearch.py`
- [x] `str/lcs.nim` — `string/LongestCommonSubsequence.py`
- [x] `str/manacher.nim` — `string/Manacher.py`
- [x] `str/merged_static_string.nim` — `string/StaticString.py`
- [x] `str/palindromic_tree.nim` — `string/PalindromicTree.py`
- [x] `str/rolling_hash.nim` — `string/RollingHash.py`
- [x] `str/run_length_encode.nim` — `string/RunLengthEncoding.py`
- [x] `str/static_string.nim` — `string/StaticString.py`
- [x] `str/zalgorithm.nim` — `string/ZAlgorithm.py`
### tmpl

- [-] `tmpl/citrus.nim` — language support; feature audit is carried by consumers
- [-] `tmpl/optimize.nim` — language support; feature audit is carried by consumers
- [-] `tmpl/qcfium.nim` — language support; feature audit is carried by consumers
- [-] `tmpl/sheep.nim` — language support; feature audit is carried by consumers
### tree

- [x] `tree/cartesiantree.nim` — `sequence_structure/CartesianTree.py`
- [x] `tree/diameter.nim` — `tree/TreeAlgorithms.py`
- [x] `tree/heavylightdecomposition.nim` — `tree/HeavyLightDecomposition.py`
- [x] `tree/prufer.nim` — `tree/PruferCode.py`
- [x] `tree/rerooting.nim` — `tree/Rerooting.py`
### utils

- [x] `utils/binary_search.nim` — `algorithm/Search.py`
- [x] `utils/bititers.nim` — `algorithm/BitAlgorithms.py`
- [-] `utils/constants.nim` — language support; feature audit is carried by consumers
- [x] `utils/cumsum2d.nim` — `data_structure/RectangleQuery.py`
- [x] `utils/grid_searcher.nim` — `graph/ExpandedGraph.py`
- [x] `utils/gridutils.nim` — `graph/ExpandedGraph.py`
- [x] `utils/imos2d.nim` — `data_structure/RectangleQuery.py`
- [x] `utils/inversion_number.nim` — `algorithm/SequenceAlgorithms.py`
- [-] `utils/itertools.nim` — language support; feature audit is carried by consumers
- [x] `utils/knapsack.nim` — `algorithm/DynamicProgramming.py`
- [x] `utils/kth_element.nim` — `algorithm/Search.py`
- [x] `utils/lis.nim` — `algorithm/SequenceAlgorithms.py`
- [-] `utils/list_procs.nim` — language support; feature audit is carried by consumers
- [-] `utils/memo.nim` — language support; feature audit is carried by consumers
- [x] `utils/mo.nim` — `algorithm/RangeQueries.py`
- [-] `utils/random_helper.nim` — language support; feature audit is carried by consumers
- [-] `utils/seqidx.nim` — language support; feature audit is carried by consumers
- [-] `utils/sequtils2D.nim` — language support; feature audit is carried by consumers
