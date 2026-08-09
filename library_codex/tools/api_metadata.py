"""Human-authored semantics used by the source-derived API reference.

The implementation modules stay annotation-light for contest use.  Details
that cannot be recovered safely from the AST live here so the generated docs
and the website share one reviewable source of truth.
"""


# 正式名・source・説明からは拾いにくい通称だけを置く。
SEARCH_TERMS_BY_MODULE = {
    "segment_tree/LazySegTree.py": (
        "遅延セグ木",
        "lazy segtree",
        "区間更新",
        "遅延評価",
    ),
    "fenwick_tree/FenwickTree.py": (
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
    "fenwick_tree/FenwickTree.py": (
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
        "合同類の代表値、mod乗、完全平方根、整数n乗根、10進桁数を求められる。",
        "integer_nth_rootは浮動小数点数を使わず、floor(number^(1/degree))を返す。",
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
    "modular_power": "baseのexponent乗をmodulusで割った余りを返す。",
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
    "decimal_digit_count": "非負整数の10進桁数を返す。",
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
    ("combinatorics/Combination.py", "Comb", "fact"): {
        "description": r"階乗 $n!\bmod\mathrm{mod}$ を返す。",
        "returnFormat": "int",
        "returnDescription": r"$n!\bmod\mathrm{mod}$。",
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
    ("fenwick_tree/FenwickTree.py", "FenwickTree", "prefix_sum"): {
        "description": r"先頭からright未満までの和 $\sum_{i=0}^{\mathrm{right}-1}a_i$ を返す。",
        "returnDescription": r"$\sum_{i=0}^{\mathrm{right}-1}a_i$。",
    },
    ("fenwick_tree/FenwickTree.py", "FenwickTree", "sum"): {
        "description": (
            r"rightを指定したときは半開区間 $[\mathrm{left},\mathrm{right})$ の和を返す。"
            r"right=Noneなら $[0,\mathrm{left})$ の和を返す。"
        ),
        "returnDescription": (
            r"rightを指定したときは $\sum_{i=\mathrm{left}}^{\mathrm{right}-1}a_i$。"
            r"right=Noneなら $\sum_{i=0}^{\mathrm{left}-1}a_i$。"
        ),
    },
    ("fenwick_tree/FenwickTree.py", "FenwickTree", "get"): {
        "description": r"位置indexの値 $a_{\mathrm{index}}$ を返す。",
        "returnDescription": r"$a_{\mathrm{index}}$。",
    },
    ("fenwick_tree/FenwickTree.py", "FenwickTree", "lower_bound"): {
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
    "combinatorics/Combination.py": {
        "Comb": "構築 O(size)",
        "ensure": "追加したtable要素数に比例（全呼び出しを通して償却 O(max size)）",
        "fact": "償却 O(1)、table拡張分を除く",
        "C": "償却 O(1)、table拡張分を除く",
        "__call__": "償却 O(1)、table拡張分を除く",
        "P": "償却 O(1)、table拡張分を除く",
        "H": "償却 O(1)、table拡張分を除く",
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
        "nearest_congruent_at_least": "O(1) integer operations",
        "modular_power": "O(log exponent)",
        "exact_square_root": "O(log number) bit operations",
        "integer_nth_root": "O(log number) bit operations",
        "decimal_digit_count": "O(number of digits)",
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
