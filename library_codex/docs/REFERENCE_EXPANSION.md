# 参照ライブラリとの機能比較

2026-11-16の調査。既存APIへ追加できる操作は既存moduleへまとめる。参照先の存在や説明だけでは、正しさやPyPyでの高速性を確認したことにはしない。

## 参照版

- [kemuniku/cplib](https://github.com/kemuniku/cplib/tree/f835598fec8e14039cf654a67f0244e0a654d035): `f835598fec8e14039cf654a67f0244e0a654d035`、Nim、CC0-1.0。
- [qandori/cp-library](https://github.com/qandori/cp-library/tree/ceec97a52d734d23f762b9c5e322b2b53df0cf9e): `ceec97a52d734d23f762b9c5e322b2b53df0cf9e`、C++、CC0-1.0。

全ソースの実装監査や、C++/Nim版との実行時間比較は未完了。以下は仕様を照合した機能単位の記録。

## 今回の対象

| 参照機能 | 対応先 | 方針 |
| --- | --- | --- |
| kemuniku `str/edit_distance_bitset.nim`、qand `string/edit_distance.hpp` | `string_sequence/EditDistance.py` | 既存の距離APIを多倍長整数のMyers法へ変更。hash不能な列は従来DPを保持。閾値付き距離も追加 |
| qand `data_structure/mo_with_updates.hpp` | `optimization/MoWithUpdates.py` | 更新前後の値をclassで保持し、利用者のcallbackを追加・削除・答え取得の3つに減らす |
| qand `graph/difference_constraints.hpp` | `shortest_path/DifferenceConstraints.py` | 解復元と差の上下限。負辺を扱い、解のpotentialでDijkstra用の非負辺へ変換 |
| qand `math/linear_diophantine.hpp` | `number_theory/LinearDiophantine.py` | 半開長方形内の解の個数とk番目。全解listを保持しない |
| 既存の対数微分復元の未採用メモ | `fps/SparseFormalPowerSeries.py` | B F'=A Fの係数比較を既存moduleへ追加 |
| qand `data_structure/interval_map.hpp` | `ordered_set/IntervalMap.py` | 半開区間への値の代入、削除、取得、同値結合。既存TreapSetを使い、削除済み領域を定期回収 |
| qand `math/fixed_size_subset_sum.hpp` | `optimization/FixedSizeSubsetSum.py` | 異なる値をk個選んだ和の集合。補集合・gcd圧縮・等差数列を利用。一般部分は多法NTTではなくbitset DP |
| qand `convolution/ordered_convolution.hpp` | `convolution/OrderedConvolution.py` | i<jの寄与のみ。既存NTT998による分割統治を再帰なしで実装 |
| qand `convolution/max_min_convolution.hpp` | `convolution/MaxMinConvolution.py` | 値順の有効化をPython整数bit集合へ置換。参照先方式のPython移植と同一入力で比較 |
| kemuniku `utils/implicit_dijkstra.nim` | `shortest_path/ImplicitDijkstra.py` | hash可能な状態、多始点、条件付き早期終了、経路復元。通常Dijkstraは変更しない |

## 続く調査候補

候補の段階では未実装・速度未確認。各行は既存APIとの操作単位の照合から始める。

| 参照先 | 比較する機能 | 既存との確認点 |
| --- | --- | --- |
| qand `data_structure/persistent_deque.hpp` | 永続deque・分割連結 | PersistentQueue/Arrayとは異なる操作。PyPyでnode objectを増やさない表現を比較 |
| qand `data_structure/priority_search_tree.hpp` | 三辺矩形内の列挙と点更新 | x座標を先に固定し、yの変更・有効化を行う。O(log N+K)列挙と既存KDTreeの定数倍を比較 |
| qand `tree/persistent_link_cut_tree.hpp` | 過去版から分岐する動的木 | 参照文書の償却O(log² N)は直前の返却版を引き継ぐ場合のみ。任意分岐には適用できず、1操作最悪O(N log N)。同じ古い版からの反復照会を測る |
| qand `data_structure/offline_range_kth_smallest.hpp` | 静的オフラインk番目 | 初期配列と(l,r,k)のquery列を受ける。更新付きという旧メモは誤り。静的WaveletMatrixとのメモリ・時間比較が必要 |
| kemuniku `collections/compressed_retroactive_priority_queue.nim` | 過去時刻への操作挿入 | 通常heapとの違い、完全/部分遡及の保証を確認 |
| kemuniku `fps/sparse_formal_power_series.nim` | 疎FPSの遠い1係数 | inv/logはBostan–Mori、exp/powは多項式係数漸化式の平方分割。最大次数dに対してd³の依存があり、非零項数だけで速くなるわけではない |

## 調査メモの訂正・非採用

- kemuniku `str/hamming_distance.nim`は同じ長さの2つのbyte列の距離をSIMDで求める実装。全位置とのHamming距離という旧メモは誤り。標準PythonだけではSIMD部分をそのまま移せず、単純ループのAPIを増やすだけにはしないため今回の追加対象から外した。
- 上の静的k番目も、名前だけで更新付きの候補へ分類していた点を訂正した。既存APIとの重複を確認する前に新規moduleは増やさない。

## 前からの残件

- Dirichlet畳み込み・逆元の古かった反復測定は、各3ケース×5回を再測定済み。現在の最大中央値は22.076秒・16.870秒で、10秒切りは残件。公式全ケースの再判定とは区別する。
- 大規模畳み込みdriverの整数入力を汎用化し、符号付き入力と通常read/splitとの比較を残す。
- 編集距離・疎FPS以外の旧module記事を順次整備する。自動生成APIがあることと具体的な記事があることは区別する。
- SPSの変換cache、Stirling固定k列、SegTreeTraversalの削除中心入力は性能比較を続ける。
- 旧 `REFERENCE_INVENTORY.md` の過去のpath・Geometry保留表示を現行sourceへ照合する。新しい参照版の完了判定には使わない。
- CodonとユーザーのWSL内コピーの同期は後回しという指定を維持する。

検証結果と速度・RSSは [編集距離・疎FPS](REFERENCE_EXPANSION_BENCHMARK.md)、[区間map・暗黙最短路・畳み込み](REFERENCE_ALGORITHMS_BENCHMARK.md) に記録する。新しい候補を見つけたことと、実装・検証・公開の完了を分けて管理する。
