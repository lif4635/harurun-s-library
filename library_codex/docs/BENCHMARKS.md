# 実装の比較記録

[公式ケースの反復測定一覧](../../verify/library_checker/benchmarks/README.md) · [比較条件と手順](LIBRARY_CHECKER_COMPARISON.md)

以下は測定時点の記録。比較には各文書の入力、実行環境、source revisionを使い、現在の実装の速度と混同しない。

## グラフ・木

- [辺追加最小全域森](INCREMENTAL_MSF_BENCHMARK.md)
- [彩色多項式](CHROMATIC_POLYNOMIAL_BENCHMARK.md)
- [二部グラフの辺彩色](BIPARTITE_EDGE_COLORING_BENCHMARK.md)
- [有向最小全域木の速度とメモリ](ARBORESCENCE_BENCHMARK.md)
- [木の距離分布の速度とメモリ](TREE_DISTANCE_FREQUENCY_BENCHMARK.md)
- [オイラー閉路の数え上げ](DECIMAL_ADDITION_BENCHMARK.md)
- [動的木のパス積・動的グラフの成分加算](DYNAMIC_TREE_BENCHMARK.md)
- [最大流・最小費用b-flow](FLOW_BENCHMARK.md)
- [SCC・一般マッチング](GRAPH_ALGORITHMS_BENCHMARK.md)
- [CodonとPyPyのSCC・2-SAT比較](../../verify/library_checker/codon/README.md)
- [木分解・st-numbering・マンハッタンMST・k本の最短walk](GRAPH_DECOMPOSITION_BENCHMARK.md)
- [彩色・クリーク・独立集合・C4・Steiner木・chordal判定](GRAPH_ENUMERATION_BENCHMARK.md)
- [木の距離範囲和・区間最頻値・群の差](TREE_RANGE_BENCHMARK.md)
- [二部マッチング・区間Union-Find・部分木クエリ](LIBRARY_CHECKER_COMPARISON.md)

## データ構造・範囲クエリ

- [区間転倒数の一括処理と都度問い合わせ](RANGE_INVERSIONS_BENCHMARK.md)
- [永続区間アフィン変換・版間の区間コピー](PERSISTENT_AFFINE_BENCHMARK.md)
- [動的列・区間頻度](DATA_STRUCTURE_BENCHMARK.md)
- [BinaryTrie・Stern–Brocot木](BINARY_TRIE_PERFORMANCE.md)
- [Wavelet Matrix・一次式加算・区間加算](RANGE_QUERY_BENCHMARK.md)
- [区間代入・巨大配列](AFFINE_RANGE_BENCHMARK.md)
- [二次元の加算・範囲和](SPATIAL_QUERIES_BENCHMARK.md)
- [Deque・木の最小転倒数](DEQUE_TREE_ORDER_BENCHMARK.md)
- [区間過半数・nim積](NIMBER_MAJORITY_BENCHMARK.md)

## 数論・多項式・線形代数

- [平方因子を持たない整数の計数](SQUARE_FREE_BENCHMARK.md)
- [固定法の離散対数](FIXED_DISCRETE_LOG_BENCHMARK.md)
- [2冪法の乗法畳み込み](MULTIPLICATIVE_CONVOLUTION_POW2_BENCHMARK.md)
- [巨大整数の10進・16進乗算](BIG_INTEGER_MULTIPLICATION_BENCHMARK.md)
- [巨大整数の商・余り](BIG_INTEGER_DIVISION_BENCHMARK.md)
- [線形漸化式の遠くの連続項](CONSECUTIVE_RECURRENCE_BENCHMARK.md)
- [素数の個数](PRIME_COUNT_BENCHMARK.md)
- [φ関数の総和](TOTIENT_SUM_BENCHMARK.md)
- [等比重み付き多項式和の速度とメモリ](POLYNOMIAL_EXPONENTIAL_SUM_BENCHMARK.md)
- [多変数の循環畳み込み](MULTIDIMENSIONAL_CONVOLUTION_BENCHMARK.md)
- [巨大整数の10進・16進加算](DECIMAL_ADDITION_BENCHMARK.md)
- [凹列のmin-plus畳み込み](MINPLUS_CONCAVE_BENCHMARK.md)
- [多項式の評価・補間・累積和](POLYNOMIAL_SAMPLING_BENCHMARK.md)
- [多項式の合成逆・剰余・因数分解](POLYNOMIAL_ALGORITHMS_BENCHMARK.md)
- [任意法・q二項係数](BINOMIAL_BENCHMARK.md)
- [整数・有理数](NUMBER_THEORY_BENCHMARK.md)
- [行列積・行列累乗](MATRIX_ALGORITHMS_BENCHMARK.md)
- [余因子行列](ADJUGATE_BENCHMARK.md)
- [F₂連立方程式・空間交差・長方形の和集合面積](F2_AND_RECTANGLE_BENCHMARK.md)

## 文字列・幾何

- [三角形内の点数え上げ](TRIANGLE_POINT_COUNT_BENCHMARK.md)
- [文字列・両端回文木](STRING_ALGORITHMS_BENCHMARK.md)
- [最近点対](CLOSEST_PAIR_BENCHMARK.md)
