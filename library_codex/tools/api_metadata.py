"""Human-authored semantics used by the source-derived API reference.

The implementation modules stay annotation-light for contest use.  Details
that cannot be recovered safely from the AST live here so the generated docs
and the website share one reviewable source of truth.
"""


# 正式名・source・説明からは拾いにくい通称だけを置く。
SEARCH_TERMS_BY_MODULE = {
    "fps998/MultipointEvaluation.py": (
        "高速多点評価",
        "multipoint evaluation",
        "積木",
        "subproduct tree",
    ),
    "segment_tree/LazySegTree.py": (
        "遅延セグ木",
        "lazy segtree",
        "区間更新",
        "遅延評価",
    ),
    "fenwick_tree/BIT.py": (
        "BIT",
        "binary indexed tree",
        "累積和",
    ),
    "convolution/MinPlusConvolution.py": (
        "高速minplus",
        "min-plus convolution",
        "凸畳み込み",
        "Monge",
    ),
}


SEARCH_TERMS_BY_SYMBOL = {
    ("combinatorics/Combination.py", "catalan"): (
        "カタラン数",
        "投票問題",
        "ballot path",
    ),
    ("segment_tree/LazySegTree.py", "max_right"): (
        "境界探索",
        "右端二分探索",
        "区間二分探索",
    ),
    ("segment_tree/LazySegTree.py", "min_left"): (
        "境界探索",
        "左端二分探索",
        "区間二分探索",
    ),
    ("convolution/MinPlusConvolution.py", "minplus_conv"): (
        "一般列 凸列",
        "monotone minima",
        "argmin",
    ),
    ("convolution/MinPlusConvolution.py", "minplus_conv_convex"): (
        "凸列 凸列",
        "線形時間",
        "差分merge",
    ),
}


MODULE_CAPABILITIES = {
    "fps998/MultipointEvaluation.py": (
        "998244353 上の多項式を、与えられたすべての点で一括評価できる。",
        "積多項式を NTT 表現のまま保持し、root の逆数を一度だけ作って評価情報を積木へ伝播する。",
    ),
    "algorithm/DynamicProgramming.py": (
        "0/1 knapsackの各重さに対する最大価値と、容量以内の最大価値を求められる。",
        "非負整数のsubset sumをPython整数bitsetで判定し、実際に選ぶ添字も復元できる。",
    ),
    "algorithm/SequenceAlgorithms.py": (
        "列の転倒数と最長増加部分列を O(N log N) で求められる。",
        "値を大小関係を保つ順位へ圧縮し、重なる区間を併合できる。",
    ),
    "random/Random.py": (
        "seedから再現可能な整数・真偽値・実数を高速に生成できる。",
        "テスト用の配列・bit列・行列・文字列・置換・重複なし標本を直接作れる。",
        "合計値を固定した非負または正の整数列を一様なcompositionとして生成できる。",
    ),
    "random/RandomGraph.py": (
        "ランダム木・path・star・cycle・forestをedge-listで生成できる。",
        "辺数を固定した単純・連結・二部graph、Erdős–Rényi graph、単閉路graphを生成できる。",
        "生成結果を隣接list・隣接行列・競プロ入力用文字列へ変換できる。",
    ),
    "fps/FormalPowerSeries.py": (
        "昇冪係数列で形式的冪級数の加減乗除・微分・積分を行える。",
        "逆数・対数・指数・冪・平方根を指定した次数まで計算できる。",
        "法998244353ではroot表と逆変換係数を再利用するradix-4 NTT高速経路が自動で使われる。",
        "多項式除算、Taylor shift、合成などの高水準処理へそのまま渡せる係数列を返す。",
    ),
    "convolution/NTT998.py": (
        "998244353固定の係数畳み込みを、汎用mod判定やCRTを通さずradix-4 NTTで計算できる。",
        "順NTTと正規化済み逆NTTを破壊的に適用し、変換済み係数列を再利用できる。",
        "同じ係数列同士では専用のsquareを使い、順変換を1回に減らせる。",
    ),
    "fps998/FPS.py": (
        "998244353固定のFPSについて、加減算・微分・積分・評価・多項式除算を計算できる。",
        "逆元・対数・指数・整数冪・平方根を指定した係数数まで高速に求められる。",
        "Taylor shiftと複数多項式の一括積も、固定NTTだけを使って計算できる。",
    ),
    "fps998/Composition.py": (
        r"998244353上でFPS合成 $f(g(x))$ と合成逆関数を計算できる。",
    ),
    "fps998/PowerProjection.py": (
        r"多項式 $f$ の各冪 $f^i$ と重み列の係数内積を、複数の $i$ についてまとめて計算できる。",
    ),
    "fps998/LinearRecurrence.py": (
        "Berlekamp--Masseyで列から最短線形漸化式を推定できる。",
        "Bostan--Moriで有理FPSの巨大添字係数や線形漸化式の第n項を求められる。",
    ),
    "fps998/SubsetSum.py": (
        "重さごとの種類数から、部分集合または多重集合の総重さ別の選び方を生成できる。",
    ),
    "fps998/NTT2D.py": (
        "2次元係数行列へ順NTT・正規化済み逆NTTを適用できる。",
        "2変数多項式の係数畳み込みを長方形の2次元listで計算できる。",
    ),
    "fps/IncreasingSequences.py": (
        r"各位置で $\mathrm{lower}_i \le x_i < \mathrm{upper}_i$ を満たす広義単調増加列 $x_0 \le \cdots \le x_{N-1}$ の個数を求める。",
    ),
    "combinatorial_series/StirlingNumbers.py": (
        r"固定した $n$ に対する第一種・第二種 Stirling 数の行を $0 \le k \le n$ の順に生成できる。",
        r"固定した $k$ に対する第一種・第二種 Stirling 数を $0 \le n \le \mathrm{upper}$ の順に生成できる。",
    ),
    "convolution/NTT.py": (
        "NTT可能な法の上で係数列を高速に畳み込める。",
        "順変換・逆変換を明示的に実行し、変換済み配列を再利用できる。",
        "法と原始根を指定して、標準設定以外のNTTも構築できる。",
    ),
    "convolution/MinPlusConvolution.py": (
        "一方または両方が凸な列のmin-plus畳み込みを高速に計算する。",
        "一般列×凸列はmonotone minima、凸列×凸列は差分列のmergeで処理する。",
        "一般列との畳み込みでは、必要なら最小値を作った凸列側の添字も返せる。",
    ),
    "optimization/ConvexConcaveConvolution.py": (
        "凹列と一般列のmax-plus畳み込みを高速に計算する。",
        "空でない入力には長さlen(concave)+len(arbitrary)-1の列を返す。",
        "必要なら最大値を作った凹列側の添字も同時に返せる。",
    ),
    "fenwick_tree/BIT.py": (
        "1次元列の一点加算とprefix和・半開区間和を O(log N) で処理できる。",
        "区間加算・区間和、疎な添字空間、2次元矩形和の各Fenwick構造を選べる。",
        "累積和が目標値以上になる最初の位置を O(log N) で探索できる。",
    ),
    "segment_tree/SegTree.py": (
        "任意の結合的演算で一点更新・半開区間集約を O(log N) で処理できる。",
        "add(index, value)で一点をop(value, current)へ更新でき、非可換演算でも順序が固定される。",
        "文字列結合や行列積のような非可換演算でも、左から右の順序を保って集約できる。",
        "prefixの集約値に対する単調な条件を使い、条件が崩れる最初の境界を O(log N) で探せる。",
    ),
    "segment_tree/LazySegTree.py": (
        "半開区間全体への作用と、半開区間の集約値取得をどちらも O(log N) で処理できる。",
        "add(index, value)で遅延作用を反映してから一点をop(value, current)へ更新できる。",
        "区間加算・区間和、区間代入・区間最小などを、mapping・composition・作用の単位元idを指定して構成できる。",
        "一点更新・一点取得に加え、max_right・min_leftによる集約値の境界探索も使える。",
    ),
    "segment_tree/DualSegTree.py": (
        "半開区間全体へ作用を適用し、指定した一点の現在値を O(log N) で取得できる。",
        "区間集約を保持しないため、区間更新と一点取得だけが必要な場合にLazy Segment Treeより単純で軽い。",
        "複数の作用はcompositionで順序を保って合成し、何もしない作用をidで明示できる。",
    ),
    "segment_tree/MaxInterval.py": (
        "数列の区間和、最大部分配列和、最小部分配列和を1つのマージ可能な値として保持できる。",
        "max_interval_segment_treeで数列を構築すると、一点更新後の全体の最大・最小部分配列和を O(log N) で取得できる。",
        "部分区間をSegmentTree.prodで集約し、その区間内の最大部分配列和をmaximumから取得できる。",
    ),
    "segment_tree/DynamicSegmentTree.py": (
        "巨大な整数座標区間で一点更新と半開区間集約を O(log W) で処理できる。Wは座標幅。",
        "add(index, value)で一点をop(value, current)へ更新でき、更新経路を1回だけ辿る。",
        "更新で通った経路だけnodeを確保するため、実際に触る座標が少ない問題でmemoryを節約できる。",
        "未設定の位置はidentityとして扱い、座標圧縮なしで疎な値を保持できる。",
    ),
    "segment_tree/DynamicLazySegmentTree.py": (
        "巨大な整数座標区間で区間作用と区間集約を O(log W) で処理できる。Wは座標幅。",
        "必要になったnodeだけを生成し、疎な座標空間へ区間加算・区間和などを適用できる。",
        "通常のLazy Segment Treeと同じop・mapping・compositionの形で構成できる。",
    ),
    "segment_tree/PersistentLazySegmentTree.py": (
        "巨大な整数座標区間への区間作用ごとに新しいversionを作り、過去versionを壊さず保持できる。",
        "任意versionから枝分かれした更新を作り、指定versionの半開区間集約を取得できる。",
        "変更経路だけをcopyするため、配列全体をversionごとに複製せず履歴を保存できる。",
    ),
    "union_find/UnionFind.py": (
        "要素の併合、同一連結成分判定、代表元と成分sizeの取得をほぼ定数時間で行える。",
        "連結成分数を保ちながら、辺追加だけの連結性問題を処理できる。",
    ),
    "range_query/WaveletMatrix.py": (
        "静的な数列に対するk番目、順位、頻度、前後の値を対数時間で取得できる。",
        "位置の半開区間と値域を同時に指定した問い合わせを処理できる。",
        "圧縮版を使えば大きな整数座標を値の種類数に応じたbit幅で保持できる。",
    ),
    "graph/CSRGraph.py": (
        "辺をCSR形式の連続配列へ格納し、隣接listより省メモリに走査できる。",
        "各アルゴリズムへCSRGraphだけでなく通常の隣接listもそのまま渡せる。",
        "Dijkstra・BFS・SCC・LowLinkなどを非再帰で計算できる。",
    ),
    "graph/ShortestPath.py": (
        "BFS・0-1 BFS・Dijkstra・Bellman–Fordなどを入力グラフに合わせて選べる。",
        "最短距離だけでなく直前頂点も取得し、始点からの経路を復元できる。",
        "全点対最短路や負閉路を含む問題にも対応できる。",
    ),
    "graph_flow/MaxFlow.py": (
        "容量付き有向グラフの最大流を計算できる。",
        "辺ごとの流量と残余容量を確認し、最小カット側の頂点集合を取得できる。",
    ),
    "linear_algebra/Matrix.py": (
        "list of listsで表した行列の加減算・乗算・累乗を行える。",
        "行列式、逆行列、線形方程式を法上または通常の数値上で計算できる。",
    ),
    "optimization/Optimization.py": (
        "monotone minima、SMAWK、divide-and-conquer DP最適化を使える。",
        "ヒストグラム・二値行列の最大長方形を線形時間で求められる。",
        "黄金分割探索とConvex Hull Trickで1変数最適化を高速化できる。",
    ),
    "prime/Factorization.py": (
        "64bit整数の素数判定とPollard's rhoによる素因数分解を行える。",
        "素因数の重複列・指数表・約数列を用途に応じて取得できる。",
        "Eulerのφ関数とMöbius関数を素因数分解結果から計算できる。",
    ),
    "string/SuffixArray.py": (
        "文字列または整数列のsuffix arrayとLCP配列を構築できる。",
        "patternに一致するsuffixの範囲を二分探索し、出現位置を列挙できる。",
    ),
    "tree/HeavyLightDecomposition.py": (
        "木をheavy pathへ分解し、頂点path・辺pathを少数の半開区間へ変換できる。",
        "LCA、頂点間距離、k個先の頂点、部分木区間を取得できる。",
        "Segment Treeなどと組み合わせてpath query・subtree queryを処理できる。",
    ),
    "tree/LCA.py": (
        "lca = LCA(tree, root) と構築し、lca(u, v)で最近共通祖先を取得できる。",
        "dist(u, v)で2頂点間の辺数距離を取得できる。",
        "森にも対応し、異なる連結成分の2頂点には-1を返す。",
    ),
}

MODULE_CAPABILITIES.update({
    "algorithm/PermutationGroup.py": (
        "置換の生成元から、点を後ろから順に固定する安定化列の代表置換を構築できる。",
        "各levelの代表元数を掛け合わせて、生成された有限置換群の要素数を求められる。",
        "全levelを平坦化すると、入力と同じ置換群を生成する置換listとして再利用できる。",
    ),
    "convolution/MiddleProduct.py": (
        r"長い列 $a$ と短い列 $b$ から、$c_i=\sum_j b_j a_{i+j}$ をまとめて計算できる。",
        "998244353では、長い列の長さ以上の最小の2冪だけを使う循環NTTで計算する。",
    ),
    "ordered_set/RangeSet.py": (
        r"整数集合を、互いに交わらない半開区間 $[\mathrm{left},\mathrm{right})$ の列として保持できる。",
        "半開区間の一括追加・一括削除、1点の包含判定、指定値以上のmexを処理できる。",
    ),
    "algorithm/IntegerUtilities.py": (
        "非負整数の整数n乗根を、浮動小数点数を使わず正確に求められる。",
        "integer_nth_rootはNewton法でfloor(number^(1/degree))を返す。",
    ),
    "geometry/Orientation.py": (
        "2本の2次元ベクトルの符号付き外積を求められる。",
        "3点が反時計回り・時計回り・一直線のどれかを判定できる。",
    ),
    "geometry/SegmentIntersection.py": (
        "2本の閉線分が交差・接触・重複するかを判定できる。",
        "touch=Falseなら端点で触れるだけの場合を交差から除外できる。",
    ),
    "geometry/ConvexHull.py": (
        "2次元点集合の凸包を反時計回りの頂点列として構築できる。",
        "重複点を除去し、必要なら凸包の辺上にある点も残せる。",
    ),
    "geometry/ArgumentSort.py": (
        "2次元ベクトルを正のx軸から反時計回りの偏角順に並べられる。",
        "浮動小数点数を使わないため、整数座標なら誤差なく比較できる。",
    ),
    "shortest_path/GridBFS.py": (
        "障害物付きgridで開始cellから全cellへの最短移動回数を求められる。",
        "2点間の最短移動回数だけを取得でき、到達不能は-1で判別できる。",
        "4近傍以外の移動規則や障害物の値も指定できる。",
    ),
    "combinatorics/GrayCode.py": (
        "整数とGray codeを相互変換できる。",
        "指定したstartからgoalまで全bitmaskを一度ずつ通るHamilton pathを生成できる。",
    ),
    "combinatorics/BinomialQueries.py": (
        "複数のsum(C(n,k), 0<=k<=m)をquery順に一括計算できる。",
        "BinomialPrefixで現在の(n,m)を前後へ動かし、隣接移動ごとにO(1)でprefix和を更新できる。",
        "素数法で巨大なnに対する第1種・第2種Stirling数をqueryできる。",
    ),
    "tree/ZeroOneTree.py": (
        "親を子より先に並べる制約の下で、0/1ラベル列の転倒数を最小化できる。",
        "各頂点が複数の0と1を持つblock版も同じAPIで処理できる。",
    ),
})


PURPOSE_BY_NAME = {
    "add_query": "半開区間の問い合わせを登録し、そのquery IDを返す。",
    "best": "現在の評価が最大の候補番号を返す。",
    "bfs_csr": "重みなしグラフでstartから各頂点までの最短辺数と直前頂点を求める。",
    "comb_small_k": "nが大きくkが小さいときに、階乗表を作らず乗法式で二項係数を求める。分母がmodで可逆な範囲で使う。",
    "comb_prefix_sums": "複数のsum(C(n,k), 0<=k<=m)をquery順に一括計算する。",
    "circuit": "要素を加えたときに生じるmatroidの基本回路を返す。",
    "component_size": "指定頂点が属する連結成分の頂点数を返す。",
    "connected_components_csr": "無向グラフを連結成分へ分け、各頂点の成分IDと頂点groupを返す。",
    "dijkstra_csr": "非負重みグラフでstartからの最短距離と経路復元用の直前頂点を求める。",
    "divisors": "正の約数を昇順で列挙する。",
    "euler_phi": "1以上number以下でnumberと互いに素な整数の個数を返す。",
    "factor_count_pairs": "素因数と指数の組を素因数順に返す。",
    "factorial": "n!を指定した法で計算する。",
    "from_adjacency": "隣接listを検証し、同じ辺をCSR形式へ変換する。",
    "get_edge": "edge_idに対応する辺情報を返す。",
    "lower_string": "英小文字からなる指定長のランダム文字列を生成する。",
    "mobius": "整数numberに対するMöbius関数の値を返す。",
    "merge_max_interval": "隣り合う2区間の集約値を結合し、結合後の区間和・最大部分配列和・最小部分配列和を返す。",
    "max_interval_segment_tree": "数列から、各区間の最大・最小部分配列和を取得できるSegmentTreeを構築する。",
    "normalize": "保持中の候補を評価順に整理し、上位だけを残す。",
    "pairs": "matchingに含まれる頂点pairを列挙する。",
    "play": "次に試す候補を選び、その番号を返す。",
    "pollard_rho": "合成数numberの非自明な因数を1つ探す。",
    "prime_factors": "素因数を重複込みで昇順に列挙する。",
    "reward": "直前に選んだ候補へ観測した報酬を反映する。",
    "scc_ids_csr": "強連結成分数と頂点ごとの成分IDをトポロジカル順で返す。",
    "scc": "有向グラフを強連結成分へ分け、各頂点の成分IDと頂点groupを返す。",
    "scc_csr": "CSR有向グラフを強連結成分へ分け、各頂点の成分IDと頂点groupを返す。",
    "top_k": "現在の範囲で値が大きい順にk件の集計結果を返す。",
    "topological_sort_csr": "有向非巡回グラフの頂点をトポロジカル順に並べる。閉路があればNoneを返す。",
    "transpose": "全ての辺の向きを反転したCSRグラフを返す。",
    "zero_one_bfs_csr": "重みが0または1のグラフでstartからの最短距離と直前頂点を求める。",
    "berlekamp_massey_poly": "最短線形漸化式の特性多項式 [1,-c1,...,-cD] を求める。",
    "ancestors": "指定頂点から重心分解木の祖先へ向かう経路情報を返す。",
    "binary_search_float": "判定条件が切り替わる実数境界を指定回数の二分探索で近似する。",
    "binary_search_int": "判定条件が切り替わる整数境界を二分探索する。",
    "bit_indices": "整数の2進表現で1になっているbit位置を昇順に列挙する。",
    "bucket_sort": "非負整数keyを使ってvaluesを安定sortした列を返す。",
    "bucket_sort_permutation": "非負整数keyを安定sortしたときの元の添字順を返す。",
    "coordinate_compress": "値の大小関係を保った0始まりの順位へ座標圧縮する。",
    "count_increasing_sequences": "lower[i]以上upper[i]未満を満たす広義単調増加列の個数を求める。",
    "count_spanning_trees": "無向グラフの全域木の個数をMatrix-Tree theoremで求める。",
    "minplus_conv_convex": "2つの凸列のmin-plus畳み込みを差分列のmergeで求める。",
    "concave_max_plus_convolution": "凹列と一般列のmax-plus畳み込みを求める。",
    "ensure_permutation": "列が0からn-1までを1回ずつ含む置換か判定する。",
    "fibonacci": "index番目のFibonacci数を高速doublingで求める。",
    "lis": "最長増加部分列の長さを求め、必要なら添字列と値列も復元する。",
    "lsb_index": "正整数の最下位1-bitの位置を0-indexedで返す。",
    "mcs_order": "最大重み探索（MCS）で頂点を選ぶ順序を返す。",
    "minplus_conv": "一般列と凸列のmin-plus畳み込みを高速に求める。",
    "msb_index": "正整数の最上位1-bitの位置を0-indexedで返す。",
    "multiplicative_convolution": "素数modの乗法に沿った畳み込みを計算する。",
    "replacement_paths": "各辺を1本ずつ除いた場合のsource-target最短距離をまとめて求める。",
    "split_mod_progression": "(multiplier*i+addend) mod modulusを等差な区間へ分割する。",
    "tree_distance_counts": "木の頂点pair数を距離ごとに数える。",
    "fps_shrink": "昇冪係数列を法で正規化し、末尾の0を除いた新しいlistを返す。",
    "fps_subtract": "第1の形式的冪級数から第2の級数を係数ごとに減算する。",
    "fps_negate": "形式的冪級数の全係数の符号を法の上で反転する。",
    "fps_multiply": "2つの昇冪係数列を畳み込み、積の係数列を返す。法998244353では専用NTT経路を使う。",
    "fps_derivative": "昇冪係数列で表した形式的冪級数を微分する。",
    "fps_evaluate": "昇冪係数列で表した多項式を指定した値へ代入する。",
    "fps_inverse": "形式的冪級数の乗法逆数を指定した係数数まで求める。",
    "fps_logarithm": "定数項が1の形式的冪級数の対数を指定した係数数まで求める。",
    "fps_exponential": "定数項が0の形式的冪級数の指数を指定した係数数まで求める。",
    "fps_power": "形式的冪級数の整数乗を指定した係数数まで求める。",
    "fps_square_root": "形式的冪級数の平方根を指定した係数数まで求め、存在しなければNoneを返す。",
    "fps_taylor_shift": "多項式f(x)からf(x+shift)の昇冪係数列を求める。",
    "integer_partitions": "整数totalの分割を辞書式順序で列挙する。",
    "integer_partitions_up_to": "指定上限までの各整数分割を列挙する。",
    "inversion_count": "列で i < j かつ values[i] > values[j] となる組数を求める。",
    "knapsack_01": "各品物を高々1回選ぶ0/1 knapsackの到達可能状態を計算する。",
    "knapsack_01_max": "各品物を高々1回選ぶ0/1 knapsackの最大価値を求める。",
    "kth_on_path": "2頂点間のpath上で始点からk個進んだ頂点を返す。",
    "merge_intervals": "重なる区間を併合し、互いに交わらない半開区間列を返す。",
    "num_vertices": "現在登録されている頂点数を返す。",
    "parent_edge_of": "指定頂点と親を結ぶ辺IDを返す。",
    "parent_of": "指定頂点の親頂点を返す。",
    "permute": "permutationに従ってvaluesを並べ替えた新しいlistを返す。",
    "permute_in_place": "permutationに従ってvalues自体を破壊的に並べ替える。",
    "radix_sort_nonnegative": "非負整数列をradix sortで昇順に並べる。",
    "submasks": "maskの部分maskを大きい順に列挙する。",
    "supermasks": "指定bit幅の範囲でmaskを含む上位maskを列挙する。",
    "choice": "空でない列から1要素を一様に選ぶ。",
    "next_u64": "内部状態を1回進め、符号なし64bit整数を返す。",
    "randrange": "半開区間から偏りのないランダム整数を1個返す。",
    "uniform": "両端を含む閉区間から偏りのないランダム整数を1個返す。",
    "uniform_bool": "FalseとTrueを同じ確率で返す。",
    "uniform01": "0以上1未満の実数を53bit精度で生成する。",
    "shuffle": "mutableな列をFisher–Yates法で破壊的に並べ替える。",
    "permutation": "連続する整数を一様ランダムに並べ替えた置換を返す。",
    "sample": "列から重複なしで指定個数を一様に選ぶ。",
    "sample_range": "閉区間内の整数から重複なしで指定個数を一様に選ぶ。",
    "string": "指定alphabetから独立に文字を選んだ文字列を生成する。",
    "edge_count": "保持している辺の本数を返す。",
    "add_directed_edge": "有向辺をedge-listへ追加し、その位置を返す。",
    "add_undirected_edge": "無向辺をedge-listへ追加し、その位置を返す。",
    "to_adjacency_list": "edge-listを頂点ごとの隣接辺listへ変換する。",
    "to_adjacency_matrix": "edge-listを辺重み入りの隣接行列へ変換する。",
    "format_edges": "辺を競プロ入力で使える改行区切り文字列へ整形する。",
    "set_seed": "乱数状態を指定seedから作り直し、generator自身を返す。",
    "single": "1要素だけを含む区間のMaxIntervalを作る。",
    "tree": "Prüfer codeからラベル付き木を一様ランダムに生成する。",
    "star": "中心頂点を一様に選んだstar graphを生成する。",
    "complete": "n頂点の完全単純graphを生成する。",
    "simple": "n頂点m辺の単純無向graphを一様に生成する。",
    "erdos_renyi": "各辺を独立に指定確率で含めたG(n,p)を生成する。",
    "unicyclic": "n頂点n辺でcycleをちょうど1個持つ連結graphを生成する。",
    "tree_center": "木の直径に対する中心頂点を1個または2個返す。",
    "tree_centroid": "取り除いた後の各成分が元の半分以下になる重心を返す。",
}


# These names are intentionally shared because their user-facing operation is
# identical across modules. Other repeated names belong in API_DETAILS_BY_SYMBOL.
SHARED_PURPOSE_NAMES = {
    "component_size",
    "get_edge",
    "kth_on_path",
    "pairs",
    "parent_of",
}


ARGUMENT_DETAILS = {
    "adjacency": "各頂点の隣接辺を並べた隣接list",
    "arm_count": "選択肢（arm）の個数",
    "block_size": "1ブロックに含める要素数",
    "build": "初期化時に前処理まで実行するか",
    "build_dag": "強連結成分を縮約したDAGも構築するか",
    "check_nonnegative": "負の辺重みがないことを検査するか",
    "check_weights": "全ての辺重みが0または1か検査するか",
    "combine": "2つの集約値をまとめる二項関数",
    "duration": "探索を続ける秒数",
    "end_temperature": "焼きなまし終了時の温度",
    "exact": "近似を使わず厳密な条件で処理するか",
    "fill_frequency": "初期値を何個あるものとして数えるか",
    "fill_value": "未設定位置に入れる初期値",
    "hash_function": "候補を同一判定するためのhash関数",
    "include_left": "左端を結果に含めるか",
    "include_right": "右端を結果に含めるか",
    "increasing_slopes": "直線の傾きを昇順で追加するか",
    "initialize": "初期状態を作って返す関数",
    "insert": "要素を現在の状態へ追加する関数",
    "k": "選ぶ個数または0-indexedの順位",
    "lazy_identity": "遅延作用を何もしない値",
    "lexicographical": "頂点番号が小さい順を優先するか",
    "lower_bound": "探索対象とする値の下限",
    "max_iterations": "反復回数の上限。Noneなら時間だけで終了判定する",
    "minimum": "値の下限。Noneなら入力から決める",
    "output": "各queryの現在の答えを返す関数",
    "p": "操作する位置（0始まり）または、このAPIで使う法",
    "propose": "現在状態から次の候補状態と評価差を作る関数",
    "python_int_sum": "区間和をPythonの任意精度整数で保持するか",
    "return_argmax": "最大値に加えて選んだ添字も返すか",
    "return_argmin": "最小値に加えて選んだ添字も返すか",
    "rollback": "snapshotで保存した状態まで巻き戻す関数",
    "snapshot": "現在状態を保存し、巻き戻し位置を返す関数",
    "start_temperature": "焼きなまし開始時の温度",
    "state_max": "同時に保持する候補状態数",
    "update": "候補状態を1回更新し、状態と評価を返す関数",
    "with_distance": "頂点番号だけでなく距離も返すか",
    "zero_indexed": "頂点番号を0始まりで出力するか",
    "target_depth": "祖先として取得したい根からの深さ",
    "alphabet": "生成文字の候補を並べた空でない文字列または列",
    "allow_empty": "長さ0の半開区間も許すか",
    "edge_count": "生成する辺の本数",
    "positive": "各要素を1以上に制限するか",
    "probability": "各候補を選ぶ確率（0.0以上1.0以下）",
    "sort_result": "選んだ整数を昇順へsortして返すか",
    "weight_min": "生成する辺重みの下限（含む）",
    "weight_max": "生成する辺重みの上限（含む）",
    "weighted": "辺重みを生成し、出力にも含めるか",
}


RETURN_DETAILS = {
    "bfs_csr": "tuple[list[int], list[int]] — 1つ目は各頂点までの辺数（未到達は-1）、2つ目は経路復元用の直前頂点（未設定は-1）",
    "bipartite_coloring_csr": "list[int] | None — 各頂点の色0/1。二部グラフでなければNone",
    "connected_components_csr": "tuple[list[int], list[list[int]]] — 1つ目は頂点ごとの成分ID、2つ目は各成分に属する頂点の列",
    "comb_small_k": (
        r"int — 二項係数 $\binom{n}{k}$ を $\mathrm{mod}$ で割った余り。"
        r"$0 \le k \le n$ でなければ0"
    ),
    "comb_prefix_sums": (
        r"list[int] — 各クエリ $(n,m)$ に対する "
        r"$\sum_{k=0}^{m}\binom{n}{k}$ を、入力と同じ順に並べた列"
    ),
    "concave_max_plus_convolution": (
        r"list[number]、return_argmax=Trueならtuple[list[number], list[int]] — "
        r"値の列 $c$ は $c_k=\max_{i+j=k}(\mathrm{concave}_i+\mathrm{arbitrary}_j)$。"
        r"長さは $\lvert\mathrm{concave}\rvert+\lvert\mathrm{arbitrary}\rvert-1$。"
        r"添字列の $k$ 番目は最大値を作った $i$"
    ),
    "count_increasing_sequences": "int — 条件を満たす列の個数をmodで割った0以上mod未満の値",
    "count_spanning_trees": "int — 無向全域木の重み付き個数をmodで割った値",
    "dijkstra_csr": "tuple[list[number], list[int]] — 1つ目は各頂点への最短距離（未到達はinf）、2つ目は経路復元用の直前頂点（未設定は-1）",
    "divisors": "list[int] — numberの正の約数を昇順に並べた列",
    "euler_phi": "int — 1以上number以下でnumberと互いに素な整数の個数",
    "factor_count_pairs": "list[tuple[int, int]] — (素因数, 指数)を素因数の昇順に並べた列",
    "mobius": "int — numberのMöbius関数値（-1、0、1のいずれか）",
    "mcs_order": "list[int] — MCSで選ばれた頂点番号を先頭から並べた長さnの列",
    "minplus_conv": (
        r"list[number] または tuple[list[number], list[int]] — "
        r"$c_k=\min_{i+j=k}(\mathrm{arbitrary}_i+\mathrm{convex}_j)$ と、"
        "return_argmin=Trueでは最小値を作る凸列側の添字"
    ),
    "minplus_conv_convex": (
        r"list[number] — $c_k=\min_{i+j=k}(\mathrm{first}_i+\mathrm{second}_j)$ "
        r"を格納した長さ $\lvert\mathrm{first}\rvert+\lvert\mathrm{second}\rvert-1$ の列"
    ),
    "multiplicative_convolution": (
        r"list[int] — $c_k=\sum_{ij\equiv k\pmod p} "
        r"\mathrm{first}_i\mathrm{second}_j$ を格納した長さ $p=\mathrm{prime}$ の列"
    ),
    "pollard_rho": "int — numberの非自明な因数。numberが素数ならnumber自身",
    "prime_factors": "list[int] — 素因数を重複込みで昇順に並べた列",
    "replacement_paths": "list[number] — index iはedges[i]を除いたsource-target最短距離。到達不能ならinf",
    "scc_ids_csr": "tuple[int, list[int]] — 強連結成分数と、頂点ごとの成分ID",
    "scc": "tuple[list[int], list[list[int]]] — 頂点ごとの成分IDと、各成分に属する頂点の列",
    "scc_csr": "tuple[list[int], list[list[int]]] — 頂点ごとの成分IDと、各成分に属する頂点の列",
    "split_mod_progression": "list[tuple[int, int, int, int, int]] — (開始index, 開始値, index差, 値の差, 長さ)の列",
    "topological_sort_csr": "list[int] | None — 頂点のトポロジカル順。閉路があればNone",
    "tree_distance_counts": (
        r"list[int] — $\mathrm{result}[d]$ は距離が $d$ の頂点のunordered pair数。"
        r"include_same=Trueなら $\mathrm{result}[0]$ は頂点数"
    ),
    "zero_one_bfs_csr": "tuple[list[int], list[int]] — 1つ目は各頂点への最短距離（未到達はinf）、2つ目は経路復元用の直前頂点（未設定は-1）",
    "permute": "list[object] — permutationの順にvaluesの要素を並べた新しいlist",
    "permute_in_place": "list[object] — permutationの順へ並べ替えた入力valuesと同じobject",
    "tree_center": "list[int] — 木の中心頂点番号を昇順に並べた長さ1または2のlist",
    "tree_centroid": "list[int] — 木の重心頂点番号を昇順に並べた長さ1または2のlist",
    "fps_shrink": "list[number] — 法で正規化し末尾の0を除いた昇冪係数列",
    "fps_subtract": "list[number] — 第1入力から第2入力を引いた昇冪係数列",
    "fps_negate": "list[number] — 各係数の符号を反転した昇冪係数列",
    "fps_multiply": (
        r"list[number] — 積 $f(x)g(x)$ を表す長さ "
        r"$\lvert f\rvert+\lvert g\rvert-1$ の昇冪係数列"
    ),
    "fps_derivative": (
        r"list[number] — 導関数 $f'(x)$ を表す長さ "
        r"$\max(0,\lvert f\rvert-1)$ の昇冪係数列"
    ),
    "fps_evaluate": (
        r"int — $f(\mathrm{value})\bmod\mathrm{mod}$。"
        r"$0 \le \mathrm{answer}<\mathrm{mod}$"
    ),
    "fps_inverse": (
        r"list[number] — $f(x)g(x)\equiv1\pmod{x^{\mathrm{degree}}}$ を満たす "
        r"$g(x)$ の、長さ $\mathrm{degree}$ の昇冪係数列"
    ),
    "fps_logarithm": (
        r"list[number] — $\log f(x)\bmod x^{\mathrm{degree}}$ の、"
        r"長さ $\mathrm{degree}$ の昇冪係数列"
    ),
    "fps_exponential": (
        r"list[number] — $\exp f(x)\bmod x^{\mathrm{degree}}$ の、"
        r"長さ $\mathrm{degree}$ の昇冪係数列"
    ),
    "fps_power": (
        r"list[number] — $f(x)^{\mathrm{exponent}}\bmod x^{\mathrm{degree}}$ の、"
        r"長さ $\mathrm{degree}$ の昇冪係数列"
    ),
    "fps_square_root": (
        r"list[number] | None — $g(x)^2\equiv f(x)\pmod{x^{\mathrm{degree}}}$ を満たす "
        r"$g(x)$ の係数列。存在しなければNone"
    ),
    "fps_taylor_shift": (
        r"list[number] — $f(x+\mathrm{shift})$ を表す入力と同じ長さの昇冪係数列"
    ),
    "choice": "object — 入力列から一様に選んだ1要素",
    "shuffle": "mutable sequence — 並べ替え後の入力と同じobject",
    "permutation": (
        r"list[int] — $\mathrm{start}$ から $\mathrm{start}+\mathrm{size}-1$ までを"
        r"1回ずつ含むランダムな列"
    ),
    "sample": "list[object] — 入力列から重複なしで選んだcount要素",
    "sample_range": "list[int] — 指定閉区間から重複なしで選んだcount個の整数",
    "string": "str — alphabetから生成したlength文字の文字列",
    "edge_count": "int — Graphが保持している辺の本数",
    "add_directed_edge": "int — 追加した辺のedge-list内の0-indexed位置",
    "add_undirected_edge": "int — 追加した辺のedge-list内の0-indexed位置",
    "to_adjacency_list": "list[list[Edge]] — 頂点ごとに外向きEdgeを並べた隣接list",
    "to_adjacency_matrix": (
        r"list[list[number]] — 行を始点、列を終点とする $n\times n$ の辺重み行列"
    ),
    "format_edges": "str — 1辺1行の改行区切り文字列（末尾改行なし）",
    "set_seed": "UndirectedGraphGenerator — 状態をresetしたgenerator自身",
    "tree": r"Graph — $n$ 頂点 $n-1$ 辺の連結な木",
    "star": r"Graph — $n$ 頂点 $\max(0,n-1)$ 辺のstar graph",
    "complete": r"Graph — $n$ 頂点 $n(n-1)/2$ 辺の完全graph",
    "simple": "Graph — n頂点edge_count辺で自己loop・多重辺のないgraph",
    "erdos_renyi": "Graph — 各候補辺を独立にprobabilityで含めた単純graph",
    "unicyclic": "Graph — n頂点n辺でcycleを1個だけ持つ連結単純graph",
}


# API names such as ``get`` and ``query`` are reused throughout the library.
# Details that cannot be inferred from the name or AST are therefore keyed by
# source module, owning class (None for a top-level function), and symbol name.
API_DETAILS_BY_SYMBOL = {
    ("fps998/MultipointEvaluation.py", None, "multipoint_evaluation"): {
        "description": "998244353 上の多項式を、すべての評価点で高速に一括評価する。",
        "argumentDescriptions": {
            "polynomial": "昇べき順の係数列。polynomial[i] は x^i の係数。",
            "points": "評価する点を並べた列。",
        },
        "returnFormat": "list[int]",
        "returnDescription": (
            "points と同じ長さの列 result。"
            "result[i] = polynomial(points[i]) mod 998244353。"
        ),
    },
    ("fps998/MultipointEvaluation.py", None, "polynomial_interpolation"): {
        "description": "998244353 上で、相異なる点と値から多項式を復元する。",
        "argumentDescriptions": {
            "points": "互いに異なる補間点を並べた列。",
            "values": "values[i] が points[i] における値となる列。",
        },
        "returnFormat": "list[int]",
        "returnDescription": (
            "長さ len(points) の昇べき順係数列 result。"
            "result(points[i]) = values[i] mod 998244353。"
        ),
    },
    ("fps/IncreasingSequences.py", None, "count_increasing_sequences"): {
        "description": (
            r"各位置で $\mathrm{lower}_i \le x_i < \mathrm{upper}_i$ を満たす"
            r"広義単調増加列 $x_0 \le \cdots \le x_{N-1}$ の個数を求める。"
        ),
        "argumentDescriptions": {
            "lower": (
                r"各位置の下限を並べた列 $\mathrm{lower}$。位置 $i$ では "
                r"$\mathrm{lower}_i$ を含む。"
            ),
            "upper": (
                r"各位置の上限を並べた列 $\mathrm{upper}$。位置 $i$ では "
                r"$\mathrm{upper}_i$ を含まない。"
            ),
        },
        "returnFormat": "int",
        "returnDescription": (
            r"条件を満たす列の個数を $\mathrm{mod}$ で割った余り。"
            r"$0 \le \mathrm{answer} < \mathrm{mod}$。"
        ),
    },
    ("combinatorial_series/StirlingNumbers.py", None, "stirling_first_row"): {
        "description": (
            r"固定した $n=\mathrm{order}$ について、第一種 Stirling 数を "
            r"$0 \le k \le n$ の順に求める。"
        ),
        "argumentDescriptions": {
            "order": r"固定する第1引数 $n$。",
            "signed": (
                r"Falseなら符号なし $c(n,k)$、Trueなら符号付き $s(n,k)$ を返す。"
            ),
        },
        "returnFormat": "list[int]",
        "returnDescription": (
            r"長さ $\mathrm{order}+1$ の列 $\mathrm{result}$。"
            r"$\mathrm{result}[k]$ は指定した符号規約の第一種 Stirling 数。"
        ),
    },
    ("combinatorial_series/StirlingNumbers.py", None, "stirling_second_row"): {
        "description": (
            r"固定した $n=\mathrm{order}$ について、第二種 Stirling 数 "
            r"$S(n,k)$ を $0 \le k \le n$ の順に求める。"
        ),
        "argumentDescriptions": {
            "order": r"固定する第1引数 $n$。",
        },
        "returnFormat": "list[int]",
        "returnDescription": (
            r"長さ $\mathrm{order}+1$ の列 $\mathrm{result}$。"
            r"$\mathrm{result}[k]=S(\mathrm{order},k)$。"
        ),
    },
    ("combinatorial_series/StirlingNumbers.py", None, "stirling_first_column"): {
        "description": (
            r"固定した $k=\mathrm{column}$ について、符号なし第一種 Stirling 数 "
            r"$c(n,k)$ を $0 \le n \le \mathrm{upper}$ の範囲で求める。"
        ),
        "argumentDescriptions": {
            "column": r"固定する第2引数 $k$。",
            "upper": r"求める最大の第1引数 $n$。この値を含む。",
        },
        "returnFormat": "list[int]",
        "returnDescription": (
            r"長さ $\mathrm{upper}+1$ の列 $\mathrm{result}$。"
            r"$\mathrm{result}[n]=c(n,\mathrm{column})$ で、"
            r"$n<\mathrm{column}$ の要素は0。"
        ),
    },
    ("combinatorial_series/StirlingNumbers.py", None, "stirling_second_column"): {
        "description": (
            r"固定した $k=\mathrm{column}$ について、第二種 Stirling 数 "
            r"$S(n,k)$ を $0 \le n \le \mathrm{upper}$ の範囲で求める。"
        ),
        "argumentDescriptions": {
            "column": r"固定する第2引数 $k$。",
            "upper": r"求める最大の第1引数 $n$。この値を含む。",
        },
        "returnFormat": "list[int]",
        "returnDescription": (
            r"長さ $\mathrm{upper}+1$ の列 $\mathrm{result}$。"
            r"$\mathrm{result}[n]=S(n,\mathrm{column})$ で、"
            r"$n<\mathrm{column}$ の要素は0。"
        ),
    },
    ("tree/AuxiliaryTree.py", "AuxiliaryTree", "get"): {
        "description": (
            "verticesと、それらを結ぶために必要なLCAだけを含む圧縮木を構築する。"
            "圧縮木の頂点は0から振り直される。"
        ),
        "returnFormat": "(auxiliary, original_vertices)",
        "returnDescription": (
            "親から子へ向かう圧縮木の隣接リストと、圧縮後の各頂点を"
            "元の木の頂点番号へ戻す対応表。入力が空なら両方とも空のlist。"
        ),
        "returnParts": (
            {
                "name": "auxiliary",
                "format": "list[list[int]] | list[list[tuple[int, int]]]",
                "description": (
                    "auxiliary[i]は圧縮木の頂点iの子indexを並べたlist。"
                    "空でなければ根はindex 0。with_distance=Trueでは各要素が"
                    "(child_index, distance)になり、distanceは元の木で親子間に"
                    "ある辺の本数。"
                ),
            },
            {
                "name": "original_vertices",
                "format": "list[int]",
                "description": (
                    "original_vertices[i]は、圧縮木の頂点iに対応する元の木の"
                    "頂点番号。指定した頂点に加えて、構築に必要なLCAも含む。"
                ),
            },
        ),
    },
    ("tree/CentroidDecomposition.py", "CentroidDistanceFenwick", "add"): {
        "description": "頂点vertexに保存されている値へdeltaを加える。",
        "returnDescription": "値は返さない。以後のqueryへ加算後の値を反映する。",
    },
    ("tree/CentroidDecomposition.py", "CentroidDistanceFenwick", "set"): {
        "description": "頂点vertexに保存されている値をvalueへ置き換える。",
        "returnDescription": "値は返さない。以後のqueryへ新しい値を反映する。",
    },
    ("tree/CentroidDecomposition.py", "CentroidDistanceFenwick", "query"): {
        "description": (
            r"vertexからの距離が半開区間 $[\mathrm{lower},\mathrm{upper})$ に入る"
            "頂点の値を合計する。"
            "upper=Noneなら距離の上限を設けない。"
        ),
        "returnFormat": "number",
        "returnDescription": (
            r"$\mathrm{lower}\le\operatorname{dist}(\mathrm{vertex},u)<\mathrm{upper}$ を"
            r"満たすすべての頂点 $u$ に対する $\sum_u\mathrm{values}[u]$。"
            "query(vertex)は木全体の値の合計を返す。"
        ),
    },
    ("algorithm/IntegerUtilities.py", None, "integer_nth_root"): {
        "description": (
            r"$r^{\mathrm{degree}}\le\mathrm{number}$ を満たす最大の非負整数 $r$ を求める。"
        ),
        "returnFormat": "int",
        "returnDescription": (
            r"$r^{\mathrm{degree}}\le\mathrm{number}<(r+1)^{\mathrm{degree}}$ を満たす $r$。"
        ),
    },
    ("convolution/MinPlusConvolution.py", None, "minplus_conv"): {
        "description": (
            r"一般列 $a=\mathrm{arbitrary}$ と凸列 $b=\mathrm{convex}$ のmin-plus畳み込み "
            r"$c_k=\min_{i+j=k}(a_i+b_j)$ をmonotone minimaで高速に求める。"
        ),
        "argumentDescriptions": {
            "arbitrary": "任意の数列a。凸性は不要。",
            "convex": (
                r"離散凸な数列b。差分 $b_{i+1}-b_i$ が広義単調増加であること。"
            ),
            "return_argmin": "最小値に加えて、選ばれた凸列側の添字jも返すか",
        },
        "returnFormat": "list[number] | tuple[list[number], list[int]]",
        "returnDescription": (
            r"values[k]は $\min_{i+j=k}(a_i+b_j)$。return_argmin=Trueでは "
            r"$(\mathrm{values},\mathrm{indices})$ を返し、"
            r"$\mathrm{indices}[k]=j$ は最小値を作った凸列側の添字。"
        ),
        "returnParts": (
            {
                "name": "values",
                "format": "list[number]",
                "description": r"$\mathrm{values}[k]=\min_{i+j=k}(a_i+b_j)$。",
            },
            {
                "name": "indices",
                "format": "list[int]",
                "description": "return_argmin=Trueのときだけ返す、最小値を作った凸列側の添字j。",
            },
        ),
    },
    ("convolution/MinPlusConvolution.py", None, "minplus_conv_convex"): {
        "description": (
            r"2つの凸列 $a=\mathrm{first}$、$b=\mathrm{second}$ のmin-plus畳み込み "
            r"$c_k=\min_{i+j=k}(a_i+b_j)$ を差分列のmergeで求める。"
        ),
        "argumentDescriptions": {
            "first": r"離散凸な数列a。差分 $a_{i+1}-a_i$ が広義単調増加であること。",
            "second": r"離散凸な数列b。差分 $b_{i+1}-b_i$ が広義単調増加であること。",
        },
        "returnFormat": "list[number]",
        "returnDescription": (
            r"長さ $\lvert a\rvert+\lvert b\rvert-1$ の列c。"
            r"$c_k=\min_{i+j=k}(a_i+b_j)$。"
        ),
    },
    (
        "arithmetic_convolution/MultiplicativeConvolutionModPrime.py",
        None,
        "multiplicative_convolution",
    ): {
        "description": (
            r"素数 $p=\mathrm{prime}$ の剰余類の乗法に沿った畳み込み "
            r"$c_k=\sum_{ij\equiv k\pmod p}\mathrm{first}_i\mathrm{second}_j$ を求める。"
        ),
    },
    ("combinatorics/Combination.py", None, "comb_small_k"): {
        "description": (
            r"$n$ が大きく $k$ が小さいとき、二項係数 $\binom{n}{k}$ を乗法式で求める。"
        ),
    },
    ("combinatorics/Combination.py", "Comb", "F"): {
        "description": r"階乗 $n!\bmod\mathrm{mod}$ を返す。",
        "returnFormat": "int",
        "returnDescription": r"$n!\bmod\mathrm{mod}$。",
    },
    ("combinatorics/Combination.py", "Comb", "Fi"): {
        "description": r"逆階乗 $(n!)^{-1}\bmod\mathrm{mod}$ を返す。",
        "returnFormat": "int",
        "returnDescription": r"$n!\,x\equiv1\pmod{\mathrm{mod}}$ を満たす $x$。",
    },
    ("combinatorics/Combination.py", "Comb", "inv"): {
        "description": r"正の整数 $n$ の乗法逆元 $n^{-1}\bmod\mathrm{mod}$ を返す。",
        "argumentDescriptions": {
            "n": r"逆元を求める整数。$1\le n<\mathrm{mod}$。",
        },
        "returnFormat": "int",
        "returnDescription": r"$n\,x\equiv1\pmod{\mathrm{mod}}$ を満たす $x$。",
    },
    ("combinatorics/Combination.py", "Comb", "P"): {
        "description": r"順列数 $P(n,k)=n!/(n-k)!$ を $\mathrm{mod}$ で割った余りを返す。",
        "returnFormat": "int",
        "returnDescription": (
            r"$P(n,k)\bmod\mathrm{mod}$。$0\le k\le n$ でなければ0。"
        ),
    },
    ("combinatorics/Combination.py", "Comb", "H"): {
        "description": (
            r"$n$ 種類から重複を許して $k$ 個選ぶ重複組合せ "
            r"$H(n,k)=\binom{n+k-1}{k}$ を返す。"
        ),
        "returnFormat": "int",
        "returnDescription": r"$H(n,k)\bmod\mathrm{mod}$。",
    },
    ("combinatorics/Combination.py", "Comb", "catalan"): {
        "description": (
            r"$(0,0)$ から右へ $n$ 回、上へ $m$ 回進み、途中の全ての点で "
            r"$y\le x+k$ を保つ格子路の本数を求める。境界 $y=x+k$ 上は通れる。"
        ),
        "argumentDescriptions": {
            "n": "右へ進む回数。0以上。",
            "m": "上へ進む回数。0以上。",
            "k": r"許す高さの差。経路は $y\le x+k$ を満たす。",
        },
        "returnFormat": "int",
        "returnDescription": (
            r"条件を満たす格子路数をmodで割った余り。終点が境界より上なら0。"
        ),
    },
    ("combinatorics/BinomialQueries.py", None, "comb_prefix_sums"): {
        "description": (
            r"複数の $\sum_{k=0}^{m}\binom{n}{k}$ をクエリ順に一括計算する。"
        ),
    },
    ("combinatorics/BinomialQueries.py", "BinomialPrefix", "move"): {
        "description": (
            r"現在位置から $(n,m)$ へ移動し、$\sum_{k=0}^{m}\binom{n}{k}$ を返す。"
        ),
        "returnFormat": "int",
        "returnDescription": r"移動後の $\sum_{k=0}^{m}\binom{n}{k}\bmod\mathrm{mod}$。",
    },
    ("combinatorics/BinomialQueries.py", "BinomialPrefix", "get"): {
        "description": r"現在位置 $(n,m)$ の $\sum_{k=0}^{m}\binom{n}{k}$ を返す。",
        "returnFormat": "int",
        "returnDescription": r"現在位置の $\sum_{k=0}^{m}\binom{n}{k}\bmod\mathrm{mod}$。",
    },
    ("combinatorics/BinomialQueries.py", "StirlingNumberQuery", "first_kind"): {
        "description": r"符号なし第一種 Stirling 数 $c(n,k)$ を求める。",
        "returnFormat": "int",
        "returnDescription": r"$c(n,k)\bmod\mathrm{mod}$。",
    },
    ("combinatorics/BinomialQueries.py", "StirlingNumberQuery", "second_kind"): {
        "description": r"第二種 Stirling 数 $S(n,k)$ を求める。",
        "returnFormat": "int",
        "returnDescription": r"$S(n,k)\bmod\mathrm{mod}$。",
    },
    ("fenwick_tree/BIT.py", "BIT", "prefix_sum"): {
        "description": r"先頭からright未満までの和 $\sum_{i=0}^{\mathrm{right}-1}a_i$ を返す。",
        "returnDescription": r"$\sum_{i=0}^{\mathrm{right}-1}a_i$。",
    },
    ("fenwick_tree/BIT.py", "BIT", "sum"): {
        "description": (
            r"rightを指定したときは半開区間 $[\mathrm{left},\mathrm{right})$ の和を返す。"
            r"right=Noneなら $[0,\mathrm{left})$ の和を返す。"
        ),
        "returnDescription": (
            r"rightを指定したときは $\sum_{i=\mathrm{left}}^{\mathrm{right}-1}a_i$。"
            r"right=Noneなら $\sum_{i=0}^{\mathrm{left}-1}a_i$。"
        ),
    },
    ("fenwick_tree/BIT.py", "BIT", "get"): {
        "description": r"位置indexの値 $a_{\mathrm{index}}$ を返す。",
        "returnDescription": r"$a_{\mathrm{index}}$。",
    },
    ("fenwick_tree/BIT.py", "BIT", "lower_bound"): {
        "description": (
            r"接頭和 $\sum_{i=0}^{r-1}a_i$ がtarget以上になる最小の $r$ を返す。"
        ),
        "returnFormat": "int",
        "returnDescription": (
            r"$\sum_{i=0}^{r-1}a_i\ge\mathrm{target}$ を満たす最小の $r$。"
            "存在しなければ要素数。"
        ),
    },
    ("fenwick_tree/DynamicFenwickTree.py", "DynamicFenwickTree", "prefix_sum"): {
        "description": r"先頭からright未満までの和 $\sum_{i=0}^{\mathrm{right}-1}a_i$ を返す。",
        "returnDescription": r"$\sum_{i=0}^{\mathrm{right}-1}a_i$。",
    },
    ("fenwick_tree/DynamicFenwickTree.py", "DynamicFenwickTree", "sum"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ の和を返す。",
        "returnDescription": r"$\sum_{i=\mathrm{left}}^{\mathrm{right}-1}a_i$。",
    },
    ("segment_tree/SegTree.py", "SegTree", "prod"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ をopで左から畳み込む。",
        "returnDescription": (
            r"$\operatorname{op}(a_{\mathrm{left}},\ldots,a_{\mathrm{right}-1})$。"
            "空区間なら単位元e。"
        ),
    },
    ("segment_tree/SegTree.py", "SegTree", "all_prod"): {
        "description": r"全区間 $[0,n)$ をopで左から畳み込む。",
        "returnDescription": r"全要素のopによる畳み込み。空なら単位元e。",
    },
    ("segment_tree/LazySegTree.py", "LazySegTree", "prod"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ をopで左から畳み込む。",
        "returnDescription": (
            r"$\operatorname{op}(a_{\mathrm{left}},\ldots,a_{\mathrm{right}-1})$。"
            "空区間なら単位元e。"
        ),
    },
    ("segment_tree/LazySegTree.py", "LazySegTree", "all_prod"): {
        "description": r"全区間 $[0,n)$ をopで左から畳み込む。",
        "returnDescription": r"全要素のopによる畳み込み。空なら単位元e。",
    },
    ("combinatorics/Combination.py", "Comb", "C"): {
        "description": r"二項係数 $\binom{n}{k}\bmod\mathrm{mod}$ を返す。",
        "returnFormat": "int",
        "returnDescription": (
            r"$\binom{n}{k}\bmod\mathrm{mod}$。$0\le k\le n$ でなければ0。"
        ),
    },
    ("combinatorics/Combination.py", "Comb", "__call__"): {
        "description": r"`C(n, k)` と同じく $\binom{n}{k}\bmod\mathrm{mod}$ を返す。",
        "returnFormat": "int",
        "returnDescription": (
            r"$\binom{n}{k}\bmod\mathrm{mod}$。$0\le k\le n$ でなければ0。"
        ),
    },
    ("combinatorics/ArbitraryBinomial.py", "LargePrimeFactorial", "C"): {
        "description": r"Lucasの定理で二項係数 $\binom{n}{k}$ を素数modで求める。",
        "returnFormat": "int",
        "returnDescription": r"$\binom{n}{k}\bmod\mathrm{mod}$。範囲外なら0。",
    },
    ("combinatorics/ArbitraryBinomial.py", "PrimePowerBinomial", "C"): {
        "description": (
            r"二項係数 $\binom{n}{k}$ を素数冪 $\mathrm{prime}^{\mathrm{exponent}}$ で求める。"
        ),
        "returnFormat": "int",
        "returnDescription": r"$\binom{n}{k}\bmod\mathrm{mod}$。範囲外なら0。",
    },
    ("combinatorics/ArbitraryBinomial.py", "ArbitraryModBinomial", "C"): {
        "description": r"二項係数 $\binom{n}{k}$ を任意の正のmodで求める。",
        "returnFormat": "int",
        "returnDescription": r"$\binom{n}{k}\bmod\mathrm{mod}$。範囲外なら0。",
    },
    ("combinatorics/QBinomial.py", "QBinomial", "C"): {
        "description": r"q二項係数 $C_q(\mathrm{number},\mathrm{chosen})$ を求める。",
        "returnFormat": "int",
        "returnDescription": (
            r"$C_q(\mathrm{number},\mathrm{chosen})\bmod\mathrm{mod}$。"
            r"$0\le\mathrm{chosen}\le\mathrm{number}$ でなければ0。"
        ),
    },
    ("combinatorics/RationalBinomial.py", "RationalBinomial", "C"): {
        "description": r"二項係数 $\binom{\mathrm{number}}{\mathrm{chosen}}$ を正確に求める。",
        "returnFormat": "Fraction",
        "returnDescription": (
            r"$\binom{\mathrm{number}}{\mathrm{chosen}}$ を表すFraction。"
            r"$0\le\mathrm{chosen}\le\mathrm{number}$ でなければ0。"
        ),
    },
    ("fps/PolynomialComposition.py", None, "composition"): {
        "description": (
            r"外側の形式的冪級数 $f=\mathrm{outer}$ へ内側の "
            r"$g=\mathrm{inner}$ を代入し、$f(g(x))$ を求める。"
        ),
        "returnFormat": "list[int]",
        "returnDescription": (
            r"$f(g(x))\bmod x^{\mathrm{degree}}$ の係数を定数項から並べた列。"
        ),
    },
    ("random/Random.py", "Random", "composition"): {
        "description": "合計を固定した非負または正の整数列を一様に生成する。",
        "returnFormat": "list[int]",
        "returnDescription": (
            r"$\sum_i \mathrm{result}_i=\mathrm{total}$ を満たす、"
            r"長さ $\mathrm{parts}$ の非負または正の整数列。"
        ),
    },
    ("prime/Factorization.py", None, "factor_count"): {
        "description": "整数を素因数分解し、各素因数の指数を数える。",
        "returnFormat": "dict[int, int]",
        "returnDescription": "keyが素因数、valueがその指数の辞書。",
    },
    ("prime/Sieve.py", "LinearSieve", "factor_count"): {
        "description": "篩の表を使ってvalueを素因数分解する。",
        "returnFormat": "list[tuple[int, int]]",
        "returnDescription": "(素因数, 指数)を素因数の昇順に並べた列。",
    },
    ("graph/CSRGraph.py", "CSRGraph", "neighbors"): {
        "description": "vertexから出る辺をCSR内の順に列挙する。",
        "returnFormat": "iterator[tuple[int, number, int]]",
        "returnDescription": "(行き先頂点, 辺重み, 元の辺ID)を辺ごとにyieldする。",
    },
    ("graph/DimensionExpandedGraph.py", "DimensionExpandedGraph", "neighbors"): {
        "description": "座標coordinateと1軸だけが1異なる、grid内の直交近傍を列挙する。",
        "returnFormat": "list[tuple[int, ...]]",
        "returnDescription": "各軸の前後に隣接する、有効な座標tupleの列。",
    },
    ("ordered_set/RangeSet.py", "RangeSet", "intervals"): {
        "description": "現在保持している互いに素な半開区間を始点順に列挙する。",
        "returnFormat": "list[tuple[int, int]]",
        "returnDescription": r"保持中の半開区間 $[\mathrm{left},\mathrm{right})$ を始点順に並べた列。",
    },
    ("random/Random.py", "Random", "intervals"): {
        "description": "指定範囲に収まるランダムな半開区間を生成する。",
        "returnFormat": "list[tuple[int, int]]",
        "returnDescription": (
            r"$[\mathrm{lower},\mathrm{upper})$ 内に収まる半開区間 "
            r"$[\mathrm{left},\mathrm{right})$ の列。"
        ),
    },
    ("tree/HeavyLightDecomposition.py", "HeavyLightDecomposition", "path"): {
        "description": "uからvへの木のpathを、頂点列上の少数の半開区間へ分解する。",
        "returnFormat": "list[tuple[int, int]]",
        "returnDescription": (
            r"HLD順の半開区間 $[\mathrm{left},\mathrm{right})$ の列。edge=Falseなら頂点path、"
            "edge=TrueならLCAを除いた辺pathを覆う。区間の列自体はpath順とは限らない。"
        ),
    },
    ("graph_connectivity/NamoriDecomposition.py", "NamoriDecomposition", "path"): {
        "description": "同じ付随木にあるuとvのtree pathを、HLD順の半開区間へ分解する。",
        "returnFormat": "list[tuple[int, int]] | None",
        "returnDescription": (
            r"HLD順の半開区間 $[\mathrm{left},\mathrm{right})$ の列。"
            "2頂点が同じ付随木に属さなければNone。"
            "edge=TrueならLCAに対応する頂点を除く。"
        ),
    },
    ("random/RandomGraph.py", "UndirectedGraphGenerator", "path"): {
        "description": "頂点labelをランダムに並べたpath graphを生成する。",
        "returnFormat": "Graph",
        "returnDescription": r"$n$ 頂点 $\max(0,n-1)$ 辺のpath graph。",
    },
    ("random/RandomGraph.py", "UndirectedGraphGenerator", "connected"): {
        "description": "n頂点edge_count辺の連結単純無向graphを生成する。",
        "returnFormat": "Graph",
        "returnDescription": "n頂点edge_count辺の連結単純graph。",
    },
    ("graph_connectivity/OnlineDynamicConnectivity.py", "OnlineDynamicConnectivity", "connected"): {
        "description": "firstとsecondが現在同じ連結成分に属するか判定する。",
        "returnFormat": "bool",
        "returnDescription": "2頂点が同じ連結成分ならTrue、異なればFalse。",
    },
    ("tree/IncrementalForest.py", "IncrementalForest", "connected"): {
        "description": "firstとsecondが現在同じ木に属するか判定する。",
        "returnFormat": "bool",
        "returnDescription": "2頂点が同じ木に属すればTrue、異なればFalse。",
    },
    ("tree/LinkCutTree.py", "LinkCutTree", "connected"): {
        "description": "firstとsecondが現在同じ木に属するか判定する。",
        "returnFormat": "bool",
        "returnDescription": "2頂点が同じ木に属すればTrue、異なればFalse。",
    },
    ("tree/LinkCutTree.py", "SubtreeLinkCutTree", "connected"): {
        "description": "firstとsecondが現在同じ木に属するか判定する。",
        "returnFormat": "bool",
        "returnDescription": "2頂点が同じ木に属すればTrue、異なればFalse。",
    },
    ("tree/LinkCutTree.py", "SubtreeAddLinkCutTree", "connected"): {
        "description": "firstとsecondが現在同じ木に属するか判定する。",
        "returnFormat": "bool",
        "returnDescription": "2頂点が同じ木に属すればTrue、異なればFalse。",
    },
}


API_DETAILS_BY_SYMBOL.update({
    ("fps/FormalPowerSeries.py", None, "fps_add"): {
        "description": "2つの形式的冪級数を係数ごとに加算する。",
        "returnFormat": "list[number]",
        "returnDescription": "2つの入力と同じ法上の和を表す昇べき順係数列。",
    },
    ("fps/FormalPowerSeries.py", None, "fps_integral"): {
        "description": "定数項を0として形式的冪級数を積分する。",
        "returnFormat": "list[number]",
        "returnDescription": r"定数項を0とした不定積分 $\int f(x)\,dx$ を表す、長さ $\lvert f\rvert+1$ の昇べき順係数列。",
    },
    ("fps/FormalPowerSeries.py", None, "fps_div"): {
        "description": r"形式的冪級数の商 $numerator(x)/denominator(x)$ を $x^{degree}$ で打ち切って返す。",
        "argumentDescriptions": {
            "numerator": "分子の昇べき順係数列。",
            "denominator": "定数項が逆元を持つ分母の昇べき順係数列。",
            "degree": "返す係数数。省略時はnumeratorの長さ。",
            "mod": "係数の法。省略時は998244353。",
        },
        "returnFormat": "list[number]",
        "returnDescription": r"長さdegreeの $numerator(x)/denominator(x)\bmod x^{degree}$ の昇べき順係数列。",
    },
    ("fps/FormalPowerSeries.py", None, "fps_product"): {
        "description": "複数の多項式を短いものから畳み込み、全体の積を返す。",
        "returnFormat": "list[number]",
        "returnDescription": "全入力多項式の積を表す昇べき順係数列。",
    },
    ("graph_connectivity/BiconnectedComponents.py", "BiconnectedComponents", "components"): {
        "description": "頂点ごとに、その頂点を含む二頂点連結成分IDを列挙する。",
    },
    ("union_find/PersistentUnionFind.py", "PersistentUnionFind", "components"): {
        "description": "指定versionにある連結成分の個数を返す。",
    },
    ("rational/SternBrocotNode.py", "SternBrocotNode", "depth"): {
        "description": "Stern–Brocot木の根1/1から現在の有理数までの辺数を返す。",
    },
    ("string/PersistentString.py", "PersistentString", "depth"): {
        "description": "内部の永続平衡木の高さを返す。文字列長ではない。",
    },
    ("tree/IncrementalForest.py", "IncrementalForest", "depth"): {
        "description": "vertexが属する木の根からvertexまでの辺数を返す。",
    },
    ("fps/MultivariateFPS.py", "MultivariateFormalPowerSeries", "index"): {
        "description": "多変数の指数tupleを、係数配列の1次元indexへ変換する。",
    },
    ("graph_connectivity/NamoriDecomposition.py", "NamoriDecomposition", "index"): {
        "description": "vertexに対応するHLD順のindexを返す。",
    },
    ("graph_spanning/MergeTree.py", "MergeTree", "index"): {
        "description": "vertexに対応するmerge tree内部のindexを返す。",
    },
    ("number_theory/MultiplicativeFunctions.py", "DirichletQuotientSeries", "index"): {
        "description": "valueに対応する商列tableのindexを返す。",
    },
    ("number_theory/MultiplicativeFunctions.py", "MultiplicativePrefixSum", "index"): {
        "description": "valueに対応するprefix tableのindexを返す。",
    },
    ("tree/DSUOnTree.py", "DSUOnTree", "index"): {
        "description": "vertexに対応するEuler tour順のindexを返す。",
    },
    ("tree/HeavyLightDecomposition.py", "HeavyLightDecomposition", "index"): {
        "description": "頂点vに対応するHLD順のindexを返す。",
    },
    ("algorithm/Search.py", None, "kth_element"): {
        "description": "valuesを部分的に並べ替え、index番目に小さい値を返す。",
    },
    ("ordered_set/OrderedMap.py", "OrderedMap", "kth_element"): {
        "description": "keyの昇順でindex番目にある(key, value)を返す。",
    },
    ("algorithm/RangeQueries.py", "Mo", "run"): {
        "description": "登録した区間queryをMo順に処理し、get()の結果をquery ID順に返す。",
    },
    ("graph_connectivity/OfflineDynamicConnectivity.py", "OfflineDynamicConnectivity", "run"): {
        "description": "辺の追加・削除とqueryを時系列順にoffline処理する。",
    },
    ("graph_flow/MinCostBFlow.py", "MinCostBFlow", "run"): {
        "description": "登録した供給・需要と容量を満たす最小費用b-flowを求める。",
    },
    ("graph_matching/GeneralWeightedMatching.py", "GeneralWeightedMatching", "run"): {
        "description": "一般グラフの最大重みmatchingを求める。",
    },
    ("heuristic/SimulatedAnnealing.py", "SimulatedAnnealing", "run"): {
        "description": "proposeで候補を作り、温度に従って受理しながらstateを更新する。",
    },
    ("heuristic/SimulatedAnnealing.py", "SAManager", "run"): {
        "description": "initializeとupdateを使って焼きなましを進め、最良の状態と評価を返す。",
    },
    ("number_theory/MultiplicativeFunctions.py", "MultiplicativePrefixSum", "run"): {
        "description": "素数上のprefix値と素数冪の値から、乗法的関数のprefix和を求める。",
    },
    ("optimization/RollbackMo.py", "RollbackMo", "run"): {
        "description": "登録した区間queryをrollback Moで処理し、query ID順に結果を返す。",
    },
    ("spatial_structure/UnionRectangle.py", "UnionRectangle", "run"): {
        "description": "登録した軸平行長方形のunion面積を求める。",
    },
    ("string/PrefixSubstringLCS.py", "PrefixSubstringLCS", "run"): {
        "description": "登録した各substringとprefixのLCS長をquery ID順にまとめて求める。",
    },
    ("tree/DSUOnTree.py", "DSUOnTree", "run"): {
        "description": "各頂点を根とする部分木queryをDSU on treeでまとめて処理する。",
    },
})

API_DETAILS_BY_SYMBOL.update({
    ("sequence_structure/SWAGDeque.py", "SWAGDeque", "pop"): {
        "returnFormat": "object", "returnDescription": "deque右端から削除した要素。",
    },
    ("string/CompressedTrie.py", "CompressedTrie", "prefix_count"): {
        "returnFormat": "int", "returnDescription": "prefixを接頭辞に持つ登録済み文字列の個数。",
    },
    ("string/Trie.py", "Trie", "prefix_count"): {
        "returnFormat": "int", "returnDescription": "prefixを接頭辞に持つ登録済み文字列の個数。",
    },
})

API_DETAILS_BY_SYMBOL.update({
    ("fps/CompositeExponential.py", None, "inverse_composite_exponential"): {
        "returnFormat": "list[int]", "returnDescription": "入力seriesを逆変換した、入力と同じ長さの係数列。",
    },
    ("fps/PolynomialComposition.py", None, "fps_compose"): {
        "returnFormat": "list[int]", "returnDescription": "outer(inner(x)) mod x^degreeの昇冪係数をdegree個並べたlist。",
    },
    ("fps/PolynomialComposition.py", None, "fps_compositional_inverse"): {
        "returnFormat": "list[int]", "returnDescription": "series(g(x))=x mod x^degreeを満たすgの昇冪係数列。",
    },
    ("fps/SparseFormalPowerSeries.py", None, "sparse_inverse"): {
        "returnFormat": "list[int]", "returnDescription": "1/series mod x^degreeの昇冪係数をdegree個並べたlist。",
    },
    ("fps/SparseFormalPowerSeries.py", None, "sparse_exponential"): {
        "returnFormat": "list[int]", "returnDescription": "exp(series) mod x^degreeの昇冪係数をdegree個並べたlist。",
    },
    ("fps/SparseFormalPowerSeries.py", None, "sparse_logarithm"): {
        "returnFormat": "list[int]", "returnDescription": "log(series) mod x^degreeの昇冪係数をdegree個並べたlist。",
    },
    ("polynomial/GeometricMultipointEvaluation.py", None, "multipoint_evaluation_geometric"): {
        "returnFormat": "list[int]", "returnDescription": "polynomial(initial*ratio^i)をi=0..count-1の順に並べたlist。",
    },
    ("combinatorial_series/DerangementNumbers.py", None, "derangement_numbers"): {
        "returnFormat": "list[int]", "returnDescription": "0からmax_indexまでの完全順列数を添字順に並べたlist。",
    },
    ("combinatorial_series/PowerSums.py", None, "power_sums"): {
        "returnFormat": "list[int]", "returnDescription": "result[k]=sum(value^k for value in values) mod modとなるlist。",
    },
    ("tree/PruferCode.py", None, "prufer_encode_extended"): {
        "returnFormat": "list[int]", "returnDescription": "通常のPruefer列の末尾へroot n-1を加えた長さn-1の列。",
    },
    ("string/Manacher.py", None, "enumerate_palindrome_lengths"): {
        "returnFormat": "list[int]", "returnDescription": "各中心の最長回文長を、文字中心と隙間中心の順に並べたlist。",
    },
    ("string/Manacher.py", None, "enumerate_palindromes"): {
        "returnFormat": "list[int]", "returnDescription": "各中心で得られる回文半径を統合したlist。",
    },
    ("string/SuffixArray.py", None, "lcp_array"): {
        "returnFormat": "list[int]", "returnDescription": "lcp[i]がsuffix_array[i]とsuffix_array[i+1]の最長共通接頭辞長となるlist。",
    },
    ("string/ZAlgorithm.py", None, "z_algorithm"): {
        "returnFormat": "list[int]", "returnDescription": "z[i]がsequenceとsequence[i:]の最長共通接頭辞長となるlist。",
    },
    ("bitwise_convolution/SetFunction.py", "SubsetConvolution", "power_projection"): {
        "returnFormat": "list[int]", "returnDescription": "各冪に対する指定係数内積を冪の昇順に並べたlist。",
    },
    ("polynomial/MultipointEvaluation.py", "ProductTree", "evaluate"): {
        "returnFormat": "list[int]", "returnDescription": "登録したpointsと同じ順のpolynomial(points[i])。",
    },
    ("optimization/Matroid.py", "PartitionMatroid", "circuit"): {
        "returnFormat": "list[int]", "returnDescription": "elementを追加すると依存になるときの基本回路の要素番号。独立なら空list。",
    },
})


# Mathematical definitions and concrete return shapes for APIs whose short
# names are not descriptive enough on their own.  Keep these module-scoped:
# names such as get/query/prod are intentionally reused with different meaning.
API_DETAILS_BY_SYMBOL.update({
    ("algorithm/BitAlgorithms.py", None, "msb_index"): {
        "description": r"正整数valueの最上位set bitの位置 $\lfloor\log_2(\mathrm{value})\rfloor$ を返す。",
        "returnFormat": "int",
        "returnDescription": r"$2^i\le\mathrm{value}<2^{i+1}$ を満たす0-indexedのbit位置 $i$。",
    },
    ("algorithm/BitAlgorithms.py", None, "lsb_index"): {
        "description": "正整数valueで最下位に立っているbitの位置を返す。",
        "returnFormat": "int",
        "returnDescription": r"$2^i$ がvalueを割り切る最大の指数 $i$。",
    },
    ("bitwise_convolution/SetFunction.py", "SubsetConvolution", "multiply"): {
        "description": (
            r"集合をbit maskで表し、subset convolution "
            r"$c_S=\sum_{T\subseteq S}\mathrm{first}_T\mathrm{second}_{S\setminus T}$ を求める。"
        ),
        "returnFormat": "list[int]",
        "returnDescription": (
            r"入力と同じ長さの列 $c$。mask $S$ の要素は "
            r"$\sum_{T\subseteq S}\mathrm{first}[T]\mathrm{second}[S\setminus T]\bmod\mathrm{mod}$。"
        ),
    },
    ("bitwise_convolution/SetFunction.py", "SubsetConvolution", "transpose_multiply"): {
        "description": (
            r"subset convolutionの転置作用 "
            r"$c_S=\sum_{T\supseteq S}\mathrm{first}_T\mathrm{second}_{T\setminus S}$ を求める。"
        ),
        "returnFormat": "list[int]",
        "returnDescription": (
            r"入力と同じ長さの列 $c$。mask $S$ の要素は "
            r"$\sum_{T\supseteq S}\mathrm{first}[T]\mathrm{second}[T\setminus S]\bmod\mathrm{mod}$。"
        ),
    },
    ("fps/DualFormalPowerSeries.py", "DualFormalPowerSeries", "get"): {
        "description": "現在の係数列のcopyを取り出す。",
        "returnFormat": "list[int]",
        "returnDescription": r"$[x^i]f(x)$ をindex $i$ に格納した係数列。内部listとは共有しない。",
    },
    ("fps/MultivariateFPS.py", "MultivariateFormalPowerSeries", "get"): {
        "description": r"指定した指数tupleに対応する係数 $[x_0^{i_0}\cdots x_{d-1}^{i_{d-1}}]f$ を返す。",
        "returnFormat": "int",
        "returnDescription": r"$\mathrm{mod}$ で正規化された指定monomialの係数。",
    },
    ("fps/MultivariateFPS.py", "MultivariateFormalPowerSeries", "power"): {
        "description": r"多変数形式的冪級数の整数冪 $f^{\mathrm{exponent}}$ を、保持している各変数の次数範囲で求める。",
        "returnFormat": "MultivariateFormalPowerSeries",
        "returnDescription": r"$f^{\mathrm{exponent}}$ の打ち切られた係数を持つ新しいMultivariateFormalPowerSeries。",
    },
    ("fps/SparseFormalPowerSeries.py", None, "sparse_power"): {
        "description": r"疎な係数列で表した $f(x)^{\mathrm{exponent}}\bmod x^{\mathrm{degree}}$ を求める。",
        "returnFormat": "list[int]",
        "returnDescription": (
            r"長さdegreeの係数列result。$\mathrm{result}[i]=[x^i]f(x)^{\mathrm{exponent}}\bmod\mathrm{mod}$。"
        ),
    },
    ("polynomial/MultipointEvaluation.py", None, "multipoint_evaluation"): {
        "description": r"多項式 $f$ をすべての評価点 $\mathrm{points}_i$ で一括評価する。",
        "returnFormat": "list[int]",
        "returnDescription": r"pointsと同じ長さの列result。$\mathrm{result}[i]=f(\mathrm{points}[i])\bmod\mathrm{mod}$。",
    },
    ("polynomial/PowerEnumerate.py", None, "power_coefficient_enumerate"): {
        "description": (
            r"$n=\deg f$ として、$[x^n]f(x)^i g(x)$ を "
            r"$0\le i\le\mathrm{count}$ の順に一括計算する。gはmultiplier。"
        ),
        "returnFormat": "list[int]",
        "returnDescription": (
            r"長さcount+1の列result。$\mathrm{result}[i]=[x^n]f(x)^i g(x)\bmod\mathrm{mod}$。"
        ),
    },
    ("polynomial/PowerEnumerate.py", None, "power_inner_product_enumerate"): {
        "description": (
            r"各 $i=0,\ldots,\mathrm{count}$ について、係数列weightsとの内積 "
            r"$\sum_j \mathrm{weights}[j][x^j]f(x)^i$ を一括計算する。"
        ),
        "returnFormat": "list[int]",
        "returnDescription": (
            r"長さcount+1の列result。$\mathrm{result}[i]="
            r"\sum_j \mathrm{weights}[j][x^j]f(x)^i\bmod\mathrm{mod}$。"
        ),
    },
    ("polynomial/PolynomialGCD.py", None, "polynomial_gcd"): {
        "description": "2つの多項式のmonicな最大公約多項式を求める。",
        "argumentDescriptions": {
            "first": "定数項から昇冪順に並べた第1多項式の係数列。",
            "second": "定数項から昇冪順に並べた第2多項式の係数列。",
            "mod": "係数体の法。通常は素数を指定する。",
        },
        "returnFormat": "list[int]",
        "returnDescription": "定数項から昇冪順に並べたmonicなGCDの係数列。両方が0多項式なら空list。",
    },
    ("polynomial/PolynomialGCD.py", None, "polynomial_extended_gcd"): {
        "description": r"$s\,\mathrm{first}+t\,\mathrm{second}=g$ を満たすmonicなGCD $g$ とBézout係数 $s,t$ を求める。",
        "argumentDescriptions": {
            "first": "定数項から昇冪順に並べた第1多項式の係数列。",
            "second": "定数項から昇冪順に並べた第2多項式の係数列。",
            "mod": "係数体の法。通常は素数を指定する。",
        },
        "returnFormat": "tuple[list[int], list[int], list[int]]",
        "returnDescription": "(g, s, t)。各要素は定数項から昇冪順の係数列。両入力が0多項式なら3つとも空list。",
        "returnParts": (
            {"name": "g", "format": "list[int]", "description": "monicな最大公約多項式の係数列。"},
            {"name": "s", "format": "list[int]", "description": "firstへ掛けるBézout係数多項式。"},
            {"name": "t", "format": "list[int]", "description": "secondへ掛けるBézout係数多項式。"},
        ),
    },
    ("polynomial/PolynomialResultant.py", None, "polynomial_resultant"): {
        "description": "2つの多項式のresultantをmod上で求める。共通因子を持つ場合は0。",
        "argumentDescriptions": {
            "first": "定数項から昇冪順に並べた第1多項式の係数列。",
            "second": "定数項から昇冪順に並べた第2多項式の係数列。",
            "mod": "係数体の法。通常は素数を指定する。",
        },
        "returnFormat": "int",
        "returnDescription": "modで正規化したresultant。",
    },
    ("segment_tree/SortableSegmentTree.py", "SortableSegmentTree", "query"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ のvaluesを、現在の並び順でopにより左から畳み込む。",
        "returnDescription": "指定区間のopによる畳み込み。空区間ならidentity。",
    },
    ("spatial_structure/LazyKDTree.py", "LazyKDTree", "query"): {
        "description": r"点 $(x,y)$ が半開矩形 $[\mathrm{left},\mathrm{right})\times[\mathrm{down},\mathrm{up})$ に入るweightsをcombineで集約する。",
        "returnDescription": "指定矩形に入る点のweightsをcombineした値。点がなければidentity。",
    },
    ("segment_tree/DynamicLazySegmentTree.py", "DynamicLazySegmentTree", "prod"): {
        "description": r"半開区間 $[\mathrm{query\_left},\mathrm{query\_right})$ をopで左から畳み込む。",
        "returnDescription": "指定区間のopによる畳み込み。空区間ならidentity。",
    },
    ("segment_tree/DynamicSegmentTree.py", "DynamicSegmentTree", "prod"): {
        "description": r"半開区間 $[\mathrm{query\_left},\mathrm{query\_right})$ をopで左から畳み込む。",
        "returnDescription": "指定区間のopによる畳み込み。空区間ならidentity。",
    },
    ("segment_tree/PersistentLazySegmentTree.py", "PersistentLazySegmentTree", "apply"): {
        "description": r"指定versionの半開区間 $[\mathrm{query\_left},\mathrm{query\_right})$ へactionを作用させ、新versionを追加する。",
        "returnFormat": "int",
        "returnDescription": "追加されたversionのID。元のversionは変更しない。",
    },
    ("segment_tree/PersistentLazySegmentTree.py", "PersistentLazySegmentTree", "prod"): {
        "description": r"指定versionの半開区間 $[\mathrm{query\_left},\mathrm{query\_right})$ をopで左から畳み込む。",
        "returnDescription": "指定version・区間のopによる畳み込み。空区間ならidentity。",
    },
    ("segment_tree/PersistentSegmentTree.py", "PersistentSegmentTree", "update_root"): {
        "description": "rootが表す木のindexの値をvalueへ置き換えた新しいrootを作る。",
        "returnFormat": "int",
        "returnDescription": "更新後の木を表す内部root ID。version一覧へは追加しない。",
    },
    ("segment_tree/PersistentSegmentTree.py", "PersistentSegmentTree", "set"): {
        "description": "指定versionのindexの値をvalueへ置き換え、新versionを追加する。",
        "returnFormat": "int",
        "returnDescription": "追加されたversionのID。元のversionは変更しない。",
    },
    ("segment_tree/PersistentSegmentTree.py", "PersistentSegmentTree", "add"): {
        "description": "指定versionのindexへop(value, current)を格納し、新versionを追加する。",
        "returnFormat": "int",
        "returnDescription": "追加されたversionのID。元のversionは変更しない。",
    },
    ("segment_tree/PersistentSegmentTree.py", "PersistentSegmentTree", "prod"): {
        "description": r"指定versionの半開区間 $[l,r)$ をopで左から畳み込む。",
        "returnDescription": "指定version・区間のopによる畳み込み。空区間ならe。",
    },
    ("segment_tree/RangeAddAssignRangeStats.py", "RangeAddAssignRangeStats", "range_sum"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ の要素和を返す。",
        "returnDescription": r"$\sum_{i=\mathrm{left}}^{\mathrm{right}-1}a_i$。",
    },
    ("segment_tree/RangeAffineRangeSum.py", "RangeAffineRangeSum", "range_sum"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ の要素和を返す。",
        "returnDescription": r"$\sum_{i=\mathrm{left}}^{\mathrm{right}-1}a_i$。mod指定時はその剰余。",
    },
    ("segment_tree/RangeLIS.py", "RangeLIS", "query"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ に含まれる部分列のLIS長を求める。",
        "returnFormat": "int",
        "returnDescription": "指定区間の狭義単調増加部分列の最大長。空区間なら0。",
    },
    ("segment_tree/RangeLinearAddRangeMin.py", "RangeLinearAddRangeMin", "query"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ の最小値を返す。",
        "returnFormat": "number",
        "returnDescription": r"$\min_{\mathrm{left}\le i<\mathrm{right}}a_i$。",
    },
    ("segment_tree/SegmentTreeBeats.py", "SegmentTreeBeats", "range_sum"): {
        "description": r"半開区間 $[l,r)$ の要素和を返す。",
        "returnDescription": r"$\sum_{i=l}^{r-1}a_i$。",
    },
    ("segment_tree/SegmentTreeBeats.py", "SegmentTreeBeats", "get"): {
        "description": r"位置pの現在値 $a_p$ を返す。",
        "returnDescription": r"遅延更新を反映した $a_p$。",
    },
    ("range_query/StaticRMQ.py", "StaticRMQ", "query"): {
        "description": r"半開区間 $[l,r)$ の最小値を返す。",
        "returnDescription": r"$\min_{l\le i<r}\mathrm{values}[i]$。",
    },
    ("spatial_structure/DynamicLiChaoTree.py", "DynamicLiChaoTree", "query"): {
        "description": "追加済みの直線・線分をxで評価し、最小値または最大値を返す。",
        "returnFormat": "number",
        "returnDescription": r"minimize=Trueなら $\min_f f(x)$、Falseなら $\max_f f(x)$。",
    },
    ("spatial_structure/LiChaoTree.py", "LiChaoTree", "query"): {
        "description": "追加済みの直線・線分を登録座標xで評価し、最小値または最大値を返す。",
        "returnFormat": "number",
        "returnDescription": r"minimize=Trueなら $\min_f f(x)$、Falseなら $\max_f f(x)$。",
    },
    ("spatial_structure/DynamicPointAddRectangleSum.py", "DynamicPointAddRectangleSum", "query"): {
        "description": r"半開長方形 $[\mathrm{left},\mathrm{right})\times[\mathrm{bottom},\mathrm{top})$ の点重み和queryを登録する。",
        "returnFormat": "None",
        "returnDescription": "値は返さない。solveが登録順の各query結果を返す。",
    },
    ("spatial_structure/PointUpdateRangeTree2D.py", "PointUpdateRangeTree2D", "query"): {
        "description": r"半開長方形 $[\mathrm{left},\mathrm{right})\times[\mathrm{bottom},\mathrm{top})$ 内の点をopで畳み込む。",
        "returnDescription": "指定長方形にある点の値のopによる畳み込み。空ならidentity。",
    },
    ("spatial_structure/RectangleAddRectangleSum.py", "RectangleAddRectangleSum", "query"): {
        "description": r"半開長方形 $[\mathrm{left},\mathrm{right})\times[\mathrm{bottom},\mathrm{top})$ の重み総和queryを登録する。",
        "returnFormat": "None",
        "returnDescription": "値は返さない。solveが登録順の各query結果を返す。",
    },
    ("spatial_structure/StaticRectangleSum.py", "StaticRectangleSum", "query"): {
        "description": r"半開長方形 $[\mathrm{left},\mathrm{right})\times[\mathrm{bottom},\mathrm{top})$ の点重み和queryを登録する。",
        "returnFormat": "None",
        "returnDescription": "値は返さない。solveが登録順の各query結果を返す。",
    },
    ("string/DynamicRollingHash.py", "DynamicRollingHash", "get"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ のrolling hashを返す。",
        "returnFormat": "int | tuple[int, int]",
        "returnDescription": "指定substringのhash。double hashでは2成分のtuple。",
    },
    ("string/RollingHash.py", "RollingHash", "get"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ のrolling hashを返す。",
        "returnFormat": "int | tuple[int, int]",
        "returnDescription": "指定substringのhash。double hashでは2成分のtuple。",
    },
    ("string/RollingHash2D.py", "RollingHash2D", "get"): {
        "description": r"半開長方形 $[\mathrm{upper},\mathrm{lower})\times[\mathrm{left},\mathrm{right})$ の2次元hashを返す。",
        "returnFormat": "int | tuple[int, int]",
        "returnDescription": "指定領域のhash。double hashでは2成分のtuple。",
    },
    ("linear_algebra/F2Matrix.py", "F2Matrix", "get"): {
        "description": r"$\mathbb F_2$ 行列の(row, column)成分を返す。",
        "returnFormat": "bool",
        "returnDescription": "成分が1ならTrue、0ならFalse。",
    },
    ("linear_algebra/F2Matrix.py", "F2Matrix", "power"): {
        "description": r"$\mathbb F_2$ 上の正方行列の整数冪 $A^{\mathrm{exponent}}$ を求める。",
        "returnFormat": "F2Matrix",
        "returnDescription": r"$A^{\mathrm{exponent}}$ を表す新しいF2Matrix。指数0なら単位行列。",
    },
    ("linear_algebra/Matrix.py", None, "matrix_power"): {
        "description": r"正方行列の整数冪 $A^{\mathrm{exponent}}$ をbinary exponentiationで求める。",
        "returnFormat": "list[list[int]]",
        "returnDescription": r"$A^{\mathrm{exponent}}\bmod\mathrm{mod}$ の各行を格納した2次元list。",
    },
    ("algebra/Affine.py", "Affine", "__call__"): {
        "description": r"保持しているaffine変換 $f(x)=ax+b$ をvalueへ適用する。",
        "returnDescription": r"$a\cdot\mathrm{value}+b$。",
    },
    ("string/LongestCommonSubsequence.py", None, "restore_lcs"): {
        "description": "firstとsecondの最長共通部分列を1つ復元する。",
        "returnFormat": "list[object] | str",
        "returnDescription": "両入力の部分列で、長さが最大のものを1つ。文字列入力ならstr、それ以外はlist。",
    },
})


for _module, _owner in (
    ("graph/CSRGraph.py", "CSRSCC"),
    ("graph_connectivity/StronglyConnectedComponents.py", "SCC"),
    ("union_find/DynamicUnionFind.py", "DynamicUnionFind"),
    ("union_find/PartialPersistentUnionFind.py", "PartialPersistentUnionFind"),
    ("union_find/PersistentUnionFind.py", "PersistentUnionFind"),
    ("union_find/RangeParallelUnionFind.py", "RangeParallelUnionFind"),
    ("union_find/RollbackUnionFind.py", "RollbackUnionFind"),
    ("union_find/UnionFind.py", "UnionFind"),
    ("union_find/WeightedUnionFind.py", "WeightedUnionFind"),
):
    API_DETAILS_BY_SYMBOL[(_module, _owner, "same")] = {
        "description": "2要素が指定時点で同じ連結成分に属するか判定する。",
        "returnFormat": "bool",
        "returnDescription": "同じ連結成分ならTrue、異なればFalse。",
    }


for _module, _owner in (
    ("string/DynamicRollingHash.py", "DynamicRollingHash"),
    ("string/RollingHash.py", "RollingHash"),
):
    API_DETAILS_BY_SYMBOL[(_module, _owner, "same")] = {
        "description": "指定した2つの半開区間の文字列が等しいかhashで判定する。",
        "returnFormat": "bool",
        "returnDescription": "2つのsubstringが等しければTrue、異なればFalse。",
    }


API_DETAILS_BY_SYMBOL[("string/RollingHash2D.py", "RollingHash2D", "same")] = {
    "description": "指定した2つの長方形領域が同じ内容か2次元hashで判定する。",
    "returnFormat": "bool",
    "returnDescription": "2つの領域が等しければTrue、異なればFalse。",
}


_FPS998_SERIES_ARGUMENT = (
    r"昇べき順の係数列。`series[i]`は $x^i$ の係数で、各係数は998244353で扱う。"
)
_FPS998_DEGREE_ARGUMENT = (
    r"返す係数数。結果は $x^{\mathrm{degree}}$ で打ち切る。省略時は入力列の長さ。"
)


API_DETAILS_BY_SYMBOL.update({
    ("convolution/NTT998.py", None, "ntt"): {
        "argumentDescriptions": {
            "values": "長さが2の冪である係数list。呼び出し後は周波数表現へ書き換わる。",
        },
        "returnFormat": "list[int]",
        "returnDescription": "周波数表現へ破壊的に書き換えた、入力と同じlist object。",
    },
    ("convolution/NTT998.py", None, "intt"): {
        "argumentDescriptions": {
            "values": "nttで得た長さ2の冪の周波数list。呼び出し後は係数表現へ戻る。",
        },
        "returnFormat": "list[int]",
        "returnDescription": "逆変換と長さの逆数による正規化を適用した、入力と同じlist object。",
    },
    ("convolution/NTT998.py", None, "multiply"): {
        "argumentDescriptions": {
            "first": "第1の昇べき順係数列。",
            "second": "第2の昇べき順係数列。",
        },
        "returnFormat": "list[int]",
        "returnDescription": (
            r"空でない入力には長さ $\lvert\mathrm{first}\rvert+\lvert\mathrm{second}\rvert-1$ の列 $c$。"
            r"$c[k]=\sum_{i+j=k}\mathrm{first}[i]\mathrm{second}[j]\bmod 998244353$。"
            "どちらかが空なら空list。"
        ),
    },
    ("convolution/NTT998.py", None, "square"): {
        "argumentDescriptions": {"series": _FPS998_SERIES_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": (
            r"空でなければ長さ $2\lvert\mathrm{series}\rvert-1$ の $\mathrm{series}(x)^2$ の係数列。"
            "入力が空なら空list。"
        ),
    },
    ("fps998/FPS.py", None, "shrink"): {
        "argumentDescriptions": {"series": _FPS998_SERIES_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": "各係数を998244353で正規化し、最高次側の0を除いた新しい係数list。",
    },
    ("fps998/FPS.py", None, "fps_add"): {
        "argumentDescriptions": {"first": "第1の昇べき順係数列。", "second": "第2の昇べき順係数列。"},
        "returnFormat": "list[int]",
        "returnDescription": r"長い入力と同じ長さの列 $c$。$c[i]=\mathrm{first}[i]+\mathrm{second}[i]\bmod 998244353$。範囲外の係数は0。",
    },
    ("fps998/FPS.py", None, "fps_sub"): {
        "argumentDescriptions": {"first": "被減数の昇べき順係数列。", "second": "減数の昇べき順係数列。"},
        "returnFormat": "list[int]",
        "returnDescription": r"長い入力と同じ長さの列 $c$。$c[i]=\mathrm{first}[i]-\mathrm{second}[i]\bmod 998244353$。範囲外の係数は0。",
    },
    ("fps998/FPS.py", None, "fps_neg"): {
        "argumentDescriptions": {"series": _FPS998_SERIES_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": r"入力と同じ長さの列 $c$。$c[i]=-\mathrm{series}[i]\bmod 998244353$。",
    },
    ("fps998/FPS.py", None, "fps_diff"): {
        "argumentDescriptions": {"series": _FPS998_SERIES_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": r"長さ $\max(0,\lvert\mathrm{series}\rvert-1)$ の形式微分。`result[i-1]=i*series[i] mod 998244353`。",
    },
    ("fps998/FPS.py", None, "fps_integral"): {
        "argumentDescriptions": {"series": _FPS998_SERIES_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": r"定数項0、長さ $\lvert\mathrm{series}\rvert+1$ の形式積分。`result[i+1]=series[i]/(i+1)`。",
    },
    ("fps998/FPS.py", None, "fps_eval"): {
        "argumentDescriptions": {"series": _FPS998_SERIES_ARGUMENT, "value": "代入する有限体の値。"},
        "returnFormat": "int",
        "returnDescription": r"$\sum_i\mathrm{series}[i]\mathrm{value}^i\bmod 998244353$。",
    },
    ("fps998/FPS.py", None, "fps_inv"): {
        "argumentDescriptions": {"series": _FPS998_SERIES_ARGUMENT, "degree": _FPS998_DEGREE_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": r"長さdegreeの係数列result。$\mathrm{series}(x)\mathrm{result}(x)\equiv1\pmod{x^{\mathrm{degree}}}$。",
    },
    ("fps998/FPS.py", None, "fps_log"): {
        "argumentDescriptions": {"series": "定数項が1である昇べき順係数列。", "degree": _FPS998_DEGREE_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": r"長さdegreeの $\log(\mathrm{series}(x))\bmod x^{\mathrm{degree}}$ の係数列。",
    },
    ("fps998/FPS.py", None, "fps_exp"): {
        "argumentDescriptions": {"series": "定数項が0である昇べき順係数列。", "degree": _FPS998_DEGREE_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": r"長さdegreeの $\exp(\mathrm{series}(x))\bmod x^{\mathrm{degree}}$ の係数列。",
    },
    ("fps998/FPS.py", None, "fps_pow"): {
        "argumentDescriptions": {"series": _FPS998_SERIES_ARGUMENT, "exponent": "整数の指数。負の場合は定数項が非0である必要がある。", "degree": _FPS998_DEGREE_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": r"長さdegreeの $\mathrm{series}(x)^{\mathrm{exponent}}\bmod x^{\mathrm{degree}}$ の係数列。",
    },
    ("fps998/FPS.py", None, "fps_sqrt"): {
        "argumentDescriptions": {"series": _FPS998_SERIES_ARGUMENT, "degree": _FPS998_DEGREE_ARGUMENT},
        "returnFormat": "list[int] | None",
        "returnDescription": r"存在すれば長さdegreeの係数列resultで、$\mathrm{result}(x)^2\equiv\mathrm{series}(x)\pmod{x^{\mathrm{degree}}}$。存在しなければNone。",
    },
    ("fps998/FPS.py", None, "fps_div"): {
        "description": r"998244353上で形式的冪級数の商 $numerator(x)/denominator(x)$ を $x^{degree}$ で打ち切って返す。",
        "argumentDescriptions": {
            "numerator": "分子の昇べき順係数列。",
            "denominator": "定数項が非0である分母の昇べき順係数列。",
            "degree": "返す係数数。省略時はnumeratorの長さ。",
        },
        "returnFormat": "list[int]",
        "returnDescription": r"長さdegreeの $numerator(x)/denominator(x)\bmod x^{degree}$ の昇べき順係数列。",
    },
    ("polynomial/PolynomialDivision.py", None, "poly_div"): {
        "description": "昇べき順係数列で表した2多項式を割り、商を返す。",
        "argumentDescriptions": {"dividend": "被除多項式の昇べき順係数列。", "divisor": "0でない除多項式の昇べき順係数列。", "mod": "係数の法。"},
        "returnFormat": "list[number]",
        "returnDescription": "多項式除算の商を、最高次側の0を除いた昇べき順係数列で返す。",
    },
    ("polynomial/PolynomialDivision.py", None, "poly_divmod"): {
        "description": "昇べき順係数列で表した2多項式を割り、商と余りを返す。",
        "argumentDescriptions": {"dividend": "被除数の昇べき順係数列。", "divisor": "0でない除数の昇べき順係数列。", "mod": "係数の法。"},
        "returnFormat": "(quotient, remainder)",
        "returnDescription": "多項式除算の商と余り。余りの次数は除数より小さく、どちらも昇べき順係数list。",
        "returnParts": (
            {"name": "quotient", "format": "list[int]", "description": "商の昇べき順係数列。"},
            {"name": "remainder", "format": "list[int]", "description": "除数より次数が小さい余りの昇べき順係数列。"},
        ),
    },
    ("polynomial/PolynomialDivision.py", None, "poly_mod"): {
        "description": "昇べき順係数列で表した2多項式を割り、余りだけを返す。",
        "argumentDescriptions": {"dividend": "被除数の昇べき順係数列。", "divisor": "0でない除数の昇べき順係数列。", "mod": "係数の法。"},
        "returnFormat": "list[number]",
        "returnDescription": "多項式除算の余りを最高次側の0を除いた昇べき順で格納したlist。",
    },
    ("polynomial/PolynomialDivision998.py", None, "poly_div"): {
        "description": "998244353上で2多項式を割り、商を返す。",
        "argumentDescriptions": {"dividend": "被除多項式の昇べき順係数列。", "divisor": "0でない除多項式の昇べき順係数列。"},
        "returnFormat": "list[int]",
        "returnDescription": "998244353上の多項式除算の商を、最高次側の0を除いた昇べき順係数列で返す。",
    },
    ("polynomial/PolynomialDivision998.py", None, "poly_divmod"): {
        "description": "998244353上で2多項式を割り、商と余りを返す。",
        "argumentDescriptions": {"dividend": "被除多項式の昇べき順係数列。", "divisor": "0でない除多項式の昇べき順係数列。"},
        "returnFormat": "(quotient, remainder)",
        "returnDescription": "998244353上の多項式除算の商と余り。余りの次数は除数より小さい。",
        "returnParts": (
            {"name": "quotient", "format": "list[int]", "description": "商の昇べき順係数列。"},
            {"name": "remainder", "format": "list[int]", "description": "除数より次数が小さい余りの昇べき順係数列。"},
        ),
    },
    ("polynomial/PolynomialDivision998.py", None, "poly_mod"): {
        "description": "998244353上で2多項式を割り、余りだけを返す。",
        "argumentDescriptions": {"dividend": "被除多項式の昇べき順係数列。", "divisor": "0でない除多項式の昇べき順係数列。"},
        "returnFormat": "list[int]",
        "returnDescription": "998244353上の多項式除算の余りを、最高次側の0を除いた昇べき順係数列で返す。",
    },
    ("fps998/FPS.py", None, "taylor_shift"): {
        "argumentDescriptions": {"series": _FPS998_SERIES_ARGUMENT, "shift": "変数へ加える有限体の値。"},
        "returnFormat": "list[int]",
        "returnDescription": r"入力と同じ長さの $\mathrm{series}(x+\mathrm{shift})$ の昇べき順係数列。",
    },
    ("fps998/FPS.py", None, "fps_product"): {
        "argumentDescriptions": {"polynomials": "昇べき順係数listを並べたiterable。"},
        "returnFormat": "list[int]",
        "returnDescription": "全入力多項式の積。入力が0本なら[1]、空多項式を含めば空list。",
    },
    ("fps998/Composition.py", None, "fps_compose"): {
        "argumentDescriptions": {"outer": r"外側のFPS $f$ の係数列。", "inner": r"内側のFPS $g$ の係数列。", "degree": _FPS998_DEGREE_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": r"長さdegreeの $f(g(x))\bmod x^{\mathrm{degree}}$ の係数列。",
    },
    ("fps998/Composition.py", None, "fps_compositional_inv"): {
        "argumentDescriptions": {"series": "定数項0、1次係数が非0であるFPSの係数列。", "degree": _FPS998_DEGREE_ARGUMENT},
        "returnFormat": "list[int]",
        "returnDescription": r"長さdegreeの係数列 $g$。$\mathrm{series}(g(x))\equiv x\pmod{x^{\mathrm{degree}}}$。",
    },
    ("fps998/PowerProjection.py", None, "power_projection"): {
        "argumentDescriptions": {"polynomial": r"多項式 $f$ の昇べき順係数列。", "weights": r"係数ごとの重み列 $w$。", "count": r"求める冪の個数。$0\le i<\mathrm{count}$を返す。"},
        "returnFormat": "list[int]",
        "returnDescription": r"長さcountの列result。$\mathrm{result}[i]=\sum_j\mathrm{weights}[j][x^j]f(x)^i\bmod998244353$。",
    },
    ("fps998/PowerProjection.py", None, "power_coefficient"): {
        "argumentDescriptions": {"polynomial": r"多項式 $f$ の昇べき順係数列。", "multiplier": r"掛け合わせる多項式 $g$。省略時は1。", "count": r"求める冪の個数。省略時は$\deg f+1$。"},
        "returnFormat": "list[int]",
        "returnDescription": r"$n=\deg f$として、長さcountの列result。$\mathrm{result}[i]=[x^n]f(x)^i g(x)\bmod998244353$。",
    },
    ("fps998/LinearRecurrence.py", None, "bostan_mori"): {
        "argumentDescriptions": {"index": "求める0以上の係数番号。", "numerator": r"分子 $P(x)$ の昇べき順係数列。", "denominator": r"定数項が非0の分母 $Q(x)$ の昇べき順係数列。"},
        "returnFormat": "int",
        "returnDescription": r"$[x^{\mathrm{index}}]P(x)/Q(x)\bmod998244353$。",
    },
    ("fps998/LinearRecurrence.py", None, "linear_recurrence_nth"): {
        "argumentDescriptions": {"initial": "漸化式の次数以上の初期値。", "coefficients": r"$a_n=\sum_i\mathrm{coefficients}[i]a_{n-1-i}$の係数。", "index": "求める0以上の添字。"},
        "returnFormat": "int",
        "returnDescription": "指定した線形漸化式で定まるindex番目の値を998244353で割った余り。",
    },
    ("fps998/SubsetSum.py", None, "subset_sum"): {
        "argumentDescriptions": {"counts": "counts[w]が重さwの品物の種類数を表すlist。各種類は0個または1個選ぶ。"},
        "returnFormat": "list[int]",
        "returnDescription": r"countsと同じ長さの列result。$\mathrm{result}[s]=[x^s]\prod_{w\ge1}(1+x^w)^{\mathrm{counts}[w]}$。",
    },
    ("fps998/SubsetSum.py", None, "multiset_sum"): {
        "argumentDescriptions": {"counts": "counts[w]が重さwの種類数を表すlist。各種類は0個以上選べる。"},
        "returnFormat": "list[int]",
        "returnDescription": r"countsと同じ長さの列result。$\mathrm{result}[s]=[x^s]\prod_{w\ge1}(1-x^w)^{-\mathrm{counts}[w]}$。",
    },
    ("fps998/NTT2D.py", None, "ntt2d"): {
        "argumentDescriptions": {"values": r"各辺長が2の冪の長方形係数行列。`values[i][j]`は$x^iy^j$の係数。"},
        "returnFormat": "list[list[int]]",
        "returnDescription": "2次元周波数表現へ破壊的に書き換えた、入力と同じ2次元list object。",
    },
    ("fps998/NTT2D.py", None, "intt2d"): {
        "argumentDescriptions": {"values": "ntt2dで得た長方形の2次元周波数list。"},
        "returnFormat": "list[list[int]]",
        "returnDescription": "逆変換と正規化を適用した、入力と同じ2次元list object。",
    },
    ("fps998/NTT2D.py", None, "multiply2d"): {
        "argumentDescriptions": {"first": "第1の長方形係数行列。", "second": "第2の長方形係数行列。"},
        "returnFormat": "list[list[int]]",
        "returnDescription": r"大きさ$(R_1+R_2-1)\times(C_1+C_2-1)$の係数行列。`result[i][j]`は$x^iy^j$の係数。",
    },
})


API_DETAILS_BY_SYMBOL.update({
    ("algorithm/PermutationGroup.py", None, "simplify_permutation_subgroup"): {
        "description": (
            "入力された生成元と同じ置換群を表す、安定化列の軌道代表元を構築する。"
            "位置をn-1から順に固定し、各位置が移れる先ごとに代表置換を1つ残す。"
        ),
        "argumentDescriptions": {
            "n": "置換が作用する点の個数。点は0からn-1。",
            "permutations": (
                "置換群の生成元。各置換pは長さnのlistで、p[i]が点iの移り先。"
            ),
            "force_size_n": (
                "Trueなら全代表置換を長さnで返す。Falseならlevel iの固定済み末尾を省き、"
                "各代表を長さi+1で返す。"
            ),
        },
        "returnFormat": "list[list[list[int]]]",
        "returnDescription": (
            "外側のindex iが、i+1からn-1を固定した部分群のlevel。"
            "levels[i]には、点iの到達可能な移り先ごとに代表置換が1つ入る。"
            "level内のp[i]は重複せず、全levelの置換を合わせると入力と同じ群を生成する。"
            "群の要素数は、空levelを1として各levelの長さを掛けた値。"
            "例えば3点の対称群S3ではlevel長が[0, 2, 3]となり、群の要素数は1*2*3=6。"
        ),
    },
    ("algorithm/Search.py", None, "kth_element"): {
        "description": (
            "valuesを変更せず、0始まりでindex番目に小さい値をintroselect型のquickselectで返す。"
            "整列済み・逆順の入力は線形走査で検出し、分割が偏り続けた場合はsortへ切り替える。"
        ),
        "argumentDescriptions": {
            "values": "大小比較できる値のiterable。入力object自体は変更しない。",
            "index": "小さい順で取得する位置。0以上len(values)未満。",
        },
        "returnFormat": "object",
        "returnDescription": "valuesを昇順に並べたとき、0始まりでindex番目に置かれる値。",
    },
    ("algorithm/SequenceAlgorithms.py", None, "merge_intervals"): {
        "description": (
            r"半開区間 $[\mathrm{left},\mathrm{right})$ を左端順にまとめ、"
            "互いに重ならない半開区間列を返す。"
        ),
        "argumentDescriptions": {
            "intervals": (
                r"各要素の2値が半開区間 $[\mathrm{left},\mathrm{right})$ を表すiterable。"
            ),
            "merge_adjacent": (
                r"Trueなら $[a,b)$ と $[b,c)$ のように端が接する区間も $[a,c)$ へ結合する。"
                "Falseなら重なる区間だけを結合する。"
            ),
        },
        "returnFormat": "list[tuple[number, number]]",
        "returnDescription": (
            r"左端順に並んだ半開区間 $[\mathrm{left},\mathrm{right})$ の列。"
            "各要素は左端と右端の2値を格納するtupleで、区間の意味は半開。"
        ),
    },
    ("convolution/MiddleProduct.py", None, "middle_product"): {
        "description": (
            r"長い列first上でsecondを1要素ずつずらし、"
            r"$c_i=\sum_{j=0}^{m-1}\mathrm{second}_j\mathrm{first}_{i+j}$ を高速に求める。"
        ),
        "argumentDescriptions": {
            "first": "走査される長さnの列。nはsecondの長さm以上。",
            "second": "firstとの内積に使う、空でない長さmの列。",
            "mod": "各内積を計算する法。",
        },
        "returnFormat": "list[int]",
        "returnDescription": (
            r"長さ $n-m+1$ の列 $c$。$c[i]=\sum_{j=0}^{m-1}"
            r"\mathrm{second}[j]\mathrm{first}[i+j]\bmod\mathrm{mod}$。"
        ),
    },
    ("ordered_set/RangeSet.py", "RangeSet", "add"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ に含まれる整数をすべて追加する。",
        "argumentDescriptions": {
            "left": "追加する半開区間の左端。この値を含む。",
            "right": "追加する半開区間の右端。この値を含まない。",
        },
        "returnFormat": "int",
        "returnDescription": "今回の操作で集合へ新しく加わった整数の個数。空区間なら0。",
    },
    ("ordered_set/RangeSet.py", "RangeSet", "discard"): {
        "description": r"半開区間 $[\mathrm{left},\mathrm{right})$ に含まれる整数をすべて削除する。",
        "argumentDescriptions": {
            "left": "削除する半開区間の左端。この値を含む。",
            "right": "削除する半開区間の右端。この値を含まない。",
        },
        "returnFormat": "int",
        "returnDescription": "今回の操作で集合から実際に削除された整数の個数。空区間なら0。",
    },
    ("ordered_set/RangeSet.py", "RangeSet", "contains"): {
        "description": "整数valueが現在の集合に含まれるか判定する。",
        "argumentDescriptions": {"value": "包含を調べる整数。"},
        "returnFormat": "bool",
        "returnDescription": "valueが保持中の半開区間のどれかに含まれればTrue。",
    },
    ("ordered_set/RangeSet.py", "RangeSet", "mex"): {
        "description": "value以上で、現在の集合に含まれない最小の整数を返す。",
        "argumentDescriptions": {"value": "探索を始める整数。"},
        "returnFormat": "int",
        "returnDescription": "value以上で保持中のどの半開区間にも含まれない最小の整数。",
    },
    ("ordered_set/RangeSet.py", "RangeSet", "intervals"): {
        "description": "現在の整数集合を表す、互いに交わらない半開区間を左端順に列挙する。",
        "returnFormat": "list[tuple[int, int]]",
        "returnDescription": (
            r"各2値が半開区間 $[\mathrm{left},\mathrm{right})$ を表す列。"
            "tupleは端点を格納する形式であり、数学的な開区間を意味しない。"
        ),
    },
    ("ordered_set/RangeSet.py", "RangeSet", "__len__"): {
        "description": "現在保持している、互いに交わらない半開区間の本数を返す。",
        "returnFormat": "int",
        "returnDescription": (
            "保持区間数。集合に含まれる整数の個数ではない。"
            "整数の個数はcovered_lengthで取得する。"
        ),
    },
})


CLASS_DETAILS_BY_SYMBOL = {
    ("segment_tree/SortableSegmentTree.py", "SortableSegmentTree"): {
        "description": (
            "列の部分区間をkeyの昇順・降順へ並べ替えながら、現在の並び順に沿った"
            "区間モノイド積を求める。点更新ではkeyとvalueを同時に置き換える。"
        ),
        "constructorCreates": (
            "keysとvaluesの対応を保った列を作る。updateで1要素を置き換え、"
            "sortで半開区間を並べ替え、queryでその区間のvaluesをopにより集約できる。"
        ),
    },
    ("spatial_structure/LazyKDTree.py", "LazyKDTree"): {
        "description": (
            "固定された二次元点集合に重みを持たせ、半開矩形への遅延作用と"
            "半開矩形内の重みの集約を処理する平衡KD-tree。"
        ),
        "constructorCreates": (
            "各点(xs[i], ys[i])にweights[i]を対応させた木を作る。updateで矩形内へ"
            "作用し、setで1点の重みを置き換え、queryで矩形内をcombineできる。"
        ),
    },
    ("ordered_set/RangeSet.py", "RangeSet"): {
        "description": (
            r"整数集合を、互いに交わらない半開区間 $[\mathrm{left},\mathrm{right})$ "
            "の列へまとめて保持する。長い連続区間を1整数ずつ保存せずに扱える。"
        ),
        "constructorCreates": (
            "空の整数集合を作る。add・discardは半開区間を一括更新し、"
            "contains・mex・intervalsで現在の集合を調べられる。"
        ),
    },
    ("tree/AuxiliaryTree.py", "AuxiliaryTree"): {
        "description": (
            "元の木から、指定した頂点とそれらを結ぶために必要なLCAだけを"
            "抜き出した圧縮木（virtual tree）を構築する。"
        ),
        "constructorCreates": (
            "同じ木に対して、任意の頂点集合から圧縮木を繰り返し構築できる"
            "状態を作る。"
        ),
    },
    ("tree/CentroidDecomposition.py", "CentroidDistanceFenwick"): {
        "description": (
            "静的な重みなし木の各頂点に値を持たせ、点更新と、指定頂点から"
            "一定距離にある頂点の値の合計を処理する。距離は元の木で通る辺の本数。"
        ),
        "constructorCreates": (
            "各頂点の値をadd・setで更新し、queryで距離区間ごとの合計を"
            "求められる状態を作る。valuesを省略した場合、すべての頂点の初期値は0。"
        ),
    },
}


# Big-O is kept separate from descriptive algorithm names.  These entries are
# used when the source alone cannot provide a useful per-API estimate.
COMPLEXITY_BY_MODULE = {
    "fps998/MultipointEvaluation.py": {
        "multipoint_evaluation": "O((N+M) log^2(N+M))",
        "polynomial_interpolation": "O(N log^2 N)",
    },
    "combinatorics/Combination.py": {
        "Comb": "構築 O(size)",
        "ensure": "追加したtable要素数に比例（全呼び出しを通して償却 O(max size)）",
        "F": "償却 O(1)、table拡張分を除く",
        "Fi": "償却 O(1)、table拡張分を除く",
        "inv": "償却 O(1)、table拡張分を除く",
        "C": "償却 O(1)、table拡張分を除く",
        "__call__": "償却 O(1)、table拡張分を除く",
        "P": "償却 O(1)、table拡張分を除く",
        "H": "償却 O(1)、table拡張分を除く",
        "catalan": "償却 O(1)、table拡張分を除く",
        "comb_small_k": "O(min(k, n-k))",
    },
    "tree/LCA.py": {
        "LCA": "構築 O(N)",
        "__call__": "O(1)",
        "dist": "O(1)",
    },
    "combinatorics/BinomialQueries.py": {
        "comb_prefix_sums": "O(max_n + Q sqrt(max_n) + Q log Q)",
    },
    "combinatorial_series/LinearRecurrence.py": {
        "berlekamp_massey_poly": "O(ND)（Dは最短漸化式の次数）",
    },
    "fps/IncreasingSequences.py": {
        "count_increasing_sequences": "O(NW)（Wは正規化後の値域幅）",
    },
    "arithmetic_convolution/MultiplicativeConvolutionModPrime.py": {
        "multiplicative_convolution": "O(prime log prime)",
    },
    "convolution/MinPlusConvolution.py": {
        "minplus_conv": "O(A log(A+C) + C)（Aはarbitrary、Cはconvexの長さ）",
        "minplus_conv_convex": "O(N+M)",
    },
    "optimization/ConvexConcaveConvolution.py": {
        "concave_max_plus_convolution": "O(A log(A+C) + C)（Aはarbitrary、Cはconcaveの長さ）",
    },
    "graph_connectivity/StronglyConnectedComponents.py": {
        "SCC": "O(V+E)",
        "scc": "O(V+E)",
    },
    "graph/CSRGraph.py": {
        "CSRSCC": "O(V+E)",
        "scc_csr": "O(V+E)",
    },
    "graph_enumeration/GraphCounting.py": {
        "count_spanning_trees": "O(V^3)",
    },
    "graph_enumeration/GraphProperties.py": {
        "mcs_order": "O(V+E)",
    },
    "graph_spanning/GraphOrdering.py": {
        "replacement_paths": "O((V+E) log V)",
    },
    "tree/TreeDistanceFrequency.py": {
        "tree_distance_counts": "O(N log^2 N)",
    },
    "algorithm/Fibonacci.py": {
        "fibonacci": "O(log index)",
    },
    "algorithm/SequenceAlgorithms.py": {
        "inversion_count": "O(N log N)",
        "lis": "O(N log N)",
        "coordinate_compress": "O(N log N)",
        "merge_intervals": "O(N log N)",
    },
    "algorithm/DynamicProgramming.py": {
        "knapsack_01": "O(NC)",
        "knapsack_01_max": "O(NC)",
        "subset_sum_possible": "O(N) Python big-int shift/or operations",
        "subset_sum_restore": "O(N + T) Python big-int operations",
    },
    "algorithm/RangeQueries.py": {
        "Mo": "構築 O(1)",
        "add_query": "O(1)",
        "order": "O(Q log Q)",
        "run": "O((N+Q) sqrt(N)) 回程度のcallback",
    },
    "algorithm/Doubling.py": {
        "Doubling": "O(N log K)",
        "jump": "O(log K)",
        "jump_with_sum": "O(log K)",
    },
    "algorithm/Search.py": {
        "binary_search_int": "O(log |true_value-false_value|)",
        "binary_search_float": "O(iterations)",
        "kth_element": "期待 O(N)、最悪 O(N log N)",
    },
    "algorithm/PermutationGroup.py": {
        "simplify_permutation_subgroup": "O(N^2 K) を目安（Kは生成元数）",
    },
    "convolution/MiddleProduct.py": {
        "middle_product": "O(N log N)、短い入力では O(M(N-M+1))",
    },
    "ordered_set/RangeSet.py": {
        "RangeSet": "O(1)",
        "add": "O((K+1) log I)（Kは結合する区間数、Iは保持区間数）",
        "discard": "O((K+1) log I)（Kは交わる区間数、Iは保持区間数）",
        "contains": "O(log I)",
        "mex": "O(log I)",
        "intervals": "O(I)",
        "__len__": "O(1)",
    },
    "algorithm/BitAlgorithms.py": {
        "bit_indices": "O(popcount(mask))",
        "submasks": "O(2^popcount(mask))",
        "supermasks": "O(2^(bit_count-popcount(mask)))",
        "popcount": "O(1) Python int operation",
        "msb_index": "O(1) Python int operation",
        "lsb_index": "O(1) Python int operation",
    },
    "algorithm/Sorting.py": {
        "radix_sort_nonnegative": "O((N+2^digit_bits) ceil(bits/digit_bits))",
        "ensure_permutation": "O(N)",
        "permute": "O(N)",
        "permute_in_place": "O(N)",
        "bucket_sort_permutation": "O(N+maximum)",
        "bucket_sort": "O(N+maximum)",
    },
    "combinatorics/IntegerPartitions.py": {
        "integer_partitions": "O(total output size)",
        "integer_partitions_up_to": "O(total output size)",
    },
    "algorithm/IntegerUtilities.py": {
        "integer_nth_root": (
            "degreeを固定すると O(log B) 回の多倍長整数演算"
            "（B = number.bit_length()）"
        ),
    },
    "fenwick_tree/BIT.py": {
        "BIT": "O(N)（列から構築）、O(N) memory。size指定なら O(N) 初期化",
        "add": "O(log N)",
        "prefix_sum": "O(log N)",
        "sum": "O(log N)",
        "get": "O(log N)",
        "set": "O(log N)",
        "lower_bound": "O(log N)。prefix和が単調非減少であることが必要",
        "__len__": "O(1)",
        "tolist": "O(N)",
        "__str__": "O(N)",
        "__repr__": "O(N)",
    },
    "combinatorics/ErdosGinzburgZiv.py": {
        "erdos_ginzburg_ziv_indices": "O(order^2) bit operations",
    },
    "algorithm/ModularProgression.py": {
        "split_mod_progression": "O(sqrt(count) + number of runs)",
    },
    "random/Random.py": {
        "Random": "O(1)",
        "next_u64": "O(1)",
        "randrange": "期待 O(1)",
        "uniform": "期待 O(1)",
        "uniform_bool": "O(1)",
        "uniform01": "O(1)",
        "choice": "O(1)",
        "shuffle": "O(N)",
        "permutation": "O(N)",
        "sample": "O(N) memory、O(count) swaps",
        "sample_range": "期待 O(count)",
        "array": "sort_result=Falseなら期待 O(length)、Trueなら O(length log length)",
        "bits": "O(length)",
        "matrix": "期待 O(rows * columns)",
        "string": "O(length)",
        "intervals": "期待 O(count)",
        "composition": "期待 O(parts)",
    },
    "random/RandomGraph.py": {
        "Edge": "O(1)",
        "Graph": "O(1)",
        "edge_count": "O(1)",
        "add_directed_edge": "償却 O(1)",
        "add_undirected_edge": "償却 O(1)",
        "to_adjacency_list": "O(N+M)",
        "to_adjacency_matrix": "O(N^2+M)",
        "format_edges": "O(M)",
        "UndirectedGraphGenerator": "O(1)",
        "set_seed": "O(1)",
        "tree": "O(N log N)",
        "path": "O(N)",
        "star": "O(N)",
        "cycle": "O(N)",
        "forest": "期待 O(N)",
        "complete": "O(N^2)",
        "simple": "期待 O(M log N)",
        "connected": "O(N^2+M)",
        "bipartite": "期待 O(M)",
        "erdos_renyi": "O(N^2)",
        "unicyclic": "O(N^2)",
    },
    "prime/Factorization.py": {
        "is_prime": "O(log N) 回の64bit mod乗算",
        "pollard_rho": "期待 O(sqrt(p))（pは最小の素因数）",
        "prime_factors": "期待 O(N^(1/4) log N)",
        "factor_count": "期待 O(N^(1/4) log N)",
        "divisors": "期待 O(N^(1/4) log N + tau(N))",
        "euler_phi": "期待 O(N^(1/4) log N)",
        "mobius": "期待 O(N^(1/4) log N)",
        "factor_count_pairs": "期待 O(N^(1/4) log N)",
    },
    "geometry/Orientation.py": {
        "cross": "O(1)",
        "orientation": "O(1)",
    },
    "geometry/SegmentIntersection.py": {
        "segments_intersect": "O(1)",
    },
    "geometry/ConvexHull.py": {
        "convex_hull": "O(N log N)",
    },
    "geometry/ArgumentSort.py": {
        "argument_sort": "O(N log N)",
    },
    "shortest_path/GridBFS.py": {
        "grid_bfs": "O(HW)",
        "grid_shortest_path": "O(HW)",
    },
    "tree/ZeroOneTree.py": {
        "min_block_inversions": "O(N log N)",
        "min_inversions": "O(N log N)",
    },
}


# Detailed per-operation costs.  Symbols receiving callables also state the
# number of user operations when that cost is not safely treated as O(1).
COMPLEXITY_BY_MODULE.update({
    "segment_tree/RangeAddAssignRangeStats.py": {
        "range_add": "O(log N)",
        "range_assign": "O(log N)",
        "range_sum": "O(log N)",
        "range_min": "O(log N)",
        "range_max": "O(log N)",
        "get": "O(log N)",
        "set": "O(log N)",
        "all_sum": "O(1)",
        "all_min": "O(1)",
        "all_max": "O(1)",
        "__getitem__": "O(log N)",
        "__setitem__": "O(log N)",
    },
    "segment_tree/RangeAffineRangeSum.py": {
        "apply": "O(log N)",
        "range_add": "O(log N)",
        "range_multiply": "O(log N)",
        "range_sum": "O(log N)",
        "get": "O(log N)",
        "set": "O(log N)",
        "all_sum": "O(1)",
        "__getitem__": "O(log N)",
        "__setitem__": "O(log N)",
    },
    "segment_tree/RangeAddCountTopK.py": {
        "range_add": "O(K log N)",
        "range_top_k": "O(K log N)",
        "top_k": "O(K)",
    },
    "segment_tree/RangeLinearAddRangeMin.py": {
        "add": "O(log^2 N)",
        "query": "O(log^2 N)",
    },
    "segment_tree/SortableSegmentTree.py": {
        "SortableSegmentTree": "O(N) time・memory、O(N) 回のop呼び出し",
        "SortableSegmentTree.__init__": "O(N) time・memory、O(N) 回のop呼び出し",
        "update": "O(log N) time、O(log N) 回のop呼び出し",
        "query": "O(log N) time、O(log N) 回のop呼び出し",
        "sort": "O(L log L + L + log N) time、O(L + log N) 回のop呼び出し（L = right-left）",
    },
    "fenwick_tree/DynamicFenwickTree.py": {
        "add": "O(log N) expected dictionary operations",
        "prefix_sum": "O(log N) expected dictionary operations",
        "sum": "O(log N) expected dictionary operations",
    },
    "fenwick_tree/RangeAddRangeSum.py": {
        "add": "O(log N)",
        "prefix_sum": "O(log N)",
        "sum": "O(log N)",
        "get": "O(log N)",
    },
    "union_find/ContiguousUnionFind.py": {
        "merge": "償却 O(alpha(N))",
        "range_merge": "償却 O((K+1) alpha(N))（Kは新しく跨ぐ境界数）",
        "interval": "償却 O(alpha(N))",
    },
    "union_find/DynamicUnionFind.py": {
        "add": "期待 O(1)",
        "find": "償却 O(alpha(N)) expected dictionary operations",
        "merge": "償却 O(alpha(N)) expected dictionary operations",
        "same": "償却 O(alpha(N)) expected dictionary operations",
        "size": "償却 O(alpha(N)) expected dictionary operations",
    },
    "union_find/EnumerateUnionFind.py": {
        "merge": "償却 O(alpha(N))",
        "members": "O(component size)",
    },
    "union_find/MonoidUnionFind.py": {
        "merge": "償却 O(alpha(N)) + O(1) 回のop呼び出し",
        "get": "償却 O(alpha(N))",
        "set": "償却 O(alpha(N))",
        "edges": "償却 O(alpha(N))",
        "has_cycle": "償却 O(alpha(N))",
    },
    "union_find/PartialPersistentUnionFind.py": {
        "find": "O(log N)",
        "merge": "O(log N)",
        "same": "O(log N)",
        "size": "O(log N)",
        "when_unite": "O(log T log N)（Tはmerge回数）",
        "size_ge": "O(log T log N)",
    },
    "union_find/RangeParallelUnionFind.py": {
        "merge": "償却 O(alpha(N))",
        "find": "償却 O(alpha(N))",
        "same": "償却 O(alpha(N))",
        "size": "償却 O(alpha(N))",
    },
    "union_find/WeightedUnionFind.py": {
        "find": "償却 O(alpha(N))",
        "weight": "償却 O(alpha(N))",
        "merge": "償却 O(alpha(N))",
        "same": "償却 O(alpha(N))",
        "diff": "償却 O(alpha(N))",
        "size": "償却 O(alpha(N))",
    },
    "ordered_set/BitSet.py": {
        "set": "O(B)", "reset": "O(B)", "flip": "O(B)",
        "get": "O(B)", "count": "O(B)", "any": "O(1)",
        "all": "O(B)", "find_next": "O(B)", "find_prev": "O(B)",
        "__getitem__": "O(B)", "__int__": "O(1)",
        "__and__": "O(B)", "__or__": "O(B)", "__xor__": "O(B)",
        "__invert__": "O(B)", "__lshift__": "O(B)", "__rshift__": "O(B)（Bはsizeを機械語word数で割った値）",
    },
    "ordered_set/OrderedMap.py": {
        "__setitem__": "期待 O(log N)",
        "__getitem__": "期待 O(log N)",
        "get": "期待 O(1)", "find": "期待 O(1)",
        "erase": "期待 O(log N)",
        "lower_bound": "期待 O(log N)", "upper_bound": "期待 O(log N)",
        "kth_element": "期待 O(log N)", "count": "期待 O(1)",
        "__contains__": "期待 O(1)",
        "__str__": "O(N)", "__repr__": "O(N)",
    },
    "ordered_set/PersistentBinaryTrie.py": {
        "count_value": "O(B)", "add": "O(B)", "discard": "O(B)",
        "kth": "O(B)", "xor_min": "O(B)（Bは管理するbit幅）",
    },
    "ordered_set/PersistentRBSTSet.py": {
        "contains_root": "期待 O(log N)", "insert_root": "期待 O(log N)",
        "erase_root": "期待 O(log N)", "insert": "期待 O(log N)",
        "erase": "期待 O(log N)", "contains": "期待 O(log N)",
        "lower_bound_root": "期待 O(log N)", "lower_bound": "期待 O(log N)",
        "upper_bound": "期待 O(log N)", "kth_root": "期待 O(log N)",
        "kth": "期待 O(log N)",
    },
    "ordered_set/PointSetRangeFrequency.py": {
        "set": "O(log^2 N)", "query": "O(log^2 N)",
    },
    "ordered_set/TopKSum.py": {
        "add": "期待 O(log N)", "discard": "期待 O(log N)", "sum": "O(1)",
    },
    "ordered_set/TreapSet.py": {
        "add": "期待 O(log N)", "discard": "期待 O(log N)",
        "bisect_left": "期待 O(log N)", "bisect_right": "期待 O(log N)",
        "kth": "期待 O(log N)", "ge": "期待 O(log N)",
        "gt": "期待 O(log N)", "le": "期待 O(log N)",
        "lt": "期待 O(log N)", "min": "期待 O(log N)",
        "max": "期待 O(log N)", "__contains__": "期待 O(log N)",
        "__str__": "O(N)", "__repr__": "O(N)",
    },
})

# Return contracts that cannot be reconstructed reliably from return
# expressions alone.  Keep concrete container shape and sentinel meaning here.
API_DETAILS_BY_SYMBOL.update({
    ("algorithm/Search.py", None, "binary_search_int"): {
        "returnFormat": "int",
        "returnDescription": "predicateがTrueになる側で、境界に最も近い整数。",
    },
    ("algorithm/Search.py", None, "binary_search_float"): {
        "returnFormat": "float",
        "returnDescription": "指定回数だけ絞り込んだ、predicateがTrueになる側の境界近似値。",
    },
    ("graph/CycleDetection.py", None, "find_cycle"): {
        "returnFormat": "tuple[list[int], list[int]]",
        "returnDescription": "閉路上の頂点列と、同じ順で閉路を構成するedge ID列。閉路がなければ([], [])。",
    },
    ("graph/TopologicalSort.py", None, "topological_sort"): {
        "returnFormat": "list[int] | None",
        "returnDescription": "頂点のトポロジカル順。閉路があればNone。",
    },
    ("graph_enumeration/GraphCounting.py", None, "evaluate_polynomial"): {
        "returnFormat": "number",
        "returnDescription": "昇冪係数で与えた多項式をpointへ代入した値。",
    },
    ("number_theory/MultiplicativeFunctions.py", None, "dirichlet_multiply"): {
        "returnFormat": "DirichletQuotientSeries",
        "returnDescription": "firstとsecondのDirichlet畳み込みのprefix値を保持する新しいseries。",
    },
    ("linear_algebra/BlackBoxLinearAlgebra.py", None, "black_box_power"): {
        "returnFormat": "list[int]",
        "returnDescription": "operator^exponentをvectorへ作用させた、元と同じ長さのベクトル。",
    },
    ("linear_algebra/Matrix.py", None, "matrix_vector_multiply"): {
        "returnFormat": "list[int]",
        "returnDescription": "result[row]=sum(matrix[row][j]*vector[j]) mod modとなる行数長のベクトル。",
    },
    ("string/SuffixArray.py", None, "suffix_array_with_empty"): {
        "returnFormat": "list[int]",
        "returnDescription": "空suffixの位置len(sequence)を先頭に加えたsuffix array。",
    },
    ("union_find/EnumerateUnionFind.py", "EnumerateUnionFind", "merge"): {
        "returnFormat": "int",
        "returnDescription": "併合後の連結成分の代表頂点。既に同じ成分なら現在の代表頂点。",
    },
    ("union_find/PersistentUnionFind.py", "PersistentUnionFind", "unite"): {
        "returnFormat": "int",
        "returnDescription": "併合後に追加されたversion番号。既に同じ成分でも新versionを1つ追加する。",
    },
    ("union_find/RollbackUnionFind.py", "RollbackUnionFind", "add_value"): {
        "returnFormat": "number",
        "returnDescription": "deltaを加えた後の、xが属する連結成分の集約値。",
    },
    ("ordered_set/BitSet.py", "BitSet", "find_next"): {
        "returnFormat": "int",
        "returnDescription": "index以上で最初に1であるbit位置。存在しなければ-1。",
    },
    ("ordered_set/BitSet.py", "BitSet", "find_prev"): {
        "returnFormat": "int",
        "returnDescription": "index以下で最後に1であるbit位置。存在しなければ-1。",
    },
    ("ordered_set/PersistentBinaryTrie.py", "PersistentBinaryTrie", "add"): {
        "returnFormat": "int",
        "returnDescription": "更新後に追加されたversion番号。元のversionは変更しない。",
    },
    ("ordered_set/PersistentBinaryTrie.py", "PersistentBinaryTrie", "discard"): {
        "returnFormat": "int",
        "returnDescription": "削除後に追加されたversion番号。存在数を超える分は削除しない。",
    },
    ("ordered_set/PersistentRBSTSet.py", "PersistentRBSTSet", "insert_root"): {
        "returnFormat": "int",
        "returnDescription": "keyを含む新しい永続木のroot node番号。既存rootは変更しない。",
    },
    ("ordered_set/PersistentRBSTSet.py", "PersistentRBSTSet", "insert"): {
        "returnFormat": "int", "returnDescription": "挿入後に追加されたversion番号。",
    },
    ("ordered_set/PersistentRBSTSet.py", "PersistentRBSTSet", "erase"): {
        "returnFormat": "int", "returnDescription": "削除後に追加されたversion番号。",
    },
    ("sequence_structure/ErasableHeap.py", "ErasableHeap", "pop"): {
        "returnFormat": "number", "returnDescription": "削除したheap先頭の値。",
    },
    ("sequence_structure/ImplicitTreap.py", "ImplicitTreap", "pop"): {
        "returnFormat": "object", "returnDescription": "削除したindex位置の要素。",
    },
    ("sequence_structure/PersistentArray.py", "PersistentArray", "update_root"): {
        "returnFormat": "int", "returnDescription": "更新後の永続配列を表すroot node番号。",
    },
    ("sequence_structure/PersistentArray.py", "PersistentArray", "set"): {
        "returnFormat": "int", "returnDescription": "更新後に追加されたversion番号。",
    },
    ("sequence_structure/PersistentQueue.py", "PersistentQueue", "append"): {
        "returnFormat": "int", "returnDescription": "末尾へ追加したqueueの新しいversion番号。",
    },
    ("sequence_structure/SkewHeap.py", "SkewHeap", "push"): {
        "returnFormat": "int", "returnDescription": "新しいnodeをmeldした後のheap root番号。",
    },
    ("sequence_structure/SkewHeap.py", "SkewHeap", "pop"): {
        "returnFormat": "int", "returnDescription": "先頭nodeを除いた後のheap root番号。空なら-1。",
    },
    ("graph/CSRGraph.py", "CSRGraph", "from_adjacency"): {
        "returnFormat": "CSRGraph", "returnDescription": "入力隣接listと同じ辺を連続配列に格納したCSRGraph。",
    },
    ("shortest_path/KShortestPaths.py", "KShortestPathDirected", "add_edge"): {
        "returnFormat": "int", "returnDescription": "追加した辺の0-indexed edge ID。",
    },
    ("graph_connectivity/OnlineDynamicConnectivity.py", "OnlineDynamicConnectivity", "link"): {
        "returnFormat": "tuple[int, int]",
        "returnDescription": "新しく全域forestへ入った正規化済み辺(u,v)。多重辺・自己loop・既に連結なら(-1,-1)。",
    },
    ("graph_connectivity/TwoEdgeConnectedComponents.py", "TwoEdgeConnectedComponents", "add_edge"): {
        "returnFormat": "None", "returnDescription": "値は返さない。build前のgraphへ無向辺を追加する。",
    },
    ("graph_flow/AdvancedFlow.py", "PushRelabelMaxFlow", "add_vertex"): {
        "returnFormat": "int", "returnDescription": "追加した頂点の0-indexed番号。",
    },
    ("graph_flow/AdvancedFlow.py", "PushRelabelMaxFlow", "add_edge"): {
        "returnFormat": "int", "returnDescription": "追加した辺の0-indexed edge ID。",
    },
    ("graph_flow/AdvancedFlow.py", "PushRelabelMaxFlow", "flow"): {
        "returnFormat": "number", "returnDescription": "今回残余graphへ追加して流せたflow量。",
    },
    ("graph_flow/MaxFlow.py", "MaxFlowGraph", "add_vertex"): {
        "returnFormat": "int", "returnDescription": "追加した頂点の0-indexed番号。",
    },
    ("graph_flow/MaxFlow.py", "MaxFlowGraph", "add_edge"): {
        "returnFormat": "int", "returnDescription": "追加した辺の0-indexed edge ID。",
    },
    ("graph_flow/MinCostBFlow.py", "MinCostBFlow", "add_edge"): {
        "returnFormat": "int", "returnDescription": "追加した辺の0-indexed edge ID。",
    },
    ("graph_flow/MinCostFlow.py", "MinCostFlowGraph", "add_edge"): {
        "returnFormat": "int", "returnDescription": "追加した辺の0-indexed edge ID。",
    },
    ("graph_flow/MinCostFlow.py", "MinCostFlowGraph", "flow"): {
        "returnFormat": "tuple[number, number]",
        "returnDescription": "(実際に流したflow量, その最小cost)。",
    },
    ("graph_spanning/MergeTree.py", "MergeTree", "restore"): {
        "returnFormat": "list[object]", "returnDescription": "arrangeで並べ替えた値を元の頂点番号順へ戻したlist。",
    },
    ("combinatorics/ArbitraryBinomial.py", "LargePrimeFactorial", "factorial"): {
        "returnFormat": "int", "returnDescription": "n! mod prime。",
    },
    ("rational/RationalFormalPowerSeries.py", "RationalFormalPowerSeries", "evaluate"): {
        "returnFormat": "Fraction", "returnDescription": "係数列を多項式としてpointへ代入した有理数。",
    },
    ("rational/RationalFormalPowerSeries.py", "RationalFormalPowerSeries", "power"): {
        "returnFormat": "RationalFormalPowerSeries",
        "returnDescription": "self^exponentをdegree項で打ち切った新しい有理FPS。",
    },
    ("algebra/FastPower.py", "FastPower", "__call__"): {
        "returnFormat": "int", "returnDescription": "前計算表で求めたbase^exponent mod mod。",
    },
    ("string/PrefixSubstringLCS.py", "PrefixSubstringLCS", "run"): {
        "returnFormat": "list[int]", "returnDescription": "登録したquery ID順のLCS長。",
    },
    ("string/StringSearch.py", "StringSearch", "search"): {
        "returnFormat": "tuple[int, int]",
        "returnDescription": "patternをprefixに持つsuffixがsuffix array上で占める半開区間(left,right)。",
    },
    ("string/SuffixArray.py", "SuffixArray", "search"): {
        "returnFormat": "tuple[int, int]",
        "returnDescription": "patternをprefixに持つsuffixがsuffix array上で占める半開区間(left,right)。",
    },
    ("optimization/RollbackMo.py", "RollbackMo", "add"): {
        "returnFormat": "int", "returnDescription": "追加したqueryの0-indexed ID。",
    },
    ("optimization/SlopeTrick.py", "WeightedSlopeTrick", "evaluate"): {
        "returnFormat": "number", "returnDescription": "保持する区分線形凸関数のpointにおける値。",
    },
    ("game/Nimber.py", "Nimber", "power"): {
        "returnFormat": "Nimber", "returnDescription": "nim積に関するselfのexponent乗。",
    },
    ("heuristic/LogTable.py", "LogTable", "__call__"): {
        "returnFormat": "float", "returnDescription": "周期表に保存したindex位置の対数近似値。",
    },
})

# Public accessors whose meaning depends on their owning data structure.  Keep
# these contracts explicit so get/query/__getitem__ never fall back to a vague
# "stored value" description.
API_DETAILS_BY_SYMBOL.update({
    ("union_find/MonoidUnionFind.py", "MonoidUnionFind", "get"): {
        "description": "nodeが属する連結成分に保持しているmonoid集約値を返す。",
        "returnFormat": "object",
        "returnDescription": "同じ連結成分の初期値をmerge順にopでまとめた値。set後は設定した成分値。",
    },
    ("ordered_set/OrderedMap.py", "OrderedMap", "__getitem__"): {
        "description": "keyに対応する値を返す。未登録ならdefault_factory()の結果を登録して返す。",
        "returnFormat": "object",
        "returnDescription": "keyに登録された値。未登録だった場合は新しく登録したdefault_factory()の結果。",
    },
    ("ordered_set/OrderedMap.py", "OrderedMap", "get"): {
        "description": "keyに対応する値を、mapを変更せず取得する。",
        "returnFormat": "object",
        "returnDescription": "登録済みなら対応する値、未登録ならdefault。新しいkeyは追加しない。",
    },
    ("ordered_set/PointSetRangeFrequency.py", "PointSetRangeFrequency", "query"): {
        "description": "半開区間[left, right)にvalueが現れる回数を返す。",
        "returnFormat": "int",
        "returnDescription": "values[left:right]のうちvalueと等しい要素の個数。",
    },
    ("ordered_set/TopKSum.py", "TopKSum", "sum"): {
        "description": "現在のmultisetから選ばれる上位または下位k個の合計を返す。",
        "returnFormat": "number",
        "returnDescription": "largest=Trueなら大きい方、Falseなら小さい方から最大k個の和。要素数がk未満なら全要素の和。",
    },
    ("sequence_structure/SWAGDeque.py", "SWAGDeque", "fold"): {
        "description": "deque全体を左端から右端へopで畳み込む。",
        "returnFormat": "object",
        "returnDescription": "op(...op(a[0], a[1]), ... , a[-1])。空ならidentity。",
    },
    ("sequence_structure/SWAGQueue.py", "SWAGQueue", "fold"): {
        "description": "queue全体を先頭から末尾へopで畳み込む。",
        "returnFormat": "object",
        "returnDescription": "op(...op(a[0], a[1]), ... , a[-1])。空ならidentity。",
    },
    ("range_query/DisjointSparseTable.py", "DisjointSparseTable", "prod"): {
        "description": "非空の半開区間[l, r)を元の並び順でopにより畳み込む。",
        "returnFormat": "object",
        "returnDescription": "op(...op(values[l], values[l+1]), ... , values[r-1])。",
    },
    ("spatial_structure/SegmentTree2D.py", "SegmentTree2D", "get"): {
        "description": "指定したrow・columnの現在値を返す。",
        "returnFormat": "object",
        "returnDescription": "現在の2次元配列におけるvalues[row][column]。",
    },
    ("graph/CSRGraph.py", "CSRSCC", "__getitem__"): {
        "description": "vertexが属する強連結成分のIDを返す。",
        "returnFormat": "int",
        "returnDescription": "component[vertex]と同じ成分ID。このIDの頂点列はgroups[ID]。",
    },
    ("graph_connectivity/AdvancedConnectivity.py", "ThreeEdgeConnectedComponents", "__getitem__"): {
        "description": "vertexが属する3-edge-connected成分のIDを返す。",
        "returnFormat": "int",
        "returnDescription": "component[vertex]と同じ成分ID。このIDの頂点列はgroups[ID]。",
    },
    ("graph_connectivity/BiconnectedComponents.py", "BlockCutTree", "__getitem__"): {
        "description": "block-cut tree上のnodeに隣接するnode IDを返す。",
        "returnFormat": "list[int]",
        "returnDescription": "tree[node]と同じ隣接list。0以上articulation_count未満は関節点node、それ以降は二重頂点連結成分node。",
    },
    ("graph_connectivity/StronglyConnectedComponents.py", "SCC", "__getitem__"): {
        "description": "vertexが属する強連結成分のIDを返す。",
        "returnFormat": "int",
        "returnDescription": "component[vertex]と同じ成分ID。このIDの頂点列はgroups[ID]。",
    },
    ("graph_connectivity/TwoEdgeConnectedComponents.py", "TwoEdgeConnectedComponents", "__getitem__"): {
        "description": "vertexが属する2-edge-connected成分のIDを返す。",
        "returnFormat": "int",
        "returnDescription": "component[vertex]と同じ成分ID。このIDの頂点列はgroups[ID]。",
    },
    ("number_theory/MultiplicativeFunctions.py", "DirichletQuotientSeries", "__getitem__"): {
        "description": "quotient-seriesの内部indexに保存されたprefix値を返す。",
        "returnFormat": "number",
        "returnDescription": "data[key]。実際の引数xに対応する値はseries[series.index(x)]で取得する。",
    },
    ("number_theory/MultiplicativeFunctions.py", "EnumerateMultiplicativePrefixSum", "get"): {
        "description": "構築時に復元した乗法的関数fのprefix和をvalueで取得する。",
        "returnFormat": "number",
        "returnDescription": "S_f(value)=sum(1<=i<=value) f(i)。valueはN//iとして現れる商、またはsqrt(N)以下の整数。",
    },
    ("rational/SternBrocotNode.py", "SternBrocotNode", "get"): {
        "description": "現在nodeが表す正の既約分数を返す。",
        "returnFormat": "tuple[int, int]",
        "returnDescription": "(numerator, denominator)。値はnumerator/denominatorで、両方とも正、gcdは1。",
    },
    ("tree/DynamicDiameter.py", "DynamicDiameter", "get"): {
        "description": "現在の辺重みに対する木の直径長と、その両端点を返す。",
        "returnFormat": "tuple[number, tuple[int, int]]",
        "returnDescription": "(distance, (first, second))。distanceはfirstからsecondまでの重み和。単一頂点なら距離0で両端は同じ頂点。",
    },
    ("tree/DynamicRerooting.py", "TopTree", "query"): {
        "description": "nodeを根とみなした連結木全体のrerooting DP値を返す。",
        "returnFormat": "object",
        "returnDescription": "vertex・compress・rake・add_edge・add_vertexで木全体を合成した、node根のDP値。",
    },
    ("tree/DynamicRerooting.py", "DynamicRerooting", "query"): {
        "description": "rootを根とみなした連結木全体のrerooting DP値を返す。",
        "returnFormat": "object",
        "returnDescription": "constructorへ渡した5つのDP callbackで木全体を合成した、root根のDP値。",
    },
    ("tree/Rerooting.py", "Rerooting", "__getitem__"): {
        "description": "vertexを根としたときの全方位tree DP結果を返す。",
        "returnFormat": "object",
        "returnDescription": "answer[vertex]と同じ値。全隣接部分木の寄与をmergeし、put_vertexを適用したDP値。",
    },
    ("tree/StaticTopTree.py", "DynamicTreeDP", "get"): {
        "description": "static top tree全体をvertex・compress・rakeで合成した現在値を返す。",
        "returnFormat": "object",
        "returnDescription": "top_tree_root clusterのDP値。setで変更したleaf値をすべて反映する。",
    },
    ("tree/StaticTopTree.py", "EdgeTopTreeDP", "get"): {
        "description": "全辺clusterをedge・compress・rakeで合成した現在値を返す。",
        "returnFormat": "object",
        "returnDescription": "top_tree_root clusterのedge-based DP値。updateした辺leafを反映する。",
    },
    ("tree/StaticTopTree.py", "DynamicRerootingDP", "get"): {
        "description": "vertexを根とみなしたstatic tree全体のDP値を返す。",
        "returnFormat": "object",
        "returnDescription": "rake_forward・rake_backward・compressで全clusterをvertex向きに合成した値。",
    },
    ("tree/StaticTopTree.py", "VertexTopTreeDP", "get"): {
        "description": "全頂点clusterを指定したDP callbackで合成した現在値を返す。",
        "returnFormat": "object",
        "returnDescription": "top_tree_rootのvertex-based path DP値。updateした頂点値を反映する。",
    },
    ("optimization/LineContainer.py", "LineContainer", "query"): {
        "description": "追加済みの全直線をpointで評価した最小値または最大値を返す。",
        "returnFormat": "number",
        "returnDescription": "minimize=Trueならmin(a*point+b)、Falseならmax(a*point+b)。直線がなければ符号付きの無限大sentinel。",
    },
    ("optimization/MonotoneConvexHullTrick.py", "MonotoneConvexHullTrick", "query"): {
        "description": "追加済みの全直線をpointで評価した最小値または最大値を返す。",
        "returnFormat": "number",
        "returnDescription": "minimize=Trueならmin(a*point+b)、Falseならmax(a*point+b)。空ならValueError。",
    },
    ("game/ImpartialGameSolver.py", "ImpartialGameSolver", "get"): {
        "description": "boardから始まる有限不偏ゲームのGrundy数を返す。",
        "returnFormat": "int",
        "returnDescription": "遷移先のGrundy数集合に含まれない最小の非負整数。0なら後手必勝、非0なら先手必勝。",
    },
    ("game/PartisanGameSolver.py", "PartisanGameSolver", "get"): {
        "description": "gameから始まるshort numeric partisan gameの値を返す。",
        "returnFormat": "SurrealNumber",
        "returnDescription": "全てのleft optionより大きく、全てのright optionより小さい最も単純なdyadic有理数。",
    },
    ("heuristic/TopK.py", "TopK", "get"): {
        "description": "hash keyごとの最良値から、小さい方count件を昇順で返す。",
        "returnFormat": "list[object]",
        "returnDescription": "長さmin(count, 異なるhash key数)の昇順list。同じhash keyでは比較上最小のvalueだけを残す。",
    },
})

COMPLEXITY_BY_MODULE.update({
    "convolution/ChirpZ.py": {
        "chirp_z": "O(M(N+C)) modular operations（Nは係数数、Cは評価点数）",
    },
    "convolution/MultidimensionalDFT.py": {
        "multidimensional_dft": "O(S * sum(log base[i])) modular operations（S=product(base)）",
        "multivariate_circular_convolution": "3回のmultidimensional_dft + O(S)",
    },
    "convolution/MultivariateMultiplication.py": {
        "multivariate_multiplication": "O(D*S log S + D^2*S) modular operations（D=len(base), S=product(base)）",
    },
    "fps/CircularSeries.py": {"circular_series": "O(M(N)) modular operations"},
    "fps/CompositeExponential.py": {
        "composite_exponential": "O(M(N) log P) modular operations（Pは入力係数数）",
        "composite_exponential_scaled": "O(M(N) log P) modular operations",
        "inverse_composite_exponential": "O(M(N) log N) modular operations",
    },
    "fps/DualFormalPowerSeries.py": {
        "deg": "O(1)", "get": "O(N)",
        "__add__": "O(N)", "__sub__": "O(N)", "__rsub__": "O(N)",
        "__neg__": "O(N)", "__mul__": "O(M(N)) modular operations",
        "__lshift__": "O(N+shift)",
    },
    "fps/EulerTransform.py": {"euler_transform": "O(M(N)) modular operations"},
    "fps/FPSFraction.py": {
        "__add__": "3回の多項式乗算 + O(N)", "__neg__": "O(N)",
        "__sub__": "3回の多項式乗算 + O(N)",
        "__rsub__": "3回の多項式乗算 + O(N)",
        "__mul__": "2回の多項式乗算", "__truediv__": "2回の多項式乗算",
        "inverse": "O(N)", "shrink": "O(N)",
    },
    "fps/SparseFormalPowerSeries.py": {
        "sparse_inverse": "O(NK)", "sparse_divide": "O(NK)",
        "sparse_exponential": "O(NK)", "sparse_logarithm": "O(NK)",
        "sparse_power": "O(NK)（Nは出力次数、Kは非零項数）",
    },
    "fps/SumOfRationals.py": {
        "sum_of_rationals": "O(M(N) log K) modular operations（Kは分数数、Nは最終次数）",
    },
    "polynomial/GeometricMultipointEvaluation.py": {
        "multipoint_evaluation_geometric": "O(M(N+C)) modular operations",
        "interpolate_geometric": "O(M(N) log N) modular operations",
    },
    "polynomial/PartialFractionDistinct.py": {
        "partial_fraction_distinct": "O(M(N) log N) modular operations",
    },
    "polynomial/PolynomialExponentialSum.py": {
        "limit_sum_polynomial_exponential": "O(M(N)) modular operations",
        "sum_polynomial_exponential": "O(M(N)) modular operations",
    },
    "polynomial/PolynomialGCD.py": {
        "polynomial_monic": "O(N)",
        "polynomial_gcd": "O(M(N) log N) modular operations（Half-GCD法）",
        "polynomial_extended_gcd": "O(M(N) log N) modular operations（Half-GCD法）",
    },
    "polynomial/PolynomialModularPower.py": {
        "polynomial_inverse_mod": "polynomial_extended_gcd(N) + polynomial division",
        "polynomial_pow_mod": "O(M(N) log exponent) modular operations",
    },
    "polynomial/PolynomialPrefixSum.py": {
        "polynomial_prefix_sum": "O(M(N)) modular operations",
    },
    "polynomial/PolynomialResultant.py": {
        "polynomial_resultant": "O(M(N) log N) modular operations（Half-GCD法）",
    },
    "polynomial/PolynomialRoots.py": {
        "polynomial_roots": "期待 O(M(N) log N log mod)、小さいmodでは O(N*mod)",
    },
    "polynomial/PowerEnumerate.py": {
        "power_inner_product_enumerate": "O(M(N) log N + M(C)) modular operations",
        "power_coefficient_enumerate": "O(M(N) log N + M(C)) modular operations",
    },
    "polynomial/PrefixSumPolynomial.py": {
        "prefix_sum_polynomial": "O(M(N)) modular operations",
    },
    "polynomial/ProductGeometricSubstitutions.py": {
        "product_geometric_substitutions": "O(M(N) log count) modular operations",
    },
})

COMPLEXITY_BY_MODULE.update({
    "combinatorial_series/BellNumbers.py": {
        "bell_numbers": "O(M(N)) modular operations",
    },
    "combinatorial_series/BernoulliNumbers.py": {
        "bernoulli_numbers": "O(M(N)) modular operations",
    },
    "combinatorial_series/DerangementNumbers.py": {
        "derangement_numbers": "O(N)",
    },
    "combinatorial_series/PartitionNumbers.py": {
        "partition_numbers": "O(M(N)) modular operations",
    },
    "combinatorial_series/PascalTransform.py": {
        "pascal_transform": "O(M(N)) modular operations",
    },
    "combinatorial_series/PolynomialMobiusTransform.py": {
        "polynomial_mobius_transform": "fps_compose(N) + O(M(N)) modular operations",
    },
    "combinatorial_series/PowerSums.py": {
        "power_sums": "O(M(K) log N) modular operations（K=max_exponent+1）",
        "prefix_sum_powers": "O(M(K)) modular operations",
    },
    "combinatorial_series/StirlingNumbers.py": {
        "stirling_first_row": "O(M(N) log N) modular operations",
        "stirling_second_row": "O(M(N)) modular operations",
        "stirling_first_column": "O(M(N) log column) modular operations",
        "stirling_second_column": "O(M(N) log column) modular operations",
    },
})

COMPLEXITY_BY_MODULE.update({
    "tree/AuxiliaryTree.py": {
        "get": "O(K log K) + O(K) 回のLCA呼び出し（Kは指定頂点数）",
    },
    "tree/EulerTour.py": {
        "idx": "O(1)", "lca": "O(1)", "distance": "O(1)",
        "node_intervals": "O(1)", "edge_intervals": "O(1)",
        "subtree_interval": "O(1)",
    },
    "tree/InclusionTree.py": {"inclusion_tree": "O(N log N)"},
    "tree/ProcessOfMergingTree.py": {"process_of_merging_tree": "O(N alpha(N))"},
    "tree/RootedTree.py": {"rooted_tree": "O(V+E)", "inverse_tree": "O(V)"},
    "tree/TreeDiameter.py": {"tree_diameter": "O(V)", "diameter": "O(V)"},
    "optimization/GoldenSectionSearch.py": {
        "golden_section_search": "O(iterations) function evaluations",
    },
    "optimization/KnapsackBranchAndBound.py": {
        "knapsack_branch_and_bound": "最悪 O(2^N)、各nodeの上界評価は O(1) amortized",
    },
    "optimization/LineContainer.py": {
        "add_line": "償却 O(log N)", "query": "O(log N)",
    },
    "optimization/MaximalRectangle.py": {
        "maximal_rectangle": "O(HW)", "maximal_rectangle_binary": "O(HW)",
    },
    "optimization/MongeShortestPaths.py": {
        "monge_shortest_paths": "O(N log N) cost呼び出し",
        "monge_d_edge_shortest_path": "O(D*(N log N)) cost呼び出し",
    },
    "optimization/MonotoneConvexHullTrick.py": {
        "add_line": "償却 O(1)", "query": "償却 O(1)（xが単調な場合）",
    },
    "optimization/MonotoneMinima.py": {
        "monotone_minima": "O(columns*log(rows+1)+rows) 回のcompare呼び出し",
    },
    "optimization/RollbackMo.py": {
        "add": "O(1)",
        "run": "O((N+Q)*sqrt(Q)) insert呼び出し + O(Q) snapshot/rollback/output呼び出し",
    },
    "game/GrundyNumbers.py": {
        "grundy_numbers": "O(V+E)", "mex": "O(N)",
    },
    "game/ImpartialGameSolver.py": {
        "get": "未計算の到達stateをS、遷移をEとして O(S+E)。optionsは各stateに1回",
        "get_sum": "O(K) + 未計算stateの探索cost",
        "get_best_move": "O(outdegree(game)) options確認 + 未計算stateの探索cost",
    },
    "game/PartisanGameSolver.py": {
        "get": "未計算の到達stateをS、遷移をEとして O(S+E)。optionsは各stateに1回",
    },
    "game/SurrealNumber.py": {
        "reduce_surreal": "O(E) dyadic比較（Eは必要となる2冪分母の指数）",
        "p": "O(1)", "q": "O(1)",
        "__add__": "O(B) bit time", "__sub__": "O(B) bit time",
        "__neg__": "O(B) bit time", "__lt__": "O(B) bit time",
        "__le__": "O(B) bit time", "__gt__": "O(B) bit time",
        "__ge__": "O(B) bit time", "__eq__": "O(B) bit time",
        "__hash__": "O(B) bit time", "__repr__": "O(B)",
        "children": "O(B) bit time", "larger": "O(B) bit time",
        "smaller": "O(B) bit time",
        "between": "O(E) dyadic比較（Bは分子bit長、Eは選ばれる分母指数）",
    },
    "heuristic/LogTable.py": {"__call__": "O(1)"},
    "heuristic/MultiArmedBandit.py": {
        "play": "O(K)", "reward": "O(1)", "best": "O(K)（Kはarm数）",
    },
    "heuristic/SimulatedAnnealing.py": {
        "SimulatedAnnealing.run": "O(iterations) propose/score/random呼び出し",
        "SAManager.run": "O(iterations) update呼び出し",
    },
    "heuristic/TopK.py": {
        "insert": "償却 O(log K)", "normalize": "O(N log N)",
        "get": "O(K)",
    },
})

COMPLEXITY_BY_MODULE.update({
    "graph_matching/DAGMinimumPathCover.py": {
        "dag_minimum_path_cover": "O(E sqrt(V) + V+E)",
    },
    "graph_matching/GeneralMatching.py": {
        "maximum_general_matching": "O(V^3)", "pairs": "O(V)",
    },
    "graph_matching/Hungarian.py": {"hungarian_max": "O(N^3)"},
    "graph_spanning/MinimumSteinerTree.py": {
        "steiner_tree_dp": "O(3^K V + 2^K (V+E) log V)（Kはterminal数）",
    },
    "graph_enumeration/ChromaticNumber.py": {
        "chromatic_number_from_edges": "O(V 2^V)",
    },
    "graph_enumeration/HeldKarp.py": {"held_karp_cycle": "O(V^2 2^V)"},
    "graph_enumeration/MaximumIndependentSet.py": {
        "maximum_independent_set_mask": "最悪 O(2^V)",
        "maximum_independent_set": "最悪 O(2^V + V)",
        "maximum_weight_independent_set": "最悪 O(2^V)",
    },
    "number_theory/FloorSum.py": {
        "floor_sum": "O(log max(modulus, multiplier))",
        "mod_affine_range_count": "O(log modulus)",
    },
    "number_theory/GaussianInteger.py": {
        "gaussian_gcd": "O(log min(norm(first), norm(second))) 回のGaussian整数除算",
        "x": "O(1)", "y": "O(1)",
        "norm": "O(M(B)) bit time", "conjugate": "O(1)",
        "__add__": "O(B) bit time", "__sub__": "O(B) bit time",
        "__neg__": "O(B) bit time", "__mul__": "O(M(B)) bit time",
        "__eq__": "O(B) bit time", "__repr__": "O(B)",
        "__pow__": "O(log exponent) Gaussian整数乗算",
        "__floordiv__": "O(M(B)) bit time", "__mod__": "O(M(B)) bit time（Bは成分のbit長）",
    },
    "number_theory/IntegerArithmetic.py": {
        "gcd": "O(log min(|first|,|second|)) 回の整数剰余",
        "lcm": "O(log min(|first|,|second|)) 回の整数剰余",
        "extended_gcd": "O(log min(|first|,|second|)) 回の整数剰余",
        "inverse_mod": "O(log modulus) 回の整数剰余",
        "inverse_table": "O(limit)",
    },
    "number_theory/IntegerDivision.py": {
        "floor_div": "O(1) 回の整数除算", "ceil_div": "O(1) 回の整数除算",
        "strict_floor_div": "O(1) 回の整数除算", "strict_ceil_div": "O(1) 回の整数除算",
    },
    "number_theory/QuadraticEquationMod.py": {
        "quadratic_equation_mod": "期待 O(log^2 p) modular multiplications（Tonelli--Shanksを含む）",
    },
    "number_theory/TetrationMod.py": {
        "tetration_mod": "法のEuler-phi連鎖ごとの因数分解 + O(log modulus) modular multiplications",
    },
    "number_theory/TwoSquareRepresentations.py": {
        "two_square_representations": "期待 O(N^(1/4) log N + R)（Rは出力数）",
    },
    "combinatorics/FloatBinomial.py": {
        "logfac": "O(1)", "logfinv": "O(1)",
        "logC": "O(1)", "logP": "O(1)",
    },
    "combinatorics/GrayCode.py": {
        "gray_code": "O(1) Python integer operations",
        "inverse_gray_code": "O(log value) shifts/xors",
    },
    "combinatorics/PisanoPeriod.py": {
        "pisano_prime": "因数分解 + O(tau(C) log C) modular operations（Cはp-1または2(p+1)）",
        "pisano_period": "modulusと各候補周期の因数分解cost",
    },
    "combinatorics/QBinomial.py": {
        "QBinomial": "O(maximum) modular multiplications + 1 modular inverse",
        "C": "math.comb(floor(n/order), floor(k/order))のcost + O(1) modular operations",
    },
    "combinatorics/RationalBinomial.py": {
        "fac": "O(1)", "finv": "O(1)", "inv": "O(1)",
        "C": "O(1)", "P": "O(1)", "H": "O(1)",
        "multinomial": "O(K)（Kはparts数）",
    },
    "linear_algebra/Semiring.py": {
        "semiring_matrix_multiply": "H*D*W回ずつのmultiply/add呼び出し",
        "semiring_matrix_power": "O(N^3 log exponent) 回のmultiply/add呼び出し",
        "semiring_linear_recurrence": "O(K^2 log index) 回のmultiply/add呼び出し",
        "__add__": "addを1回呼び出す", "__mul__": "multiplyを1回呼び出す",
        "__eq__": "保持値の比較を1回行う",
    },
    "linear_algebra/XorBasis.py": {
        "insert": "O(B)", "contains": "O(B)", "kth_smallest": "O(B^2)",
        "maximum": "O(B)", "minimum": "O(B)", "xor_kth": "O(B^2)",
        "rank": "O(1)（Bは管理値のbit幅）",
    },
    "rational/Digamma.py": {"digamma": "O(max(0, threshold-x)) scalar steps"},
    "rational/InverseSum.py": {"inverse_sum": "O(sqrt(N))"},
    "rational/RationalNumberSearch.py": {
        "has_next": "O(1)", "get_next": "O(1)", "give": "O(1)",
    },
    "rational/SternBrocotNode.py": {
        "get": "O(1)", "lower_bound": "O(1)", "upper_bound": "O(1)",
        "depth": "O(R)（Rはrun-length path長）",
        "go_left": "償却 O(1)", "go_right": "償却 O(1)",
        "go_parent": "O(number of removed runs)", "lca": "O(min(R1,R2))",
    },
    "algebra/Affine.py": {
        "__call__": "O(1)", "__mul__": "O(1)", "__eq__": "O(1)",
    },
    "algebra/PowerTable.py": {"power_table": "O(length)"},
})

COMPLEXITY_BY_MODULE.update({
    "sequence_structure/CartesianTree.py": {
        "cartesian_tree": "O(N)", "cartesian_tree_graph": "O(N)",
    },
    "sequence_structure/ErasableHeap.py": {
        "push": "O(log N)", "erase": "償却 O(log N)",
        "top": "償却 O(log N)", "pop": "償却 O(log N)",
        "__str__": "O(N log N)", "__repr__": "O(N log N)",
    },
    "sequence_structure/PersistentQueue.py": {
        "append": "O(1)", "popleft": "O(1)", "front": "O(1)",
    },
    "sequence_structure/SWAGDeque.py": {
        "appendleft": "償却 O(1) 回のop呼び出し",
        "append": "償却 O(1) 回のop呼び出し",
        "popleft": "償却 O(1) 回のop呼び出し",
        "pop": "償却 O(1) 回のop呼び出し",
        "fold": "O(1) 回のop呼び出し",
        "__str__": "O(N)", "__repr__": "O(N)",
    },
    "sequence_structure/SWAGQueue.py": {
        "append": "償却 O(1) 回のop呼び出し",
        "popleft": "償却 O(1) 回のop呼び出し",
        "fold": "O(1) 回のop呼び出し",
        "__str__": "O(N)", "__repr__": "O(N)",
    },
    "sequence_structure/SkewHeap.py": {
        "new_node": "O(1)", "meld": "償却 O(log N)",
        "push": "償却 O(log N)", "add_all": "O(1)",
        "top": "O(1)", "pop": "償却 O(log N)",
    },
    "sequence_structure/SlidingWindowMinimum.py": {
        "sliding_window_minimum": "O(N)",
    },
    "spatial_structure/CompressedFenwick2D.py": {
        "add": "O(log^2 N)", "prefix_sum": "O(log^2 N)",
        "sum": "O(log^2 N)",
    },
    "spatial_structure/CumulativeSum2D.py": {"sum": "O(1)"},
    "spatial_structure/DynamicLiChaoTree.py": {
        "add_line": "O(log W)", "add_segment": "O(log^2 W)",
        "query": "O(log W)（Wは座標domain幅）",
    },
    "spatial_structure/DynamicPointAddRectangleSum.py": {
        "add": "O(1)", "query": "O(1)",
        "solve": "O((U+Q) log^2 U)（Uは点追加数、Qはquery数）",
    },
    "spatial_structure/FenwickTree2D.py": {
        "add": "O(log H log W)", "prefix_sum": "O(log H log W)",
        "sum": "O(log H log W)",
    },
    "spatial_structure/LazyKDTree.py": {
        "LazyKDTree": "O(N log N) time、O(N) memory、O(N) 回のcombine呼び出し",
        "LazyKDTree.__init__": "O(N log N) time、O(N) memory、O(N) 回のcombine呼び出し",
        "update": "期待 O(sqrt(N))、最悪 O(N) + 訪問nodeごとにmapping/composition",
        "set": "O(log N)（構築された平衡木の高さ）+ 各祖先でcombine",
        "query": "期待 O(sqrt(N))、最悪 O(N) + 訪問nodeごとにcombine",
    },
    "spatial_structure/PointUpdateRangeTree2D.py": {
        "add_point": "O(1)（build前の登録）", "build": "O(N log N)",
        "add": "O(log^2 N)", "set": "O(log^2 N)",
        "query": "O(log^2 N) 回のop呼び出し",
    },
    "spatial_structure/RectangleAddRectangleSum.py": {
        "add": "O(1)", "query": "O(1)",
        "solve": "O((R+Q) log(R+Q))（Rは矩形追加数、Qはquery数）",
    },
    "spatial_structure/SegmentTree2D.py": {
        "set": "O(log H log W) 回のop呼び出し",
        "get": "O(1)", "prod": "O(log H log W) 回のop呼び出し",
        "__str__": "O(HW)", "__repr__": "O(HW)",
    },
    "spatial_structure/StaticRectangleSum.py": {
        "add": "O(1)", "query": "O(1)",
        "solve": "O((N+Q) log N)（Nは点数、Qはquery数）",
    },
    "spatial_structure/UnionRectangle.py": {
        "union_rectangle_area": "O(N log N)",
        "add": "O(1)", "run": "O(N log N)",
    },
    "graph/DFSForest.py": {"dfs_forest": "O(V+E)"},
    "graph/DimensionExpandedGraph.py": {
        "valid": "O(D)", "id": "O(D)", "coordinate": "O(D)",
        "extra_id": "O(1)", "neighbors": "O(D)",
        "bfs": "O(V+E)。transitionsは到達頂点ごとに1回、既定gridでは E<=2DV",
        "bfs01": "O(V+E)。transitions呼び出しを含む",
        "dijkstra": "O((V+E) log V)。transitionsは確定頂点ごとに1回",
    },
    "graph/GraphFromEdges.py": {"graph_from_edges": "O(V+E)"},
    "graph/GridToGraph.py": {"grid_to_graph": "O(HW + E)"},
    "graph/RangeEdgeGraph.py": {
        "add_point_to_point": "O(1)",
        "add_point_to_range": "O(log N)", "add_range_to_point": "O(log N)",
        "add_range_to_range": "O(log N)", "add_edge": "O(1)",
    },
    "graph/RestorePath.py": {"restore_path": "O(path length)"},
    "graph/ReverseGraph.py": {"reverse_graph": "O(V+E)"},
    "graph/TopologicalSort.py": {"topological_sort": "O(V+E)"},
    "graph/TwoSAT.py": {
        "literal": "O(1)", "add_implication_literal": "O(1)",
        "add_clause_literal": "O(1)", "add_clause": "O(1)",
        "set_value": "O(1)", "add_xor": "O(1)", "add_equal": "O(1)",
        "solve": "O(V+E)",
    },
    "shortest_path/BFS.py": {"bfs": "O(V+E)"},
    "shortest_path/BellmanFord.py": {"bellman_ford": "O(VE)"},
    "shortest_path/DialDijkstra.py": {
        "dial_dijkstra": "O(E+V*C)（Cは最大辺重み）",
    },
    "shortest_path/Dijkstra.py": {"dijkstra": "O((V+E) log V)"},
    "shortest_path/WarshallFloyd.py": {"warshall_floyd": "O(V^3)"},
    "shortest_path/ZeroOneBFS.py": {"zero_one_bfs": "O(V+E)"},
    "graph_connectivity/BipartiteColoring.py": {"bipartite_coloring": "O(V+E)"},
    "graph_connectivity/ConnectedComponents.py": {"connected_components": "O(V+E)"},
    "graph_connectivity/DynamicBipartiteGraph.py": {
        "find": "償却 O(alpha(N))", "color": "償却 O(alpha(N))",
        "can_add_edge": "償却 O(alpha(N))", "add_edge": "償却 O(alpha(N))",
        "is_bipartite": "O(1)",
    },
})


# MASPyPy/libraryを追加候補の参照元として精査した第一バッチ。
SEARCH_TERMS_BY_MODULE.update({
    "optimization/SMAWK.py": (
        "全単調行列",
        "totally monotone matrix",
        "行最小",
    ),
    "optimization/LARSCH.py": (
        "オンライン行最小",
        "Monge DP",
        "下三角Monge",
    ),
    "range_query/RangeMex.py": ("区間mex", "range mex"),
    "algorithm/ParallelBinarySearch.py": (
        "並列二分探索",
        "offline binary search",
    ),
    "graph_connectivity/DominatorTree.py": (
        "支配木",
        "immediate dominator",
        "Lengauer Tarjan",
    ),
})

MODULE_CAPABILITIES.update({
    "optimization/SMAWK.py": (
        "要素を必要なときだけcallbackで評価し、totally monotoneな行列の各行の最小列を求められる。",
        "同じ最小値を取る列が複数ある場合は、最小の列番号を返す。",
    ),
    "optimization/LARSCH.py": (
        "下三角Monge行列のrow 0, 1, ...について、列0からrowまでの最小位置を順番に取得できる。",
        "行列全体を保存せず、callbackで必要な要素だけを評価する。",
    ),
    "range_query/RangeMex.py": (
        "静的な整数列に対する複数の半開区間mexを、queryの入力順で一括計算できる。",
        "負数とlen(values)より大きい値はmexへ影響しないため、内部表へ保存しない。",
    ),
    "algorithm/ParallelBinarySearch.py": (
        "同じ更新列を共有する複数の単調判定について、true側とfalse側の境界をまとめて二分探索できる。",
        "判定方向に応じてokとngを入れ替え、最初にtrueとなる時刻と最後にtrueである時刻の両方を求められる。",
    ),
    "graph_connectivity/DominatorTree.py": (
        "有向グラフで、rootから頂点vへ至るすべてのpathが最後に共通して通るimmediate dominatorを求められる。",
        "rootから到達できない頂点も含む隣接listをそのまま渡せる。",
    ),
})
MODULE_CAPABILITIES["random/Random.py"] += (
    "指定した組数のbalanced bracket stringを一様ランダムに生成できる。",
    "Monge不等式を満たす整数行列を、再現可能なランダムテストとして生成できる。",
)

API_DETAILS_BY_SYMBOL.update({
    ("optimization/SMAWK.py", None, "smawk"): {
        "description": "totally monotoneな行列について、各行で最小値を取る最小の列番号を求める。",
        "argumentDescriptions": {
            "rows": "行数。",
            "columns": "列数。rowsが正なら1以上でなければならない。",
            "value": "value(row, column)で行列要素を返すcallback。betterを指定する場合は不要。",
            "better": "better(row, candidate, current)でcandidate列の方が真に小さいときTrueを返すcallback。",
        },
        "returnFormat": "list[int]",
        "returnDescription": "長さrowsの列result。result[row]はその行で最小値を取る最小の列番号。",
    },
    ("optimization/LARSCH.py", "LARSCH", "get_argmin"): {
        "description": "まだ返していない次のrowについて、列0からrowまでの最小位置を返す。",
        "returnFormat": "int",
        "returnDescription": "次のrowで最小値を取る最小のcolumn。row 0から順に1個ずつ返す。",
    },
    ("optimization/LARSCH.py", "LARSCH", "reset"): {
        "description": "同じ行列のrow 0からargminを取り直せる状態へ戻す。",
        "returnFormat": "None",
        "returnDescription": "値は返さない。次のget_argminがrow 0を処理するように内部位置を戻す。",
    },
    ("range_query/RangeMex.py", None, "range_mex"): {
        "description": "整数列の複数の半開区間について、区間内に現れない最小の非負整数を求める。",
        "argumentDescriptions": {
            "values": "mexを調べる整数列。",
            "queries": r"半開区間 $[\mathrm{left},\mathrm{right})$ を表す2要素列の並び。",
        },
        "returnFormat": "list[int]",
        "returnDescription": r"queriesと同じ長さの列result。result[i]はqueries[i]が表す半開区間のmex。",
    },
    ("algorithm/ParallelBinarySearch.py", None, "parallel_binary_search"): {
        "description": "同じ時系列更新に対する複数の単調な判定をまとめて二分探索し、各queryのtrue側境界を求める。",
        "argumentDescriptions": {
            "query_count": "判定するqueryの個数。checkへ0からquery_count-1を渡す。",
            "ok": "すべてのqueryでcheckがTrueだと既知の更新回数。",
            "ng": "すべてのqueryでcheckがFalseだと既知の更新回数。okより小さくても大きくてもよい。",
            "reset": "引数なしで、更新を0回適用した状態へ戻すcallback。探索roundごとに呼ぶ。",
            "update": "update(t)で0-indexedのt番目の更新を1回適用するcallback。",
            "check": "現在まで更新した状態で、check(query)がそのqueryの判定結果をboolで返すcallback。",
        },
        "returnFormat": "list[int]",
        "returnDescription": "長さquery_countの列result。ng < okならresult[q]は最初にTrueとなる更新回数、ok < ngなら最後にTrueである更新回数。",
    },
    ("graph_connectivity/DominatorTree.py", None, "dominator_tree"): {
        "description": "rootからvへの全有向pathに含まれる頂点のうち、vに最も近いstrict dominatorを各vについて求める。",
        "argumentDescriptions": {
            "graph": "graph[u]にuから出る行き先v、または先頭要素がvのtupleを並べた有向隣接list。",
            "root": "pathの始点とする頂点。",
        },
        "returnFormat": "list[int]",
        "returnDescription": "頂点数と同じ長さのidom。idom[root]=root、到達不能な頂点は-1、それ以外のidom[v]はvのimmediate dominator。",
    },
    ("random/Random.py", "Random", "brackets"): {
        "description": "指定した組数のbalanced bracket stringを一様ランダムに生成する。",
        "argumentDescriptions": {
            "pairs": "openingとclosingをそれぞれ使う個数。",
            "opening": "opening bracketとして出力する文字列。",
            "closing": "closing bracketとして出力する文字列。",
        },
        "returnFormat": "str",
        "returnDescription": "openingとclosingをpairs個ずつ含み、左から読んだ各prefixでopening数がclosing数以上となる文字列。",
    },
    ("random/Random.py", "Random", "monge"): {
        "description": "Monge不等式を満たすランダムな整数行列を生成する。",
        "argumentDescriptions": {
            "rows": "生成する行数。",
            "columns": "生成する列数。",
            "difference_max": "隣接4要素のMonge差へ使う0以上の乱数の上限。",
            "offset": "各行・各列へ加える独立な整数offsetの絶対値上限。",
        },
        "returnFormat": "list[list[int]]",
        "returnDescription": r"rows行columns列のmatrix。$i_1<i_2, j_1<j_2$ に対して $A_{i_1,j_1}+A_{i_2,j_2}\le A_{i_1,j_2}+A_{i_2,j_1}$ を満たす。",
    },
})

CLASS_DETAILS_BY_SYMBOL[("optimization/LARSCH.py", "LARSCH")] = {
    "description": "下三角Monge行列をcallbackで評価し、各rowのargminをrow順にオンライン取得する。",
    "constructorCreates": "size行の下三角行列を表すvalue(row, column)を保持する。get_argminを呼ぶたびに次のrowについて、0以上row以下で最小値を取る最小columnを返せる。",
    "argumentDescriptions": {
        "size": "行数。",
        "value": "value(row, column)で下三角行列の要素を返すcallback。0 <= column <= row < sizeの範囲で呼ばれる。",
    },
}

COMPLEXITY_BY_MODULE.update({
    "optimization/SMAWK.py": {
        "smawk": "O(rows + columns) 回のvalueまたはbetter呼び出し、O(rows + columns) memory",
    },
    "optimization/LARSCH.py": {
        "LARSCH": "構築 O(log N) time、O(log N) memory",
        "get_argmin": "全N回を通して O(N) 回のvalue呼び出し（1回あたり償却 O(1)）",
        "reset": "O(log N)",
    },
    "range_query/RangeMex.py": {
        "range_mex": "O((N+Q) log N) time、O(N+Q) memory",
    },
    "algorithm/ParallelBinarySearch.py": {
        "parallel_binary_search": "O((U+Q) log(|ok-ng|+1)) callback呼び出し、O(U+Q) memory",
    },
    "graph_connectivity/DominatorTree.py": {
        "dominator_tree": "O((V+E) alpha(V)) time、O(V+E) memory",
    },
})
COMPLEXITY_BY_MODULE["random/Random.py"].update({
    "brackets": "O(pairs)",
    "monge": "O(rows * columns)",
})


# MASPyPy/libraryを追加候補の参照元として精査した第二バッチ。
SEARCH_TERMS_BY_MODULE.update({
    "graph_connectivity/ComplementGraph.py": (
        "補グラフ", "complement graph", "補グラフBFS",
    ),
    "range_query/RangeXorBasis.py": (
        "区間XOR基底", "range xor basis", "部分集合XOR",
    ),
    "shortest_path/KShortestWalks.py": (
        "k shortest walk", "sidetrack", "Eppstein",
    ),
    "graph_matching/StableMatching.py": (
        "安定結婚", "stable marriage", "Gale Shapley",
    ),
    "tree_query/TreeWaveletMatrix.py": (
        "木上wavelet matrix", "path kth", "部分木k番目",
    ),
})

MODULE_CAPABILITIES.update({
    "graph_connectivity/ComplementGraph.py": (
        "元の隣接listで辺が存在しない異なる頂点対を辺とみなし、補グラフを明示構築せずにBFSできる。",
        "無向グラフの補グラフを連結成分へ分けられる。元のグラフが密でも、補辺を列挙せず処理する。",
    ),
    "range_query/RangeXorBasis.py": (
        "静的な非負整数列の複数の半開区間について、区間内の値が張るXOR線形基底を一括計算できる。",
        "各区間から任意個の値を選んだsubset XORとinitialとのXORを最大化できる。",
    ),
    "shortest_path/KShortestWalks.py": (
        "非負辺重みの有向グラフで、sourceからtargetへ至るwalkのコストを小さい順に最大k個列挙できる。",
        "既存KShortestPathsと異なり、同じ頂点・辺を何度でも通るwalkを対象にする。cycleや平行辺も区別する。",
    ),
    "graph_matching/StableMatching.py": (
        "両側の厳密な希望順を満たすstable matchingのうち、first側の各要素にとって最適なものを求められる。",
        "希望listを途中で切ることで、相手によってmatchingを拒否できる不完全listも扱える。",
    ),
    "tree_query/TreeWaveletMatrix.py": (
        "静的な木の2頂点間pathまたはrooted subtreeについて、k番目に小さい頂点値を求められる。",
        "path・部分木内で、半開値域lower以上upper未満に入る頂点数を数えられる。負数と重複値も扱える。",
    ),
})

API_DETAILS_BY_SYMBOL.update({
    ("graph_connectivity/ComplementGraph.py", None, "complement_bfs"): {
        "description": "元のgraphに辺がない異なる頂点対を辺とみなし、その補グラフでsourceからBFSする。",
        "argumentDescriptions": {
            "graph": "graph[v]に元の有向辺の行き先、または先頭要素が行き先のtupleを並べた隣接list。補辺そのものは渡さない。",
            "source": "補グラフ上の距離を測る始点。",
        },
        "returnFormat": "tuple[list[int], list[int]]",
        "returnDescription": "第1要素はdistance、第2要素はparent。どちらも頂点番号順の長さVの列。",
        "returnParts": (
            {
                "name": "distance", "format": "list[int]",
                "description": "distance[v]は補グラフでのsourceからvへの最短辺数。到達不能なら-1。",
            },
            {
                "name": "parent", "format": "list[int]",
                "description": "parent[v]はBFS木でvの直前にある頂点。sourceと到達不能頂点では-1。",
            },
        ),
    },
    ("graph_connectivity/ComplementGraph.py", None, "complement_components"): {
        "description": "無向graphの補グラフを連結成分へ分ける。",
        "argumentDescriptions": {
            "graph": "各無向辺を両端の隣接listへ入れた元グラフ。要素は行き先、または先頭要素が行き先のtuple。",
        },
        "returnFormat": "list[list[int]]",
        "returnDescription": "補グラフの連結成分を発見順に並べた列。各内側listにはその成分の頂点をBFS発見順で1回ずつ格納する。",
    },
    ("range_query/RangeXorBasis.py", None, "range_xor_basis"): {
        "description": "各半開区間内の値から任意個を選んで作れるXOR全体を張る線形基底を求める。",
        "argumentDescriptions": {
            "values": "非負整数を並べた静的な入力列。",
            "queries": r"半開区間 $[\mathrm{left},\mathrm{right})$ を表す2要素列の並び。",
        },
        "returnFormat": "list[list[int]]",
        "returnDescription": "queriesと同じ長さのbases。bases[q]はqueries[q]内の値と同じsubset XOR全体を張る独立な整数列で、最高bitが高い順に並ぶ。",
    },
    ("range_query/RangeXorBasis.py", None, "range_max_xor"): {
        "description": "各半開区間から任意個の値を選び、そのXORとinitialとのXORを最大化する。",
        "argumentDescriptions": {
            "values": "非負整数を並べた静的な入力列。",
            "queries": r"半開区間 $[\mathrm{left},\mathrm{right})$ を表す2要素列の並び。",
            "initial": "各queryでsubset XORと組み合わせる共通の非負整数。空subsetも選べる。",
        },
        "returnFormat": "list[int]",
        "returnDescription": r"queriesと同じ長さのresult。result[q]は $\max_{S\subseteq[\mathrm{left},\mathrm{right})}(\mathrm{initial}\mathbin{\mathtt{xor}}\bigoplus_{i\in S}\mathrm{values}[i])$。",
    },
    ("shortest_path/KShortestWalks.py", None, "k_shortest_walks"): {
        "description": "sourceからtargetへ至るwalkを辺列の違いで区別し、コストを小さい順に最大k個列挙する。",
        "argumentDescriptions": {
            "vertex_count": "有向グラフの頂点数。",
            "edges": "有向辺を(from, to, nonnegative_cost)で並べた列。平行辺は別の辺として扱う。",
            "source": "walkの始点。",
            "target": "walkの終点。",
            "k": "先頭から取得するwalk数の上限。0以下なら空listを返す。",
        },
        "returnFormat": "list[number]",
        "returnDescription": "存在するwalkのコストを小さい順に最大k個並べた列。walkがk個未満なら存在する分だけ返し、source=targetでは空walkのコスト0が先頭になる。",
    },
    ("graph_matching/StableMatching.py", None, "stable_matching"): {
        "description": "first側から順に提案し、blocking pairがないmatchingのうちfirst側最適なものを求める。",
        "argumentDescriptions": {
            "first_preferences": "first_preferences[first]に、受け入れ可能なsecond番号を希望が高い順に重複なく並べる。省略したsecondは受け入れない。",
            "second_preferences": "second_preferences[second]に、受け入れ可能なfirst番号を希望が高い順に重複なく並べる。省略したfirstは受け入れない。",
        },
        "returnFormat": "tuple[list[int], list[int]]",
        "returnDescription": "第1要素はmatch_first、第2要素はmatch_second。両側から同じmatchingを参照できる。",
        "returnParts": (
            {
                "name": "match_first", "format": "list[int]",
                "description": "match_first[first]は対応するsecond番号。matchingされなければ-1。",
            },
            {
                "name": "match_second", "format": "list[int]",
                "description": "match_second[second]は対応するfirst番号。matchingされなければ-1。",
            },
        ),
    },
    ("tree_query/TreeWaveletMatrix.py", "TreeWaveletMatrix", "kth_path"): {
        "description": "firstからsecondまでの両端を含む単純path上で、k番目に小さい頂点値を返す。",
        "argumentDescriptions": {"first": "pathの一端。", "second": "pathの他端。", "k": "小さい方から数えた順位。0 <= k < path頂点数。"},
        "returnFormat": "int",
        "returnDescription": "path上の頂点値を重複込みで昇順に並べたときのk番目の値。",
    },
    ("tree_query/TreeWaveletMatrix.py", "TreeWaveletMatrix", "count_path"): {
        "description": "firstからsecondまでの両端を含む単純path上で、指定値域に入る頂点数を数える。",
        "argumentDescriptions": {"first": "pathの一端。", "second": "pathの他端。", "lower": "含める値の下端。", "upper": "含めない値の上端。"},
        "returnFormat": "int",
        "returnDescription": r"path上で $\mathrm{lower}\le\mathrm{values}[v]<\mathrm{upper}$ を満たす頂点vの個数。",
    },
    ("tree_query/TreeWaveletMatrix.py", "TreeWaveletMatrix", "kth_subtree"): {
        "description": "constructorで指定したrootに対するvertex部分木で、k番目に小さい頂点値を返す。",
        "argumentDescriptions": {"vertex": "部分木の根。vertex自身を含む。", "k": "小さい方から数えた順位。0 <= k < 部分木頂点数。"},
        "returnFormat": "int",
        "returnDescription": "vertex部分木の頂点値を重複込みで昇順に並べたときのk番目の値。",
    },
    ("tree_query/TreeWaveletMatrix.py", "TreeWaveletMatrix", "count_subtree"): {
        "description": "constructorで指定したrootに対するvertex部分木で、指定値域に入る頂点数を数える。",
        "argumentDescriptions": {"vertex": "部分木の根。vertex自身を含む。", "lower": "含める値の下端。", "upper": "含めない値の上端。"},
        "returnFormat": "int",
        "returnDescription": r"vertex部分木で $\mathrm{lower}\le\mathrm{values}[v]<\mathrm{upper}$ を満たす頂点vの個数。",
    },
    ("tree_query/TreeWaveletMatrix.py", "TreeWaveletMatrix", "tolist"): {
        "description": "constructorへ渡した頂点値を頂点番号順のlistとして返す。",
        "returnFormat": "list[int]",
        "returnDescription": "長さVの列result。result[v]は頂点vへ設定した値。",
    },
    ("tree_query/TreeWaveletMatrix.py", "TreeWaveletMatrix", "__str__"): {
        "description": "constructorへ渡した頂点値を頂点番号順のlist形式で表示する。",
        "returnFormat": "str",
        "returnDescription": "頂点番号順のvaluesをPython listと同じ形式で表した文字列。",
    },
    ("tree_query/TreeWaveletMatrix.py", "TreeWaveletMatrix", "__repr__"): {
        "description": "型名とconstructorへ渡した頂点値をデバッグ用に表示する。",
        "returnFormat": "str",
        "returnDescription": "`TreeWaveletMatrix(values)`の形で、valuesを頂点番号順のlistとして含む文字列。",
    },
})

CLASS_DETAILS_BY_SYMBOL[("tree_query/TreeWaveletMatrix.py", "TreeWaveletMatrix")] = {
    "description": "静的な頂点値をHLD順にWavelet Matrixへ格納し、木のpath・部分木で順位と値域個数を検索する。",
    "constructorCreates": "treeの各頂点値を保持する。kth_path・count_pathで2頂点間pathを、kth_subtree・count_subtreeでrooted subtreeを検索できる。",
    "argumentDescriptions": {
        "tree": "連結な無向木の隣接list。要素は行き先、または先頭要素が行き先のtuple。",
        "values": "頂点番号順に1個ずつ並べた長さVの整数列。負数と重複を許す。",
        "root": "kth_subtreeとcount_subtreeで親子関係を決める根。path queryの結果には影響しない。",
    },
}

COMPLEXITY_BY_MODULE.update({
    "graph_connectivity/ComplementGraph.py": {
        "complement_bfs": "O(V+E) time、O(V) memory（Eは元graphの辺数）",
        "complement_components": "O(V+E) time、O(V) memory（無向辺を両方向に数えた元graphの辺数をEとする）",
    },
    "range_query/RangeXorBasis.py": {
        "range_xor_basis": "O((N+Q) B) time、O(N+Q+QB) memory（Bは値の最大bit長、出力を含む）",
        "range_max_xor": "O((N+Q) B) time、O(N+Q) memory（Bは値とinitialの最大bit長）",
    },
    "shortest_path/KShortestWalks.py": {
        "k_shortest_walks": "O((V+E) log V + E log E + K log K) time、O(V + E log E + K) memory",
    },
    "graph_matching/StableMatching.py": {
        "stable_matching": "O(P) time、O(P+N+M) memory（Pは両側の希望listの合計長）",
    },
    "tree_query/TreeWaveletMatrix.py": {
        "TreeWaveletMatrix": "O(V log S) time、O(V log S) memory（Sは異なる頂点値の個数）",
        "kth_path": "O(log V log S)", "count_path": "O(log V log S)",
        "kth_subtree": "O(log S)", "count_subtree": "O(log S)",
        "tolist": "O(V)", "__str__": "O(V)", "__repr__": "O(V)",
    },
})
