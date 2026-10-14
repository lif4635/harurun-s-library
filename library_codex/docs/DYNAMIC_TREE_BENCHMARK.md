# 動的木・動的グラフの比較記録

2026-10-14。PyPy 7.3.16 / Python 3.10.14、WSL Linux、Ryzen 7 3700X。公式問題revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。

## 対象と検証範囲

| 問題 | 採用した実装 | 公式ケース数 |
| --- | --- | ---: |
| Dynamic Tree Vertex Add Path Sum | LinkCutTree | 15 |
| Dynamic Tree Vertex Set Path Composite | LinkCutTree、係数を整数に格納 | 23 |
| Dynamic Tree Vertex Add Subtree Sum | OfflineDynamicSum | 18 |
| Dynamic Tree Subtree Add Subtree Sum | OfflineDynamicSum | 18 |
| Dynamic Graph Vertex Add Component Sum | OfflineDynamicSum | 19 |

計93ケースをすべて公式checker・公式時間制限で通過した。オンライン提出はしていない。CPU・PyPyの違いや実行時の負荷があるため、オンラインACの保証ではない。

`OfflineDynamicSum`は、一般の無向グラフで辺の追加削除、1頂点への加算、連結成分全体への加算、成分和を処理する。木の部分木では、親との辺を一時的に外して成分操作へ変換した。全操作を先読みするため、直前の答えに依存するオンライン入力には使えない。

## 上位PyPyとの比較

取得時点で最新テストにACしたPyPy提出を実行時間順に取得し、先頭の提出を比較した。

- パス和: [400767](https://judge.yosupo.jp/submission/400767)。可換演算専用、パス上の位置検索・遅延更新なし。
- パス合成: [400769](https://judge.yosupo.jp/submission/400769)。非可換演算対応、パス上の位置検索・遅延更新なし。
- 頂点加算・部分木和: [401863](https://judge.yosupo.jp/submission/401863)。先読みの動的連結性。
- 部分木加算・部分木和: [401862](https://judge.yosupo.jp/submission/401862)。先読みの動的連結性。

各問題の`max_random_00`と`almost_line_00`を各5回、毎回新しいプロセスで測定した。いずれもN=Q=200,000。起動・JIT・入出力を含む壁時計時間の中央値を示す。実装の実行順を入れ替え、全出力を公式checkerで確認した。重い検査は並列実行していない。

| 問題 | ケース | 変更前 | 採用版 | 上位PyPy | 採用版の最大RSS | 上位の最大RSS |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| パス和 | max_random_00 | 4.657秒 | 3.715秒 | 2.687秒 | 104964 KiB | 174504 KiB |
| パス和 | almost_line_00 | 3.806秒 | 3.091秒 | 2.176秒 | 105120 KiB | 172664 KiB |
| パス合成 | max_random_00 | 13.806秒 | 3.574秒 | 3.496秒 | 104428 KiB | 223900 KiB |
| パス合成 | almost_line_00 | 11.000秒 | 3.467秒 | 3.266秒 | 104460 KiB | 224680 KiB |
| 頂点加算・部分木和 | max_random_00 | 6.534秒 | 0.993秒 | 0.839秒 | 205496 KiB | 174016 KiB |
| 頂点加算・部分木和 | almost_line_00 | 4.326秒 | 1.050秒 | 0.845秒 | 204464 KiB | 179248 KiB |
| 部分木加算・部分木和 | max_random_00 | 5.143秒 | 1.218秒 | 1.070秒 | 229016 KiB | 197456 KiB |
| 部分木加算・部分木和 | almost_line_00 | 5.919秒 | 1.332秒 | 1.233秒 | 236080 KiB | 197936 KiB |

パス和は約19〜20%短縮したが、可換演算専用の参照実装より遅い。パス合成は約3.2〜3.9倍速くなり、参照実装に近づいた。参照実装と異なり、採用版のLinkCutTreeは非可換演算・位置検索・遅延更新・不正なlinkの拒否を維持している。機能差だけを速度差の原因と断定したわけではない。

部分木2問題の改善は、オンラインのLink-Cut Treeから先読みのUnion-Findへ変更した効果を含む。Link-Cut Tree単体がこの倍率で高速化したわけではない。先読み版は全操作と辺の有効期間を保持するため、メモリとの交換になる。

## 採用した変更

- LinkCutTreeとSubtreeLinkCutTreeのsplayで、回転により下がった頂点だけを再集計する。新しい根の集計値は、回転前の木全体の値を再利用する。
- splayの内側で配列参照を保持し、回転ごとのmethod呼び出しを減らす。再帰や頂点ごとのobjectは追加しない。
- linkの閉路判定で、access後に同じ根を再探索する処理を省く。閉路になる辺は引き続きFalseを返して拒否する。
- パス合成のdriverでは、法998244353の2係数を30bitずつ整数に格納する。汎用LinkCutTreeの要素型は制限しない。
- OfflineDynamicSumでは辺の結合だけを巻き戻し、頂点加算を時刻順に保持する。成分加算は結合時の差分を用いて分裂先へ引き継ぐ。

SubtreeAddLinkCutTreeの回転・遅延伝搬を整理する試作は、ランダムな木で一貫した改善にならなかったため戻した。このオンラインclassは残し、先読みできる問題の解答にのみOfflineDynamicSumを使う。

## 記録と再実行

採用版の重い公式3ケースを各5回測った結果は次のとおり。

| 問題 | 最大中央値 | 最も遅かった1回 | 最大RSS | 公式制限 |
| --- | ---: | ---: | ---: | ---: |
| パス和 | 4.380秒 | 4.506秒 | 106956 KiB | 5秒 |
| パス合成 | 4.693秒 | 4.777秒 | 106756 KiB | 5秒 |
| 頂点加算・部分木和 | 1.207秒 | 1.284秒 | 207604 KiB | 5秒 |
| 部分木加算・部分木和 | 1.449秒 | 1.599秒 | 236080 KiB | 5秒 |
| 一般グラフの成分和 | 0.528秒 | 0.539秒 | 128936 KiB | 10秒 |

パス合成は通過したが5秒制限への余裕が小さい。他の環境でも十分な余裕があるとは扱わない。メモリ制限はローカルでは強制していない。

- 同条件比較: [パス和](../benchmarks/results/dynamic_tree_vertex_add_path_sum_comparison.json)、[パス合成](../benchmarks/results/dynamic_tree_vertex_set_path_composite_comparison.json)、[頂点加算・部分木和](../benchmarks/results/dynamic_tree_vertex_add_subtree_sum_comparison.json)、[部分木加算・部分木和](../benchmarks/results/dynamic_tree_subtree_add_subtree_sum_comparison.json)。各回の時間・RSS・入力とsourceのhash・取得時のランキングを含む。
- 変更前の提出コード: `benchmarks/baselines/dynamic_tree_*.py`。部分木の変更前はオンライン実装、採用版は先読み実装。
- 公式全件検証: [results](../../verify/library_checker/results/)。新規5問題それぞれのJSONを参照。
- 採用版の反復測定: [一覧](../../verify/library_checker/benchmarks/README.md)。公式全件検証で遅かった各3ケースを5回測定する。全93ケースを5回ずつ測ったわけではない。

```sh
pypy3 library_codex/tools/check_library_checker.py test dynamic_tree_vertex_add_path_sum dynamic_tree_vertex_set_path_composite dynamic_tree_vertex_add_subtree_sum dynamic_tree_subtree_add_subtree_sum dynamic_graph_vertex_add_component_sum --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py dynamic_tree_vertex_add_path_sum dynamic_tree_vertex_set_path_composite dynamic_tree_vertex_add_subtree_sum dynamic_tree_subtree_add_subtree_sum dynamic_graph_vertex_add_component_sum --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```

参照sourceを取得・確認した後、保存したsnapshotとIDを指定する。次はパス和の例。他の問題も上のID・問題名に置き換えて同条件で測れる。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot /home/harurun/.cache/harurun-library-checker/comparisons/dynamic_tree_vertex_add_path_sum/dynamic_tree_vertex_add_path_sum-pypy3.json --reviewed 400767 --problem /home/harurun/.cache/harurun-library-checker/problems/tree/dynamic_tree_vertex_add_path_sum --cases max_random_00 almost_line_00 --variant baseline=library_codex/benchmarks/baselines/dynamic_tree_vertex_add_path_sum.py --variant candidate=verify/library_checker/solutions/dynamic_tree_vertex_add_path_sum.py --repeat 5 --timeout 30 --output library_codex/benchmarks/results/dynamic_tree_vertex_add_path_sum_comparison.json
```
