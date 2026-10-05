# グラフ7問題の公式検査と高速化

2026-10-05。PyPy 7.3.16 / Python 3.10.14、WSL Linux、Ryzen 7 3700X。公式問題revisionは `1814c4e5205517e368bb57a8d1127eb961cfeaae`。オンライン提出は行っていない。

## 公式全ケース

| 問題 | ケース数 | 結果 |
| --- | ---: | --- |
| assignment | 14 | 全件通過 |
| biconnected_components | 22 | 全件通過 |
| three_edge_connected_components | 20 | 全件通過 |
| incremental_scc | 23 | 全件通過 |
| general_weighted_matching | 24 | 全件通過 |
| counting_spanning_tree_directed | 22 | 全件通過 |
| counting_spanning_tree_undirected | 22 | 全件通過 |

計147ケース。累計130問題・2899ケース、未実装123問題。各問題の単独実行コードと公式判定は `verify/library_checker/solutions/` と `results/` に保存した。

7問題それぞれで、全件検査で遅かった3ケースを各5回、合計105回再測定した。[通常の反復ベンチマーク一覧](../../verify/library_checker/benchmarks/README.md)へ各回の時間・RSS・hashを保存した。標準の反復記録がある問題は累計54問題で、130問題すべてを反復したわけではない。

## 重み付き一般マッチング

変更前は5秒制限の公式24ケース中7ケースでTLE。変更後は全件通過し、最大2.568秒だった。

- 辺ごとのtupleを、辺番号・両端点・重みの整数配列へ置き換えた。
- 双対変数を巨大な固定値でなく入力の最大重みから初期化した。
- 探索待ちの頂点が途中で内側の頂点になった場合、その走査を省いた。
- 再帰は導入していない。重み合計の最大化、未使用頂点を-1とする返り値、多重辺の最大重み採用を維持した。

変更前・採用版・取得時点の上位PyPy提出 [89280](https://judge.yosupo.jp/submission/89280) を、同じ公式入力で各5回比較した。参照sourceは実行前に全体を確認した。

| ケース | 変更前 | 採用版 | 参照89280 |
| --- | ---: | ---: | ---: |
| complete_plane_01 | 13.789秒 | 2.585秒 | 1.841秒 |
| complete_01 | 10.388秒 | 1.904秒 | 1.147秒 |
| sparse_01 | 0.463秒 | 0.211秒 | 0.149秒 |

- 比較範囲では約2.20〜5.45倍高速化した。
- 3ケース中の最大RSSは変更前198420 KiB、採用版129552 KiB、参照99432 KiB。採用版は変更前より約34.7%少ない。
- 採用版は参照より約1.40〜1.66倍遅く、メモリも多い。最速と同等になったわけではない。
- 参照は平坦な行列、採用版は行ごとの整数listと辺番号の間接参照を使う。残る差の要因別の寄与は測定していない。

## 辺追加SCC

変更前は公式23ケース中、大きな閉路の2ケースが5秒制限でTLE。最終版は全件通過し、最大1.850秒だった。元のimportは単独実行コードへ展開できない形式だったため、変更前の測定コードではimportだけを修正している。

1. 縮約グラフ・成分内の頂点一覧まで作るSCC classをやめ、必要な成分番号だけを計算する。
2. 頂点番号の詰め直しを辞書から整数配列へ変える。
3. 隣接リストの再構築をやめ、CSRの辺配列・各頂点の区間・探索用配列を分割統治の全処理で再利用する。

1・2までの中間版も保存した。CSR配列再利用の方針は、全sourceを確認した上位PyPy提出 [276958](https://judge.yosupo.jp/submission/276958) を参考にした。分割統治とDFSはどちらも再帰を使わず、既存の併合イベント形式を保っている。

| ケース | 変更前 | 隣接リストの中間版 | 採用版 | 参照276958 |
| --- | ---: | ---: | ---: | ---: |
| large_cycle_00 | 14.175秒 | 3.982秒 | 1.821秒 | 0.764秒 |
| random_04 | 4.092秒 | 2.012秒 | 1.338秒 | 1.420秒 |
| max_random_00 | 2.343秒 | 0.912秒 | 0.575秒 | 1.518秒 |

- 変更前に対して約3.06〜7.78倍、中間版に対して約1.50〜2.19倍高速化した。
- 3ケース中の最大RSSは変更前1328156 KiB、中間版735360 KiB、採用版378736 KiB、参照136688 KiB。採用版は変更前より約71.5%、中間版より約48.5%少ない。
- 大きな閉路では採用版が参照の約2.38倍遅い。一方、2種類のランダム入力では参照より速かった。入力によって優劣が異なり、全ケースで最速とは言えない。
- 参照は各辺が同一成分になる時刻を返し、採用版は必要なUnion-Find併合だけを返す。問題の答えが一致することをcheckerで検査したが、内部APIや入出力処理は同一ではない。

## 測定条件と記録

PyPy quickテスト144件、対象実装・提出コードの関連36テスト、source・API・catalog同期、説明監査、再帰監査は通過した。全ライブラリのfull検査は今回再実行していない。

通常の性能検査は、未変更のCSR Dijkstraで初回1.046倍となり、基準1.050倍を下回った。[初回の6測定値](../benchmarks/results/graph-checkpoint-csr-warning.json)を保存した。実装・基準を変えずに性能検査全体を1回だけ再実行すると、Dijkstraは1.164倍で全項目が通過した。[再測定の全生データ](../benchmarks/results/graph-checkpoint-quick-performance.json)も保存した。短時間測定の揺れがあるため、再測定で通ったことを初回警告のなかった証拠とは扱わない。

比較は独立した新規PyPyプロセスを逐次起動し、順番を入れ替えて測定した。表は起動・JIT・入出力込みの中央値。すべての出力を公式checkerで検証した。別の最適解を返す場合は出力hashが違っても、公式checkerの判定を使う。

変更前が5秒を超えた時間も測るため、比較時のtimeoutは90秒。公式の合否は別途5秒制限で検査した記録を使う。参照ランキングは変化するので、比較JSON内のID・source hash・取得時のsnapshotを正本とする。

- [重み付きマッチングの変更前コード](../benchmarks/baselines/general_weighted_matching.py)
- [重み付きマッチングの変更前全件結果](../benchmarks/results/general-weighted-matching-before.json)
- [重み付きマッチングの比較生データ](../benchmarks/results/general-weighted-matching-comparison.json)
- [辺追加SCCの変更前コード](../benchmarks/baselines/incremental_scc.py)
- [辺追加SCCの変更前全件結果](../benchmarks/results/incremental-scc-before.json)
- [辺追加SCCの比較生データ](../benchmarks/results/incremental-scc-comparison.json)
- [辺追加SCCの隣接リスト中間版](../benchmarks/experiments/incremental_scc_adjacency.py)
- [中間版までの最初の比較](../benchmarks/results/incremental-scc-adjacency-comparison.json)

```sh
pypy3 library_codex/tools/check_library_checker.py test assignment biconnected_components three_edge_connected_components incremental_scc general_weighted_matching counting_spanning_tree_directed counting_spanning_tree_undirected --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/library_checker.py fetch --problem general_weighted_matching --language pypy3 --top 2 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/library_checker.py fetch --problem incremental_scc --language pypy3 --top 2 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/general_weighted_matching-pypy3.json --reviewed 89280 --problem /home/harurun/.cache/harurun-library-checker/problems/graph/general_weighted_matching --cases complete_plane_01 complete_01 sparse_01 --variant previous=library_codex/benchmarks/baselines/general_weighted_matching.py --variant library=verify/library_checker/solutions/general_weighted_matching.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/general-weighted-matching-comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/incremental_scc-pypy3.json --reviewed 276958 --problem /home/harurun/.cache/harurun-library-checker/problems/graph/incremental_scc --cases large_cycle_00 random_04 max_random_00 --variant previous=library_codex/benchmarks/baselines/incremental_scc.py --variant adjacency=library_codex/benchmarks/experiments/incremental_scc_adjacency.py --variant library=verify/library_checker/solutions/incremental_scc.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/incremental-scc-comparison.json
pypy3 library_codex/benchmarks/official_benchmark.py assignment biconnected_components three_edge_connected_components incremental_scc general_weighted_matching counting_spanning_tree_directed counting_spanning_tree_undirected --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```
