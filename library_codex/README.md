# library_codex

`library` に移す前の試作・検証用ディレクトリです。

- PyPy での実行を前提にする
- 実行速度を優先する
- 原則として再帰を使わない
- 検証コードもこのディレクトリの `verify` に置く

## 現在の完了状況

- 参照スナップショット全 792 ソースのうち、678 件を実装へ対応付け済み
- 言語・runtime support 92 件を監査済み
- Geometry 22 件はユーザー指定により保留
- Geometry を除く未監査項目は 0 件
- PyPy 全検証: 409 passed
- 再帰監査: 2734 functions、direct/mutual recursion なし

対応の正本は `REFERENCE_INVENTORY.md` です。

## APIドキュメント

- [APIリファレンス](docs/README.md): 全142モジュールの公開関数・クラス・メソッドについて、用途・signature・引数・返り値・source位置を掲載
- 1モジュール1ページで、category別の索引から辿れる
- `pypy3 library_codex/tools/build_api_reference.py` でsourceから再生成できる
- `pypy3 library_codex/tools/build_api_reference.py --check` でsourceとの同期を検査できる

## 追加済み

| ファイル | 概要 | 計算量 |
| --- | --- | --- |
| `algorithm/BasicAlgorithms.py` | Fibonacci・転倒数・LIS・0/1 knapsack・subset sum・Mo・doubling | 各標準計算量 |
| `convolution/ArithmeticConvolution.py` | 約数/倍数zeta--Möbius・GCD/LCM畳み込み | $O(N\log\log N)$ |
| `convolution/AdvancedConvolution.py` | Chirp-Z・middle product・多変数通常/巡回・乗法畳み込み | NTT/Bluestein依存 |
| `convolution/FormalPowerSeries.py` | FPS四則演算・inv/log/exp/pow・Taylor shift・一括積 | 主要演算 $O(N\log N)$ |
| `convolution/LinearRecurrence.py` | Berlekamp--Massey・Bostan--Mori・線形漸化式第n項 | BM $O(ND)$、第n項 $O(M(D)\log n)$ |
| `convolution/MultipointEvaluation.py` | 積木による多点評価・多項式補間・連続点補間 | $O(M(N)\log N)$、連続点は $O(N)$ |
| `convolution/NTT.py` | 動的radix-4 NTT・NTT-friendly/任意mod/符号付き整数畳み込み | $O(N\log N)$ |
| `convolution/PolynomialComposition.py` | 高速FPS合成・Brent--Kung fallback・合成逆関数 | $O(N\log^2N)$（NTT法） |
| `convolution/PolynomialAlgorithms.py` | 多項式GCD・resultant・剰余冪・有限体根・部分分数・冪和 | 主要演算はFPS乗除依存 |
| `convolution/SeriesSequences.py` | sparse FPS・Stirling/Bernoulli/Bell/partition・Pascal/Euler変換 | $O(M(N)\log N)$ または疎項数依存 |
| `convolution/SetFunction.py` | subset/superset変換・OR/AND/XOR・subset畳み込み/除算・set power series演算 | $O(N\log N)$ / subset $O(N\log^2 N)$ |
| `data_structure/DisjointSparseTable.py` | 静的列の半群区間積 | 構築 $O(N\log N)$、クエリ $O(1)$ |
| `data_structure/LiChaoTree.py` | 固定座標・動的整数区間のLi Chao Tree（線分・min/max対応） | 直線追加・取得 $O(\log X)$、線分追加 $O(\log^2 X)$ |
| `data_structure/PersistentArray.py` | 分岐可能な永続配列（非再帰・フラットプール） | 取得・更新 $O(\log N)$ |
| `data_structure/PersistentSegmentTree.py` | 汎用演算の永続セグメント木（非再帰） | 更新・区間積 $O(\log N)$ |
| `data_structure/PersistentUnionFind.py` | 完全永続Union Find（非再帰） | 取得・併合 $O(\log^2 N)$ |
| `data_structure/RadixHeap.py` | 単調非負整数キー用優先度付きキュー | 償却 $O(\log C)$ |
| `data_structure/RollbackUnionFind.py` | undo・snapshot・成分和対応Union Find | unite/find $O(\log N)$、undo $O(1)$ |
| `data_structure/SegmentTreeBeats.py` | range chmin/chmax/add/update・range sum/min/max（非再帰） | 構築 $O(N)$、更新はBeatsの償却計算量 |
| `data_structure/StaticRMQ.py` | 静的range minimum・最左argmin | 構築・メモリ $O(N)$、クエリ $O(1)$ |
| `data_structure/WaveletMatrix.py` | 非負整数列のrank・k-th・range frequency | 構築 $O(N\log \sigma)$、クエリ $O(\log \sigma)$ |
| `data_structure/FenwickTree.py` | 1D/動的/2D Fenwick・range add/range sum | 更新・取得 $O(\log N)$、2D $O(\log H\log W)$ |
| `data_structure/SegmentTree.py` | 非可換Segment Tree・Lazy・Dual・境界二分探索 | 各操作 $O(\log N)$ |
| `data_structure/DynamicSegmentTree.py` | 巨大座標の動的/Lazy/Persistent Lazy Segment Tree | 各操作 $O(\log X)$ |
| `data_structure/UnionFind.py` | 通常・動的・重み付き・成分列挙Union-Find | ほぼ $O(\alpha(N))$ |
| `data_structure/SWAG.py` | 非可換SWAG queue/deque・削除可能heap | 償却 $O(1)$ / heap $O(\log N)$ |
| `data_structure/BinaryTrie.py` | multiset・全体xor・k-th・xor min/max | $O(B)$ |
| `data_structure/AdvancedCollections.py` | lazy meldable Skew Heap・矩形union面積 | meld償却 $O(\log N)$ / sweep $O(N\log N)$ |
| `data_structure/FastSet.py` | word-size tree型の固定整数universe ordered set | $O(\log_{64}N)$ |
| `data_structure/RectangleQuery.py` | 2D累積和/Segment Tree/圧縮Fenwick・各種rectangle sum | $O(1)$〜$O(\log^2N)$ |
| `data_structure/Collections.py` | Treap set・区間set・BitSet・永続queue/trie・Top-K和 | 各操作 $O(\log N)$ または $O(B)$ |
| `data_structure/ImplicitTreap.py` | 動的列の挿入削除・反転・非可換積・range lazy作用 | 期待 $O(\log N)$ |
| `graph/BipartiteMatching.py` | 反復Hopcroft--Karp・頂点/独立/辺被覆・DM分解 | $O(E\sqrt V)$ |
| `graph/DijkstraRadixHeap.py` | 非負整数重み用Radix Heap Dijkstra・経路復元 | $O((V+E)\log C)$ |
| `graph/CycleDetection.py` | 有向・無向閉路検出（辺ID、多重辺対応、非再帰） | $O(V+E)$ |
| `graph/EulerianTrail.py` | 有向・無向Euler路・閉路・成分別分解（非再帰） | $O(V+E)$ |
| `graph/FunctionalGraph.py` | Functional graph の周期分解・移動・距離 | 構築 $O(N\log N)$、移動 $O(\log N)$（周期上は $O(1)$） |
| `graph/LowLink.py` | 辺ID付きlowlink・橋・関節点（多重辺対応、非再帰） | $O(V+E)$ |
| `graph/MaxFlow.py` | ACL互換寄りの反復Dinic・min-cut・辺変更 | Dinicの計算量 |
| `graph/MinCostBFlow.py` | lower/upper・頂点supply・負費用対応minimum-cost b-flow | cost scaling法 |
| `graph/MinCostFlow.py` | 非負費用のポテンシャル付き最小費用流・slope | $O(FE\log V)$ |
| `graph/MinimumSpanningTree.py` | Kruskal最小全域森・最小全域木（辺ID付き） | $O(E\log E)$ |
| `graph/NamoriDecomposition.py` | 重み付き擬森林の周期・付随木分解と距離 | 構築 $O(V+E)$、距離 $O(\log V)$ |
| `graph/OfflineDynamicConnectivity.py` | 辺追加削除・連結性・成分和のオフライン処理 | $O((Q+K)\log Q\log N)$ |
| `graph/OnlineDynamicConnectivity.py` | splay Euler Tour Tree＋HDT level昇格による完全動的連結性 | amortized polylogarithmic |
| `graph/TwoEdgeConnectedComponents.py` | 二辺連結成分・橋森・辺の成分対応 | $O(V+E)$ |
| `graph/ShortestPath.py` | BFS/0-1 BFS/Dijkstra/Bellman--Ford/Floyd・復元・topological sort | 各標準計算量 |
| `graph/StronglyConnectedComponents.py` | 反復Kosaraju・縮約DAG | $O(V+E)$ |
| `graph/BiconnectedComponents.py` | 二重頂点連結成分・block-cut forest（自己ループ・平行辺対応） | $O(V+E)$ |
| `graph/GraphEnumeration.py` | 彩色数・厳密最大独立集合・三角形/C4/全clique列挙 | $O(N2^N)$ または出力依存 |
| `graph/GraphOptimization.py` | Hungarian・Steiner木・Held--Karp TSP・Dial Dijkstra・有向最小全域木 | 各標準計算量 |
| `graph/KShortestPaths.py` | 有向/無向k-shortest loopless path（辺ID・平行辺対応） | Yen法 $O(KN(E+V)\log V)$ |
| `graph/GraphProperties.py` | Chordal認識・誘導閉路証拠・二部グラフ最小辺彩色 | MCS $O(V+E)$、彩色は反復matching |
| `graph/GraphMatching.py` | 一般blossom・2-SAT・動的二部判定・DAG最小path cover | blossom $O(V^3)$、ほか標準計算量 |
| `graph/ExpandedGraph.py` | Range Edge Graph・多次元grid・reverse/grid変換 | 区間辺 $O(\log N)$ 補助辺 |
| `graph/GraphCounting.py` | 彩色多項式・有向/無向全域木数・有向Euler閉路数 | subset法 / Matrix--Tree / BEST定理 |
| `graph/GraphOrdering.py` | 木制約最適順序・st-numbering・全辺replacement shortest path | $O(N\log N)$ / $O(N+M)$ / $O((N+M)\log N)$ |
| `graph/AdvancedConnectivity.py` | 三辺連結成分・辺追加offline SCC統合列 | $O(N+M)$ / $O((N+M)\log M)$ |
| `graph/MergeTree.py` | 先読みunion tree・現在成分の連続葉区間 | 構築 $O((N+Q)\alpha(N))$ |
| `math/ChineseRemainder.py` | 非互いに素な法のCRT・balanced bigint CRT・法付きGarner | 通常 $O(K\log M)$、Garner $O(K^2)$ |
| `math/Combinatorics.py` | factorial/binomial・拡張GCD・floor sum・商区間・Gray code | 各標準計算量 |
| `math/BlackBoxLinearAlgebra.py` | dense/sparse/作用素の最小多項式・巨大冪・行列式・線形方程式 | Krylov列生成 $O(NT)$、BM $O(N^2)$ |
| `math/AdvancedMatrix.py` | 合成数法行列式・Hafnian/Pfaffian・Matrix-Tree | determinant/Pfaffian $O(N^3)$、Hafnian $O(N^3 2^{N/2})$ |
| `math/F2Matrix.py` | Python int bit-rowのGF(2)行列・AND-XOR/AND-OR積・逆行列 | 掃き出し $O(HW)$ big-int演算 |
| `math/Matrix.py` | 動的法の行列演算・rank/det/inverse/連立方程式・特性多項式 | 密行列主要演算 $O(N^3)$ |
| `math/ModularArithmetic.py` | Tonelli--Shanks平方根・拡張BSGS離散対数 | $O(\log^2 P)$ / $O(\sqrt M)$ |
| `math/ModularRoot.py` | 素数法k乗根・原始根・整数floor/ceil k乗根 | 法k乗根 $O(\min(P,K)^{1/4})$、整数根 $O(\log A)$ |
| `math/PolynomialMatrix.py` | 多項式行列式・$\det(A+xB)$・多項式行列prefix積・多項式Matrix-Tree | 評価補間 / BSGS |
| `math/Structures.py` | Affine・XOR基底・Stern--Brocot・DAG Grundy・Fraction | 各標準計算量 |
| `math/NumberTheoryExtras.py` | tetration・Gaussian整数・二平方和・二次方程式・有理探索 | 各標準計算量 |
| `math/SATSolver.py` | watched literal型の反復SAT solver | 問題依存 |
| `math/AlgebraExtras.py` | semiring・Pisano・q-binomial・浮動/有理binomial | 各標準計算量 |
| `prime/Factorization.py` | deterministic Miller--Rabin・Brent型Pollard Rho・約数/phi/Möbius | 64-bit確率的分解 |
| `prime/Sieve.py` | 線形sieve・LPF/Möbius/φ・Lucy素数計数・square-free個数 | $O(N)$ / sublinear counting |
| `optimization/Optimization.py` | Monotone Minima・凸min-plus・CHT・最大長方形・整数黄金分割 | 各参照計算量 |
| `optimization/ProjectSelection.py` | binary/K値Project Selection・高次all-0/all-1 profit | 1回のmin-cutへ帰着 |
| `optimization/SlopeTrick.py` | 重み付きSlope Trick・shift/slide/chmin/merge/eval | 更新はheap償却 $O(\log N)$ |
| `optimization/AdvancedDP.py` | Monge DP・凸/凹min/max-plus・branch-and-bound・rollback Mo | 各参照計算量 |
| `optimization/Matroid.py` | graphic/partition/transversal matroid intersection | oracle依存の多項式時間 |
| `game/GameTheory.py` | 不偏DAG Grundy・numeric partisan game・dyadic surreal | 状態・遷移数に線形 |
| `random/RandomGraph.py` | xoshiro256**・graph container・各種random graph | 出力サイズに線形 |
| `heuristic/Heuristics.py` | SA・multipoint SA・bandit・Top-K・log乱数表 | iteration依存 |
| `string/AhoCorasick.py` | dict/固定alphabet対応Aho--Corasick（軽量・pattern別集計） | 固定alphabet構築 $O(V\sigma)$、集計 $O(T)$、列挙 $O(T+M)$ |
| `string/CompressedTrie.py` | 辺ラベルを元の語の区間で持つ圧縮Trie | 追加・検索 $O(L)$、ノード数 $O(U)$ |
| `string/DynamicRollingHash.py` | 点更新・反転hash対応segment tree | 更新・取得 $O(\log N)$ |
| `string/LongestCommonSubsequence.py` | bit-parallel LCS長・反復Hirschberg復元 | 長さ $O(N\lceil M/w\rceil)$ word演算 |
| `string/Manacher.py` | 奇数・偶数半径・全中心極大回文列挙 | $O(N)$ |
| `string/PalindromicTree.py` | オンラインEertree（頻度・位置・復元対応） | dict期待 $O(N)$、固定alphabet $O(N\sigma)$ |
| `string/PersistentString.py` | 64要素葉の永続AVL rope（split/concat/repeat） | 構築 $O(N)$、編集 $O(\log N)$ |
| `string/PrefixSubstringLCS.py` | prefix対substringのオフラインLCS | $O(NM\log M+Q\log M)$ |
| `string/RollingHash.py` | $2^{61}-1$ 静的hash・連結・反転・LCP | 構築 $O(N)$、取得 $O(1)$ |
| `string/RollingHash2D.py` | フラット配列による2次元矩形hash | 構築 $O(HW)$、取得 $O(1)$ |
| `string/RunLengthEncoding.py` | 任意iterableの連長圧縮・復元 | $O(N)$ |
| `string/RunEnumeration.py` | 最小周期付き極大run列挙（反復分割統治） | $O(N\log N)$ |
| `string/StringSearch.py` | Suffix Arrayによるsubstring LCP・比較・検索 | 構築 $O(N)$、LCP・比較 $O(1)$ |
| `string/StaticString.py` | SA共有substring view・複数view連結 | 同一baseのLCP $O(1)$、index $O(\log K)$ |
| `string/Subsequence.py` | 異なる部分列数・部分列判定 | 期待 $O(N)$ |
| `string/SuffixArray.py` | 非再帰SA-IS・LCP・検索・静的部分文字列比較 | 構築 $O(N)$、LCP $O(1)$ |
| `string/SuffixAutomaton.py` | オンライン構築・出現/辞書順/LCS対応Suffix Automaton | 構築 $O(N)$、検索 $O(L)$ |
| `string/Trie.py` | dict/固定alphabet対応Trie（重複・prefix件数・ID保持） | 追加・検索 $O(L)$ |
| `string/WildcardPatternMatching.py` | 両側wildcard対応の決定的pattern matching | $O(KN\log N)$、$1\le K\le3$ |
| `string/ZAlgorithm.py` | 空列・任意sequence対応Z Algorithm | $O(N)$ |
| `tree/HeavyLightDecomposition.py` | Heavy-Light Decomposition（非再帰） | 構築 $O(N)$、LCA・パス分解 $O(\log N)$ |
| `tree/LinkCutTree.py` | Link-Cut Tree（非可換path積・遅延作用・可換群部分木積・部分木加算和） | 各操作 amortized $O(\log N)$ |
| `tree/PruferCode.py` | Prüfer列の線形encode/decode（標準・拡張形式） | $O(N)$ |
| `tree/StaticTopTree.py` | 辺/頂点cluster Static Top Tree・動的tree DP・reroot DP | 構築 $O(N\log N)$、更新 $O(\log N)$ |
| `tree/TreeAlgorithms.py` | Euler Tour・virtual/Cartesian/rooted/inclusion/merge tree・重み付き直径 | 主に $O(N)$、virtual tree $O(K\log K)$ |
| `tree/Rerooting.py` | 非可換monoid・辺/頂点変換対応の全方位木DP | $O(N)$ |
| `tree/CentroidDecomposition.py` | 重心分解・点加算/距離範囲和Fenwick | 構築 $O(N\log N)$、更新/取得 $O(\log^2N)$ |
| `tree/DSUOnTree.py` | Euler区間を用いるDSU on Tree | $O(N\log N)$ 回のadd/remove |
| `tree/DynamicDiameter.py` | Static Top Treeによる固定木の動的重み付き直径 | 構築 $O(N\log N)$、辺更新 $O(\log N)$ |
| `tree/TreeIsomorphism.py` | 衝突なしAHU分類・128-bit木hash・中心/重心 | 構築 $O(N\log N)$、高次数以外は実質線形 |
| `tree/TreeDistanceFrequency.py` | 木の全頂点対距離の度数分布 | centroid＋整数NTT $O(N\log^2N)$ |

### Wavelet Matrix API

- `access(k)` / `wm[k]`: 元の列の `k` 番目
- `rank(l, r, x)`: `[l, r)` にある `x` の個数
- `kth_smallest(l, r, k)` / `kth_largest(l, r, k)`: 0-indexed k-th
- `count_lt(l, r, x)` / `count_le(l, r, x)`: `< x` / `<= x` の個数
- `range_freq(l, r, upper)` または `range_freq(l, r, lower, upper)`
- `prev_value(l, r, upper)` / `next_value(l, r, lower)`: `< upper` の最大値 / `>= lower` の最小値

### Segment Tree Beats API

- `range_chmin(l, r, x)` / `range_chmax(l, r, x)`
- `range_add(l, r, x)` / `range_update(l, r, x)`
- `range_sum(l, r)` / `range_min(l, r)` / `range_max(l, r)`
- `get(p)` / `set(p, x)`

### Li Chao Tree

- `LiChaoTree(xs, minimize=True)`: クエリ座標を先に与える配列版
- `DynamicLiChaoTree(left, right, minimize=True)`: 整数半開区間 `[left, right)` の動的版
- `add_line(a, b)`: $y=ax+b$ を全域へ追加
- `add_segment(a, b, l, r)`: $y=ax+b$ を `[l,r)` へ追加
- `query(x)`: `x` における最小値または最大値

### Radix Heap

- `push(key, value)`: `key >= 最後にpopしたkey` が必要
- `pop()` / `top()`: 最小キーの `(key, value)`
- `dijkstra_radix_heap(edge, start=0, goal=None)`: 非負整数重み専用、到達不能は `-1`
- `dijkstra_radix_heap_restore(edge, start=0)`: 距離と親配列を返す

### Persistent data structures

- 初期状態のversionは `0`。更新元versionを指定すると任意の過去から分岐する
- `PersistentArray.get(i, version)` / `set(i, x, version)`
- `PersistentUnionFind.unite(x, y, version)` / `same` / `size` / `components`
- `PersistentSegmentTree.set/add(i, x, version)` / `prod(l, r, version)`
- Persistent Arrayの既定 `shift=2` はPyPyの時間・メモリ実測に基づく

### Rollback Union-Find / Offline Dynamic Connectivity

- `RollbackUnionFind.merge/same/size/get_state/undo/snapshot/rollback`
- 初期頂点値を渡すと `add_value(v, delta)` / `component_sum(v)` もrollback対象になる
- `OfflineDynamicConnectivity(n, q, values=None)` は時刻 `0 <= t < q` を先に確保
- `add_edge(t,u,v)` / `remove_edge(t,u,v)` は多重辺・自己ループ・同時刻の複数操作に対応
- `query_same` / `query_size` / `query_components` / `query_component_sum` を登録し、`solve()` で登録順の答えを返す
- 同じ時刻の変更は登録順にすべて反映され、その時刻の問い合わせは変更後の状態を見る
- `run(query, add=None, remove=None)` では各時刻のUnion Findと、必要なら全域森のlink/cut callbackを受け取れる
- 時間セグメント木は再帰せず、区間項目もフラット配列に格納

### Online Fully Dynamic Connectivity

- `OnlineDynamicConnectivity(n).link(u,v)` / `cut(u,v)` / `connected(u,v)` を操作順に即時処理する
- `component_size(v)` と `component_count`、多重辺・自己ループに対応する
- `link` は全域森へ入った辺、`cut` は `ForestCutQuery(forest_cut,forest_link)` を返すため、外部のforest集約も同期できる
- Euler Tour Treeのsplay nodeは整数IDの平行配列で保持し、HDTのtree/non-tree edge level昇格でreplacementを探す
- level再帰はcutフレームを積んで逆順処理し、splay・探索・昇格を含めすべて非再帰
- 30頂点×各1万操作を毎回BFS・全域森と比較。10万頂点path＋5万代替辺の交互cutは約3.6秒・RSS約334MiB

### Link-Cut Tree

- `LinkCutTree(values, op, identity)` は非可換monoidの向きを保って `link/cut/evert/path_fold`、LCA、親、path上k-thを処理する
- `LazyLinkCutTree` は `mapping(action, aggregate, length)` と `composition(new, old)` を追加し、`path_apply` を処理する
- `SubtreeLinkCutTree` は可換群の `subtree_fold(node, root)`、`SubtreeAddLinkCutTree` は数値の `subtree_add/subtree_sum` を処理する
- nodeは整数ID、splayは平行配列、祖先pushも明示stackで、相互・直接再帰を使わない
- 動的forestを愚直BFSと2.2万操作比較。10万頂点path構築＋5千path積はPyPyで約0.6秒・RSS約83MiB

### Static Top Tree

- `StaticTopTree` / `StaticTopTreeEdgeBased` はrootのdummy edgeを含む辺cluster、`StaticTopTreeVertexBased` はPath/Pointを分離した頂点clusterを構築する
- `DynamicTreeDP` / `EdgeTopTreeDP` / `VertexTopTreeDP` は元の頂点または辺からcluster rootまでだけ再計算する
- `DynamicRerootingDP.get(v)` はclusterを作り直さず、任意の頂点をrootとした答えを返す
- heavy pathの依存順処理、重み平衡merge、初期DP評価はすべて反復処理。10万頂点pathでも再帰を使わない

### Tree utility / DP

- `EulerTour` はforest対応LCA・subtree区間、`AuxiliaryTree` は選択点と必要LCAだけのvirtual treeを返す
- `Rerooting` は隣接順を保つ非可換mergeと辺情報に対応し、各頂点rootの答えと各辺両側のDPを保持する
- `CentroidDistanceFenwick` は頂点値の点加算/代入と、頂点から距離 `[l,r)` にある値の和を処理する
- `DSUOnTree.run(add, query, remove)` はlight/ heavy処理をイベントstackで実行する
- `DynamicDiameter.update(u,v,w)` は固定木の辺重みを更新し、`get()` で直径長と端点を返す（非負重み）

### Static RMQ

- `query(l, r)` / `prod(l, r)`: `[l,r)` の最小値
- `argmin(l, r)`: 最小値を取る最左の添字
- 100万要素では既存Sparse Tableより構築が約2.9倍高速、RSSは半分以下
- クエリ単体は既存Sparse Tableの方が約2倍高速なので、メモリ・構築時間との使い分けを想定

### Graph basics

- MST系の辺は `(u, v, weight)`、Euler/cycle系の辺は `(u, v)`
- `minimum_spanning_forest`: `(cost, edge_ids, component_count)`
- `minimum_spanning_tree`: 非連結なら `None`、連結なら `(cost, edge_ids)`
- `eulerian_trail` / `eulerian_cycle`: `(vertices, edge_ids)` または `None`
- `eulerian_trails`: 弱連結成分ごとのEuler路へ分解し、グローバル辺IDを維持
- `find_cycle`: 閉路上の `(vertices, edge_ids)`。自己ループ・無向多重辺にも対応

### Bipartite Matching

- `BipartiteMatching(left_size, right_size)` に `add_edge(left, right)` して `solve()`
- `pairs()` / `maximum_matching()` はマッチした `(left, right)` の列
- `minimum_vertex_cover()` / `maximum_independent_set()` は左右の頂点番号を分けて返す
- `minimum_edge_cover()` は孤立点があれば `None`、なければ最小辺被覆
- `dulmage_mendelsohn()` は右頂点を `left_size` だけずらした全体頂点番号で返す
- BFS・増加路探索・DM分解はすべて非再帰

### LowLink / Two-Edge-Connected Components

- `LowLink(n, edges)`、または `LowLink(n)` に `add_edge(u, v)` して `build()`
- `order` / `low` / `articulation` / `bridge_ids` / `bridges` を保持
- 親の頂点ではなく親の辺IDだけを除外するため、自己ループ・平行辺にも対応
- `TwoEdgeConnectedComponents` の `component[v]` / `groups` が成分番号・頂点集合
- `tree` は成分を頂点、橋を辺にした森。`bridge_forest(True)` で元の辺IDも返す
- `edge_mapping[e]` は橋なら `-1`、それ以外なら所属する二辺連結成分番号
- すべてのDFSと成分列挙は明示スタック

### Biconnected / Graph enumeration

- `BiconnectedComponents` は辺ID単位の二重頂点連結成分と関節点を構築し、`BlockCutTree` は非連結グラフをforestとして保持する
- `chromatic_number` は独立集合数の包除原理、`maximum_independent_set` は補グラフの色数上界付き厳密探索を使う
- `enumerate_triangles` / `enumerate_cliques` はcallback処理に対応し、指数個の結果を保持せず逐次処理できる
- `count_c4_per_edge` は各辺を含む4-cycleの個数または他3辺の重み積和を $O(N+M\sqrt M)$ で返す
- 探索・lowlink・列挙はすべて明示stackで、再帰を使わない

### Graph optimization / properties

- `hungarian` は長方形行列と負費用、`minimum_steiner_tree` は辺ID復元、`minimum_cost_arborescence` は負辺・平行辺に対応する
- `held_karp_path/cycle` は経路復元、`dial_dijkstra` は多始点と親復元に対応する
- `k_shortest_paths_directed/undirected` は単純路を `(cost, vertices, edge_ids)` で返し、同費用や平行辺を区別する
- `ChordalGraphRecognizer` はPEOまたは誘導閉路を返し、`bipartite_edge_coloring` は多重辺を最大次数色で彩色する
- 縮約展開・DP復元・Yen分岐・MCS・証拠探索はすべて非再帰

### Graph matching / expansion

- `GeneralMatching` は一般無向グラフの最大cardinality matchingを blossom 縮約で求める
- `TwoSAT` は clause/implication/equality/xor、`DynamicBipartiteGraph` は追加辺制約と各成分の大きい側の合計を処理する
- `dag_minimum_path_cover` は頂点をちょうど1回覆う最小本数の有向pathを復元する
- `RangeEdgeGraph` は point/range の4通りの有向辺を表現し、元頂点IDを保つ
- `DimensionExpandedGraph` は任意次元gridのflatten/近傍と BFS・0-1 BFS・Dijkstra を提供する

### Graph counting / tree distance

- `chromatic_polynomial` は独立集合への順序付き分割を subset power projection で数え、通常の冪基底係数へ変換する
- `count_directed_spanning_trees` は根へ向かう/根から離れる両向き、`count_undirected_spanning_trees` は重み・多重度に対応する
- `count_eulerian_circuits` は有向多重グラフの次数釣合いと BEST 定理を使う
- `frequency_table_of_tree_distance` は異なる頂点の unordered pair 数を距離ごとに返し、1万頂点のpathでも再帰を使わない

### Graph ordering / advanced connectivity

- `optimal_tree_topological_order` は親が子より先という制約下の全pair目的関数を厳密最小化する
- `bipolar_orientation` はst-number、`shortest_path_without_each_edge` は各辺削除後の距離をまとめて返す
- `ThreeEdgeConnectedComponents` は多重辺対応で二辺/三辺連結成分を同時に保持する
- `incremental_scc_offline` の時刻別辺IDをDSUへ適用すると、各prefixのSCC分割と一致する
- lowlink吸収・分割統治・復元・最短路木走査はすべて非再帰

### Namori decomposition

- `NamoriDecomposition(n, edges)`。辺は `(u,v)` または `(u,v,weight)`
- 各連結成分が木またはちょうど1周期の擬森林を対象とし、2周期以上なら `ValueError`
- 自己ループを長さ1、平行2辺を長さ2の周期として扱う
- `cycles` / `cycle_edge_ids` / `cycle_weights` は同じ順序で周期を保持
- `component_id[v]` / `root(v)` / `in_cycle(v)` / `same_tree(u,v)` で所属を取得
- `distances(u,v)` は単純路の重みを昇順の `(短い方, 長い方)` で返す
- 単純路が1本なら第2要素、非連結なら両要素が `None`
- `hop_distances`、付随木内の `lca/tree_distance/kth_ancestor/jump_tree/path/path_ordered/subtree` に対応
- 葉刈り・周期抽出・付随木HLDはすべて非再帰

### Tree isomorphism / Prüfer code

- `RootedTreeIsomorphism(tree, root, interner=None)` は子の型ID列を使う衝突なしAHU分類
- 同じ木の `class_id[v]` は根付き部分木の同型類。別の木と厳密比較するときは同じ `AHUInterner` を渡す
- `rooted_tree_isomorphic` / `unrooted_tree_isomorphic` は共有internerを内部で作る厳密判定
- `hash[v]` と `tree_hash(tree)` は独立構築間でも比較できる固定128-bit確率的hash
- `tree_hash` は木の中心1個なら同じhashを2個、中心2個なら両根のhashをソートして返す
- `tree_center` は直径の中心、`tree_centroid` は削除後の最大成分サイズを最小化する重心
- `prufer_encode(tree)` / `prufer_decode(code, n=None)` は長さ `n-2` の標準Prüfer列
- `prufer_encode_extended` / `prufer_decode_extended` はtko919版互換の末尾 `n-1` 付き形式
- Prüfer変換はheapを使わないポインタ法で $O(N)$、木処理もすべて非再帰

### Suffix Array / LCP

- `suffix_array(s, upper=None)` は `str` / `bytes` / 任意の比較可能な列を受け取る
- 非ASCII Unicodeと負整数列は座標圧縮し、bytesは0〜255を直接SA-ISへ渡す
- `sa_is(s, upper)` の縮約列処理も明示フレームで、再帰を使わない
- 通常は空suffixを含めず、`suffix_array_with_empty` / `SuffixArray.with_empty()` で先頭に追加
- `SuffixArray` は `sa/rank/lcp` と既存互換名 `SA/RSA/LCP` を保持
- `lcp_suffix` / `lcp_substring` / `compare_suffix` / `compare_substring`
- LCP RMQは初回問い合わせ時だけ線形メモリの `StaticRMQ` を構築し、以後 $O(1)$
- `search(pattern)` は一致するSA半開区間、`count` / `occurrences` / `distinct_substrings` も提供
- 検索は両端LCPを引き継ぎ、文字比較 $O(|pattern|+\log N)$
- `substring(l,r)` の `StaticSubstring` は同じbase上でLCP・比較・sliceを行う

### Rolling Hash

- 法はMersenne素数 $2^{61}-1$、既定baseはプロセス開始時の時刻seedから生成
- `RollingHash(s).get(l,r)` は単一hashを速度優先で返す
- `DoubleRollingHash` は独立な2基数のtupleを返し、より低い衝突確率が必要な場合に使う
- `ReversibleRollingHash` / `get_value` は正逆hashを持つ `HashString` を返す
- `HashString` は連結、反転、回文判定、二分累乗による反復、prefix除去に対応
- `RollingHashView` はslice、LCP、辞書順比較を行い、`extend` で静的hashの末尾追加も可能
- 文字、bytes、負整数を同じ法へ正規化。異なるobjectの比較には同じbaseを使う
- `DynamicRollingHash` は点更新、区間正逆hash、回文判定、LCPを反復segment treeで処理
- `RollingHash2D.get(u,l,d,r)` は矩形hash、`find(pattern)` は2次元パターン位置を列挙
- 全実装で再帰を使わない。hash一致は確率的判定であり、厳密判定が必要なら元データも確認する

### Trie / Aho--Corasick

- `Trie()` は任意のhash可能な記号をdict遷移で扱い、`Trie(alphabet)` は固定alphabetをフラットな `array('i')` で持つ
- `add/find/count/contains/prefix_count/erase`、終端ID、挿入済みprefix列挙に対応する
- `CompressedTrie` は辺文字列を複製せず、挿入した元の語の半開区間で参照する。格納中の可変sequenceは変更しないこと
- `AhoCorasick.add(pattern, pattern_id)` 後に `build()` すると固定alphabet版はfailure遷移も補完する
- `count_matches` は全一致数、`count_by_pattern` はfailure木の逆順加算で各patternの一致数を返す
- `finditer` / `match_positions` はoutput linkだけを辿るため、各頂点へ終端ID列を複製しない
- 重複patternと空patternに対応し、空patternは長さ $T$ の本文に $T+1$ 回一致する
- 構築・failure木・照合・圧縮辺の分割はすべて非再帰

### Suffix Automaton

- `SuffixAutomaton(sequence, alphabet=None)` は任意のhash可能な記号をdict遷移で扱う
- 固定alphabetを渡すと遷移をフラットな `array('i')` にし、速度とメモリを優先する
- `extend/push/build` でオンライン追加でき、`find/contains/count/first_occurrence/occurrences` で部分文字列を検索する
- `length/link/first_pos/origin/is_clone/prefix_states` と長さ順 `topological_order`、suffix-link木を公開する
- `distinct_substrings`、異なる部分文字列の長さ総和、`kth_substring`、出現回数別の最長反復部分文字列に対応する
- `longest_common_substring(other)` は `(長さ, base内の開始位置, other内の開始位置)` を返す
- 出現位置列挙はsuffix-link木のEuler順を遅延構築し、固定patternのendpos部分木だけを走査する
- 50万文字・26文字alphabetでは約67.6万状態を1.24秒、100万文字・二値列では約113万状態を0.93秒で構築した
- clone生成、suffix-link伝播、Euler順、長さ順整列を含めて再帰を使わない

### Z Algorithm / Run Enumeration

- `z_algorithm(sequence)` は `z[i] = LCP(sequence, sequence[i:])` を返し、空列では空listを返す
- 既存の綴りとの互換用に `Z_algorithm` / `Z_algorism`、一般的な別名 `z_function` も持つ
- `run_enumerate(sequence)` は `(period, left, right)` を返し、`sequence[left:right]` は最小周期 `period` を持つ極大run
- runの長さは `2 * period` 以上。左右へ同じ周期を保って延長できず、同一区間の複数周期は最小周期だけを返す
- 出力は `(period, left, right)` の昇順で重複せず、run数は文字列長以下
- Nyaan版の分割統治＋Z Algorithmを明示スタック化し、長さ2の区間は直接処理する
- 50万byteでは非周期寄り入力を約0.53秒・RSS約96MiB、周期5の入力を約1.94秒・RSS約168MiBで列挙した
- Z Algorithm、分割統治、候補統合のすべてで再帰を使わない

### Manacher / Palindromic Tree

- `manacher` / `manacher_even` は各文字中心の奇数半径と、各文字直前を中心とする偶数半径を返す
- `enumerate_palindrome_lengths` はYosupo形式で全 `2N-1` 中心の極大回文長を返し、`Manacher` はその別名
- `enumerate_palindromes` は空の偶数中心を含む半開区間、`get_palindromes` は存在しない偶数中心を `(-1,-1)` にする
- `enumerate_leftmost_palindromes()[r-1]` は右端 `r` の回文のうち最小の左端を返す
- `PalindromicTree(sequence, alphabet=None)` はdict遷移、固定alphabet指定時はフラットな `array('i')` 遷移を使う
- `extend/push`、回文からの `find/count/first_occurrence/occurrences`、回文復元、最長回文、suffix列挙に対応する
- `direct_count` は各prefixで最長回文suffixになった回数、`occurrence_counts` はsuffix-link逆伝播後の全出現回数
- `total_count` は重複込み回文部分文字列数、`distinct_count` は異なる非空回文数
- 100万文字の26文字乱択では約2911回文を0.35秒、全同一文字では100万回文ノードを1.16秒で構築した
- suffix探索、頻度伝播、suffix-link木のEuler順、Manacherを含めて再帰を使わない

### LCS / remaining string utilities

- `lcs_length(a,b)` は記号ごとのbit maskとPython任意長整数でLCS長をword並列計算する
- `restore_lcs(a,b)` は同じbitset DP列を使う明示スタックHirschberg法で、LCSを元のcontainer型に復元する
- 記号がhash不能な場合だけ通常の1行DPへfallbackし、復元メモリは短い側の長さに比例する
- `PrefixSubstringLCS.add(a,b,c)` は `LCS(first[:a], second[b:c])` を登録し、`run()` が登録順に返す
- Prefix--Substring版はqueryのないセルへ空listを作らず、prefix行ごとの疎なbucketだけを保持する
- `StringSearch` は `SuffixArray` 上の互換APIで、suffix/substringの `lcp/strcmp` とpattern検索を提供する
- `count_distinct_subsequences(sequence, mod=None)` は空部分列を除く異なる部分列数。`include_empty=True` にも対応する
- `run_length_encode` / `run_length_decode` はiterator、文字列、bytes、tupleを扱う
- 10万対10万のLCS長は約1.64秒、2万対2万のLCS復元は約0.25秒、100万要素のmod付き部分列数は約0.01秒
- LCS復元・Prefix--Substring走査を含め、すべて再帰を使わない

### Persistent / Static String

- `PersistentString` は最大64要素の葉と永続AVL ropeを使い、旧versionと部分木を共有する
- `substr` / `+` / `inserted` / `deleted` / `replaced` は非破壊、`insert` / `+=` / `*=` は現在のwrapperだけを更新する
- `*` は二分累乗したropeをDAG共有するため、長さ $2^{60}$ の反復文字列も $O(\log z)$ 個の共有段で表現できる
- 添字アクセス、slice、materialize、LCP、辞書順比較に対応し、`MaxSize()` は $2^{60}$
- `StaticStringBase` はSuffix Array/LCPを一度だけ構築し、`StaticString` は同じbaseの半開区間をコピーせず保持する
- 同一baseのview間は初回RMQ構築後LCP・比較 $O(1)$。異なるbaseでは衝突のない直接比較へfallbackする
- `MergedStaticString` は複数viewを累積長付きで持ち、indexを二分探索、sliceを境界viewだけ作り直して返す
- `to_static_strings` は複数sequenceを一つのbaseへ載せ、`init_suffix_array` はsuffix view列を返す
- 長さ20万の構築は約0.03秒、長さを20万に保つcopy-paste 10万回は約1.02秒、10万partのMerged LCPは約0.02秒
- AVL join/split、構築、materialize、巨大DAGの添字探索を含めて再帰を使わない

### NTT / convolution / wildcard matching

- `NumberTheoreticTransform(mod, root=None)` は法ごとに原始根とradix-4 butterfly用の定数を構築し、`get_ntt` が再利用する
- `convolution_ntt(a,b,mod)` はNTT-friendly prime用、`convolution(a,b,mod)` は直接NTTと3法CRTを自動選択する
- `convolution_any_mod` は任意の正の法、`convolution_int` は符号付き整数の正確な畳み込みを返す
- CRTは $469762049,1811939329,2013265921$ を使い、係数上界が積以上（符号付きは積の半分以上）なら誤答にせず `OverflowError` を送出する
- `wildcard_pattern_matching(text,pattern,wildcard=0)` は本文・patternの両方のwildcardと任意sequenceに対応し、空patternは全 $N+1$ 位置で一致する
- 各位置の非一致度を $\sum (x-y)^2$ として畳み込み、値域から求めた上界に応じて1〜3法だけを使うため、hash衝突のない決定的判定になる
- 各法では6回のforward NTTの周波数成分を先に合算し、inverse NTTを1回に抑える
- PyPy実測で50万×50万の998244353畳み込みは約0.39秒、20万×20万の任意mod畳み込みは約0.56秒、本文50万・pattern25万のwildcard照合は約0.87秒
- 原始根探索、butterfly、CRT、照合のすべてで再帰を使わない

### Formal Power Series / linear recurrence

- 既定法は $998244353$。`mod` を変える場合も係数環が体であることを前提とし、逆元が存在しない定数・主係数は例外にする
- `fps_add/subtract/negate/multiply`、`fps_derivative/integral/evaluate` が基本演算を提供する
- `fps_inverse/logarithm/exponential/power(series, degree, mod)` は指定した `degree` 項を返し、NTT可能な法ではNewton法とradix-4 butterflyを直接再利用する
- `fps_square_root` は先頭0の偶奇と定数項のTonelli--Shanksを処理し、平方根がなければ `None`、あれば指定次数の根を返す
- `fps_quotient/remainder/divmod` は末尾の0を除いた多項式として除算し、長い除数ではreverse＋FPS逆元を使う
- `fps_taylor_shift(f,c)` は $f(x+c)$、`fps_product` は長さの短い多項式からheapで併合する
- 積分・Taylor shiftは必要な整数の逆元を使うため次数が `mod` 未満であることが必要
- `berlekamp_massey(sequence)` は $a_n=\sum_{i=1}^D c_i a_{n-i}$ の `[c1,...,cD]`、`berlekamp_massey_polynomial` は `[1,-c1,...,-cD]` を返す
- `bostan_mori(n,P,Q)` は $[x^n]P(x)/Q(x)$、`linear_recurrence_nth(initial,coefficients,n)` は既知の漸化式、`nth_term(n,sequence)` はBMで推定した最小漸化式から第n項を求める
- Bostan--Moriは $\deg P\ge\deg Q$ の多項式部分、定数有理式、巨大indexにも対応する
- PyPy実測で20万次のFPS逆元は約0.32秒、expは約0.49秒、5万項漸化式の第 $10^{18}$ 項は約4.62秒（最大RSS約108MiB）
- Newton反復、BM、Bostan--Mori、多項式積の併合を含めて再帰を使わない

### Polynomial composition / compositional inverse

- `fps_compose(outer,inner,degree,mod)` は `outer(inner(x)) mod x^degree` を返す
- NTT可能な法ではNyaan版の $O(N\log^2N)$ アルゴリズムを明示フレーム化し、各段の周波数配列を再計算してPythonでの保持メモリを抑える
- NTT長を確保できない法ではBrent--Kung型へfallbackし、64次以下はHorner法を使う
- `composition(inner,outer,...)` は参照ライブラリ互換の引数順、`fps_compose` は一般的なouter-first順
- `fps_compositional_inverse(f)` は $f(0)=0,f'(0)\ne0$ に対し、合成Newton法で $f(g(x))=x$ となる $g$ を返す
- 定数・恒等写像・線形写像は専用分岐で $O(N)$。非自明な2万次逆関数はPyPyで約3.20秒、検算合成は約0.82秒、RSS約98MiB
- 高速合成の下降・復元、平方根・逆関数Newton反復を含めて再帰を使わない

### Multipoint Evaluation / Interpolation

- `ProductTree(points, mod)` は $\prod_i(x-x_i)$ と全区間積を一度構築し、`evaluate` と `interpolate` で再利用できる
- `multipoint_evaluation(f,xs)` は重複する評価点も許し、空多項式は全点で0を返す
- 評価は上段を多項式剰余で分割し、残余の次数または区間長が64以下になった下段をHorner法へ切り替える
- `polynomial_interpolation(xs,ys)` は相異なる点から次数 $N$ 未満・長さちょうど $N$ の係数列を復元する
- 補間分母 $M'(x_i)$ の逆元はprefix積による一括逆元で求め、`pow` は全体で1回だけ使う
- 同じ法で一致する点があれば `ValueError`、体でなく必要な逆元が存在しなければ `ZeroDivisionError` を送出する
- `interpolate_consecutive(ys,t)` は $f(0),\ldots,f(N-1)$ から $f(t)$ を $O(N)$ で求める
- PyPy実測の10万点では積木構築約0.65秒、多点評価約2.11秒、補間約2.62秒、最大RSS約148MiB
- 積木構築、剰余伝播、補間の下からの合成はすべて非再帰

### CRT / modular arithmetic / factorization

- `chinese_remainder(residues,moduli)` は負の剰余・非互いに素な法を扱い、解を標準形 `(remainder,lcm)`、不整合なら `(0,0)` で返す
- `chinese_remainder_balanced` / `garner_bigint` は合成を平衡木状に行い、多数の法で巨大整数の偏った成長を避ける
- `garner_mod(residues,moduli,target_modulus)` はpairwise coprimeな法から、積全体を作らずtarget法での値だけを求める
- `modular_square_root(a,p)` は素数法のTonelli--Shanksで、小さい方の平方根、存在しなければ `-1` を返す
- `discrete_logarithm(a,b,m)` は $a^x\equiv b\pmod m$ の最小非負 $x$ を返し、$\gcd(a,m)>1$ と $m=1$ にも対応する
- `is_prime` は $0\le n<2^{64}$ で決定的な7基底Miller--Rabin、`pollard_rho` は128個ずつgcdするBrent法
- `prime_factors/factor_count/divisors/euler_phi/mobius` は明示スタックで64-bit整数を処理する
- PyPy実測で法 $10^9+7$ の離散対数は約0.010秒、難しい64-bit合成数4個の分解は合計約0.074秒、1000法balanced CRTは約0.019秒
- CRT合成、BSGS、Pollard分割、素因数分解、約数列挙を含めて再帰を使わない

### Matrix / black-box linear algebra

- `matrix_multiply/matrix_power/matrix_vector_multiply` は法を引数で受け、入力行列を変更しない
- `gauss_elimination` はrank・行列式・変形済み行列・pivot列を返し、`reduced=True` でRREFを作る
- `inverse_matrix` は特異なら `None`、`linear_equation` は `(particular, kernel_basis)` または `None` を返す
- `sparse_linear_equation(dict_rows,b,width,mod,elimination_band)` は疎な行を密配列化せず、自由変数を0とした解を返す
- `characteristic_polynomial` はHessenberg相似変換から $\det(xI-A)$ の昇冪係数を $O(N^3)$ で求める
- `SparseMatrix` / `LinearOperator` と通常の二重listを同じblack-box APIへ渡せる
- `black_box_minimal_polynomial/power/determinant/linear_solve` は乱択Krylov列とBerlekamp--Masseyを使い、`seed/trials` を指定できる
- PyPy実測で350次特性多項式は約0.21秒、1200次・約3600非零要素の $A^{10^{18}}b$ は約0.78秒
- `determinant_arbitrary_mod` は逆元を使わないEuclid消去、`F2Matrix` は各行を1個のPython整数で保持する
- `hafnian` は多項式縮約を明示スタック化し、`pfaffian` は交代行列を2行ずつ消去する
- `spanning_tree_count` と `directed_spanning_tree_count` は重み付きMatrix-Tree theoremを適用する
- PyPy実測で20次Hafnianは約0.24秒、2000次GF(2) rankは約0.58秒、300次合成数法determinantは約0.36秒
- `polynomial_matrix_determinant` は行ごとの次数上界まで評価補間し、`determinant_a_plus_xb` は正則点shiftと特性多項式で三次計算する
- `polynomial_matrix_prefix_product(M,k)` は $M(k-1)\cdots M(0)$ を連続標本shiftとbaby-step/giant-stepで求める
- `spanning_tree_polynomial` は辺重みが多項式のMatrix-Tree theoremに対応する
- PyPy実測で3次・次数4・100万項prefix積は約0.44秒、200次 $\det(A+xB)$ は約0.34秒
- PyPy実測で帯幅5・1万元の疎連立方程式は約0.18秒・RSS約67MiB
- Hessenberg化、掃き出し、Krylov列、BM、作用素冪を含めて再帰を使わない

### Modular / integral roots

- `modular_kth_root(a,k,p)` は素数 `p` 上で $x^k=a$ の解を1つ返し、存在しなければ `-1`
- 離散対数全体を解かず、$\gcd(k,p-1)$ の素因数ごとに一般化Tonelli--Shanksと再利用BSGSを行う
- `primitive_root(p)` は $p-1$ をdeterministic Miller--Rabin / Pollard Rhoで分解して最小候補から原始根を探す
- `floor_kth_root(a,k)` / `ceil_kth_root(a,k)` は任意精度非負整数に対応し、積が `a` を越えた時点で打ち切る
- PyPy実測で61-bit素数上の生成済み法k乗根2000件は約0.27秒、整数5乗根10万件は約0.25秒
- 素数冪根の補正、BSGS、整数二分探索を含めて再帰を使わない

### Set function / arithmetic convolution

- `subset_zeta_transform/subset_mobius_transform` と `superset_*` は長さが2冪の配列をin-place変換し、同じ配列を返す
- `mod=None` は整数上の正確な加減算、`mod` 指定時は入口で標準剰余へ正規化する
- `walsh_hadamard_transform` と `bitwise_or/and/xor_convolution` は既存の固定法XOR版を一般化し、入力を変更しない
- `SubsetConvolution(mod).multiply/divide/transpose_multiply` はranked zetaをフラット配列で処理する
- subset除算は $B[\varnothing]$ が可逆なとき、$A=B*C$ を満たす $C$ を返す
- `set_series_exponential` は $f[\varnothing]=0$、`set_series_logarithm` は $f[\varnothing]=1$ のset power seriesで互いに逆になる
- `set_series_composition(outer, series)` は定数項を含む多項式とset power seriesの合成を返す
- `set_series_power_projection(series, weights, terms)` は $\langle series^k,weights\rangle$ を $0\le k<terms$ について一括計算する
- 合成とpower projectionは同じ非再帰block DPの互いに転置な演算として実装し、計算量は $O(n^2 2^n)$
- `divisor_zeta/mobius_transform` は約数和、`multiple_zeta/mobius_transform` は倍数和をin-place変換する。添字0は未使用
- `gcd_convolution` / `lcm_convolution` は正の添字だけを対象とし、返り値の添字0を0にする
- PyPy実測でsubset $N=2^{18}$ は約0.72秒・RSS約141MiB、set series合成＋19項projectionは約2.35秒・RSS約148MiB
- XOR $N=2^{20}$ は約0.45秒、GCD/LCM $N=10^6$ は約0.13/0.11秒
- ranked変換、set seriesのblock反復、素数ごとの約数・倍数変換を含めて再帰を使わない

### Flow

- `MaxFlowGraph.add_edge/get_edge/edges/change_edge`
- `MinCostBFlow(n).add_edge(u,v,lower,upper,cost)` は負費用・自己ループ・負のlowerにも対応する
- `add_supply(v,b)` の符号は `outflow-inflow=b`。需要は `add_demand(v,b)` で追加する
- `run()` は `(feasible,total_cost)`、成功後は `get_flow(edge_id)` と最適性証明用 `dual` を取得できる
- 実装はDinicでlower boundの実行可能流を作り、残余グラフを非再帰cost-scaling circulationで最適化する
- 小容量6000ランダムケースを全フロー列挙と比較。1万頂点・約2万辺の帯状輸送はPyPyで約6.7秒・RSS約102MiB
- `flow(s, t, limit=None)` / `min_cut(s)`
- Dinicの増加路探索も明示スタックで、深いグラフに再帰制限なし
- `MinCostFlowGraph` の辺費用は非負整数。`flow` と限界費用ごとの `slope` に対応
- Min Cost Flowの0 reduced-cost辺は専用スタックで処理し、ヒープ操作を削減

### Optimization

- `monotone_minima(rows,columns,value=...)` は行ごとのargminが単調な暗黙行列を明示区間スタックで探索する
- `convex_min_plus_convolution(arbitrary,convex)` と両側convexの差分merge版に対応する
- `MonotoneConvexHullTrick` はmin/max・傾き昇順/降順を指定し、整数交差だけで追加 $O(1)$ 償却・query $O(\log N)$
- `LineContainer` は任意順の直線を既定64-bit整数座標域の動的Li Chao Treeで処理する
- `ProjectSelection` はunary/submodular pair/all-zero/all-one項、`KProjectSelection` はMonge pair costをmin-cutへ変換する
- `maximal_rectangle` / `maximal_rectangle_binary`、閉整数区間の `golden_section_search` も反復実装
- 小規模Project Selectionをbinary/K値とも全割当列挙で比較。単調CHT20万本＋20万query・100万棒・5万変数min-cutの連続実行は約0.48秒・RSS約120MiB
- `WeightedSlopeTrick` は重み付きhinge/abs、座標・値shift、区間slide、左右chmin、merge、任意点evalを持つ
- 同じ座標の重みを個数として保持し、重みを要素へ展開しない。50万 weighted更新は約2.44秒・RSS約100MiB
