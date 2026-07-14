# Roadmap

4ライブラリのファイル名をそのまま集めるのではなく、同じ機能の別実装をまとめた上で
PyPy向けに移植する。比較の基準にしたスナップショットは次の通り。

| library | commit |
| --- | --- |
| NachiaVivias/cp-library | `82b31d5` |
| tko919/library | `3478d17` |
| NyaanNyaan/library | `b3981ad` |
| kemuniku/cplib | `8c61d81` |

## Staging済み

- [x] Fibonacci / inversion count / LIS / knapsack / subset sum / Mo / doubling
- [x] Combination / ext-gcd / signed floor-sum / quotient enumeration / Gray code
- [x] Linear sieve / LPF・Möbius・φ / prime counting / square-free counting
- [x] Affine / XOR basis / Stern--Brocot / DAG Grundy
- [x] Disjoint Sparse Table
- [x] Li Chao Tree（固定座標・動的整数区間、line/segment、min/max）
- [x] Persistent Array / Union Find / Segment Tree
- [x] Radix Heap / Radix Heap Dijkstra
- [x] Segment Tree Beats（chmin/chmax/add/update・sum/min/max）
- [x] Static RMQ（線形構築・線形メモリ・O(1) query）
- [x] Wavelet Matrix（静的・非負整数）
- [x] Heavy-Light Decomposition
- [x] Functional Graph
- [x] Kruskal / minimum spanning forest / minimum spanning tree
- [x] Eulerian Trail / Cycle Detection
- [x] Max Flow / Min Cost Flow（非負費用標準版）
- [x] Bipartite Matching（被覆・Dulmage--Mendelsohn分解を含む）
- [x] LowLink / Two-Edge-Connected Components（多重辺・橋森対応）
- [x] Rollback Union Find / Offline Dynamic Connectivity（多重辺・成分和対応）
- [x] Namori decomposition（重み付き擬森林・自己ループ・平行辺対応）
- [x] Tree Hash / AHU isomorphism / Prüfer Code（衝突なし判定・線形変換）
- [x] Suffix Array / LCP（非再帰SA-IS・検索・StaticSubstring）
- [x] Rolling Hash（静的/連結/反転・動的segment tree・2次元）
- [x] Trie / Aho-Corasick（dict/固定alphabet・圧縮Trie・軽量/個別集計）
- [x] Suffix Automaton（オンライン構築・出現位置・k-th・LCS）
- [x] Z Algorithm / Run Enumeration（最小周期・極大区間・非再帰分割統治）
- [x] Manacher / Palindromic Tree（奇偶中心・オンライン頻度・位置・復元）
- [x] LCS / Prefix-Substring LCS（bit-parallel長・反復Hirschberg復元）
- [x] String Search / subsequence count / Run-Length Encoding
- [x] Persistent String / Static-Merged String（永続AVL rope・共有SA view）
- [x] NTT / arbitrary-mod convolution / Wildcard Pattern Matching
- [x] Formal Power Series core（四則・inv/log/exp/pow・Taylor shift・一括積）
- [x] Berlekamp--Massey / Bostan--Mori / linear recurrence
- [x] Multipoint Evaluation / Polynomial Interpolation（再利用可能な積木・連続点補間）
- [x] CRT / Garner / modular square root / discrete logarithm
- [x] Deterministic Miller--Rabin / Brent Pollard Rho（64-bit・非再帰分解）
- [x] Subset/superset Zeta--Möbius / OR--AND--XOR / Subset Convolution
- [x] Divisor/multiple transform / GCD--LCM Convolution
- [x] Chirp-Z / multidimensional DFT / multivariate・multiplicative convolution
- [x] FPS square root / polynomial composition / compositional inverse
- [x] Set Power Series composition / exponential / power projection
- [x] Modular k-th root / primitive root / integral k-th root
- [x] Dense Matrix / characteristic polynomial / black-box linear algebra
- [x] Arbitrary-mod determinant / GF(2) Matrix / Hafnian / Pfaffian
- [x] Polynomial Matrix determinant / prefix product / polynomial Matrix-Tree
- [x] Sparse/banded linear equation / fixed-size and SIMD matrix feature equivalents
- [x] Minimum Cost b-flow（lower/upper bound・負費用・頂点supply）
- [x] Online Fully Dynamic Connectivity（splay ETT＋HDT、多重辺対応）
- [x] Convex Hull Trick / Monotone Minima / convex min-plus convolution
- [x] Binary/K-value Project Selection / Maximum Rectangle / integer golden search
- [x] Weighted Slope Trick（shift/slide/chmin/merge/eval）
- [x] Link-Cut Tree（非可換path積・path遅延作用・部分木積・部分木加算和）
- [x] Static Top Tree（辺/頂点cluster・動的tree DP・reroot DP）
- [x] Tree utility 群（Euler Tour・virtual/Cartesian/inclusion/merge tree・diameter）
- [x] Rerooting / Centroid Decomposition / distance-range Fenwick / DSU on Tree
- [x] Dynamic Diameter（固定木・辺重み点更新）
- [x] Fenwick / Segment / Lazy / Dual / dynamic / persistent-lazy Segment Tree
- [x] Union-Find（通常・動的・重み付き・列挙）/ SWAG / Binary Trie / FastSet
- [x] 2D cumulative/Fenwick/Segment・static/dynamic rectangle sum・rectangle add/sum
- [x] Treap ordered set / interval set / BitSet / Persistent Queue・Binary Trie / Top-K sum
- [x] Partial Persistent / Range Parallel / contiguous / monoid Union-Find
- [x] Implicit Treap sequence（insert/erase/reverse/noncommutative fold/lazy action）
- [x] Generic shortest paths / SCC / topological sort / graph component utilities
- [x] Biconnected Components / Block-Cut Forest
- [x] Chromatic Number / exact Maximum Independent Set / Triangle・Clique・C4 enumeration
- [x] Hungarian / Steiner / Held--Karp / Dial Dijkstra / minimum-cost arborescence
- [x] Directed・undirected K-shortest loopless paths
- [x] Chordal recognition / bipartite edge coloring
- [x] General blossom matching / 2-SAT / dynamic bipartite / DAG path cover
- [x] Range Edge Graph / dimension-expanded grid graph
- [x] Chromatic Polynomial / Matrix-Tree / BEST Euler-circuit count
- [x] Frequency table of all tree distances（centroid＋integer NTT）
- [x] Optimal tree topological order / bipolar orientation / replacement paths
- [x] Three-edge-connected components / offline incremental SCC
- [x] Polynomial GCD/ext-GCD/resultant/mod-pow/root finding / partial fractions
- [x] Famous/sparse FPS / Stirling・Bernoulli・partition・Bell / Pascal・Euler transforms
- [x] Tetration / Gaussian integer / two-square representations / quadratic equation
- [x] Merge tree / integer partitions / modular progression splitting / EGZ task
- [x] Monge DP / concave min-plus / branch-and-bound / rollback Mo
- [x] General SAT / impartial・numeric partisan games / short surreal numbers
- [x] Graphic・partition・transversal matroid intersection
- [x] Random graph generator / simulated annealing helpers / multi-armed bandit / Top-K
- [x] Semiring recurrence / Pisano period / q-binomial / rational・floating binomial

## 完了状況

- [x] Geometry を除く参照機能の監査・実装対応
- [x] PyPy 全検証（409 tests）
- [x] direct / mutual recursion 監査（2734 functions）
- [~] Geometry 22 件はユーザー指定により保留

この一覧は優先順位用。全792ソースの完了判定は `REFERENCE_INVENTORY.md` を正とし、
各項目を追加するたびに参照元とローカル実装の対応を `[x]` へ更新する。

## 追加時の確認

1. `library` に同等機能がないか、既存APIを壊さず併存できるか確認する。
2. 再帰を使わず、標準ライブラリだけで動くPyPy向け実装にする。
3. 非可換演算、空・単要素、深い木など、その構造固有の端ケースを検証する。
4. 小さいランダムケースを愚直解と比較し、大きいケースで再帰・速度・メモリを確認する。
5. 合意されるまでは `library_codex` の外へ移さない。
