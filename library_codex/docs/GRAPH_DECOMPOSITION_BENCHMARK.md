# 木分解・st-numbering・マンハッタンMST・最短walkの検証

2026-10-10 JST。公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`を固定。オンライン提出は行わない。

## 公式全件検証

| 問題 | ケース数 | module |
| --- | ---: | --- |
| tree_decomposition_width_2 | 24 | TreeDecompositionWidth2 |
| st_numbering | 28 | STNumbering |
| manhattanmst | 16 | MinimumSpanningTree |
| k_shortest_walk | 26 | KShortestWalks |

追加94ケース。累計188/253問題・4433ケース通過、未実装65問題。同じmoduleを使う既存の `minimum_spanning_tree` も31ケースを再検証した。ローカル検証は公式時間制限を使うが、オンラインとはCPU・PyPyが異なる。メモリ制限は強制していない。

## 実装と変更点

- 木幅2の木分解を追加した。次数2以下の頂点を消去し、必要な辺を補う。辺の削除は平坦な双方向リストと整数IDで処理する。頂点集合と親配列を返し、再帰や頂点ごとのsetは使わない。hash処理を期待定数時間として、期待 `O(N+M)` 時間・メモリ。
- st-numberingを追加した。反復DFSとlow値、配列による双方向リストで `O(N+M)`。普通の無向隣接listと無向CSRGraphを受け取る。返り値は頂点ごとの順位であり、一本のHamiltonian pathではない。
- マンハッタンMSTの候補生成をTreapSetから座標圧縮したBITへ変更した。候補辺もtupleではなく平坦な3配列で保持し、KruskalのUnion-Findをループ内で処理する。入力を変更せず、座標の整数幅を固定しない。
- k本の最短walkは、辺と永続leftist heapを整数ID・平坦な配列へ変更した。頂点内のヒープ構築には破壊的meldを使い、親から継承する段階だけコピーする。Dijkstraの確定順を再利用し、子リストを持たない。費用0の閉路、多重辺、巨大整数を扱う契約は維持する。

マンハッタンMSTは[初期検証](../benchmarks/results/manhattanmst_initial_verification.json)で16件中7件TLE。FastSetへの置換だけでは[3件TLE](../benchmarks/results/manhattanmst_fastset_verification.json)が残った。最終的なBIT方式は全16件通過した。失敗版も `benchmarks/baselines/manhattanmst_before.py` と `manhattanmst_fastset.py` に保存している。

k本の最短walkは[変更前](../benchmarks/results/k_shortest_walk_initial_verification.json)も全26件通過していた。比較用の提出コードは `benchmarks/baselines/k_shortest_walk_before.py`。

## 比較条件

- WSL Ubuntu、Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。
- 同じ公式入力・checker・PyPyで各5回。新規processの起動・JIT・入出力を含む時間の中央値と、測定中の最大RSSを記録する。実行順はseed固定で入れ替える。
- 重いテストと並行実行しない。Windowsの他アプリやCPU周波数は固定していない。
- 公式APIの「最新テストAC・PyPy・時間昇順」の先頭を取得し、全文を確認してから比較した。取得時点の順位であり、将来の順位や全言語の最速を意味しない。
- 比較元は[木分解222630](https://judge.yosupo.jp/submission/222630)、[マンハッタンMST400756](https://judge.yosupo.jp/submission/400756)、[最短walk389046](https://judge.yosupo.jp/submission/389046)。アルゴリズムとデータ配置を参考にし、ライブラリのAPI・整数範囲を維持した。
- st-numberingは[取得時点の条件に合うPyPy AC提出がなかった](../benchmarks/results/st_numbering_reference_availability.json)。[上位C++404721](https://judge.yosupo.jp/submission/404721)と[公式解法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/graph/st_numbering/sol/correct.cpp)を設計の参考にしたが、C++との実行時間比較はしていない。
- マンハッタンMSTの変更前は公式時間制限を超える。比較では打切りを90秒へ延ばして正答をcheckerで確認するが、公式制限内の通過とは扱わない。

## 同一入力での比較

時間は秒の中央値、RSSはKiB。各行5回。「旧版」がない欄は今回新設した機能。

| 問題・ケース | 旧版 秒 | 今回 秒 | 上位PyPy 秒 | 旧版 RSS | 今回 RSS | 上位PyPy RSS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 木分解 / max_cycle_00 | — | 2.6201 | 5.8266 | — | 381224 | 373276 |
| 木分解 / outer_planer_fix_00 | — | 2.4088 | 5.1446 | — | 232904 | 301680 |
| 木分解 / tree_00 | — | 2.3100 | 4.4026 | — | 319572 | 351256 |
| マンハッタンMST / max_random_00 | 7.2730 | 3.3091 | 3.6448 | 310408 | 238516 | 222748 |
| マンハッタンMST / many_cluster_00 | 6.4235 | 2.2021 | 2.4566 | 279096 | 239744 | 207940 |
| マンハッタンMST / enclosed_00 | 5.4079 | 2.2064 | 2.1244 | 275400 | 198040 | 186560 |
| 最短walk / dense_01 | 3.8846 | 1.4566 | 0.6693 | 307668 | 200244 | 155584 |
| 最短walk / random_01 | 3.1076 | 1.0194 | 0.6633 | 211024 | 142196 | 123480 |
| 最短walk / path_00 | 2.3922 | 0.5064 | 0.3675 | 241448 | 137060 | 119328 |

- 木分解は比較した3ケースで上位PyPy提出の約1.9〜2.2倍速い。ただし最大閉路のRSSは約2%多い。driverの入出力も含む提出全体の比較。
- マンハッタンMSTは旧版の約2.2〜2.9倍速く、RSSも減った。上位提出にはランダム・クラスタで少し速い一方、enclosedでは約4%遅く、RSSは3ケースとも多い。
- 最短walkは旧版の約2.7〜4.7倍速く、RSSは約33〜43%減った。ただし上位提出との約1.4〜2.2倍の時間差が残る。上位提出は整数をビットシフトして優先度キューへ詰める。今回の本体は従来の非負数入力と巨大整数を維持するtuple方式で、この差の寄与を単独で切り分けてはいない。
- st-numberingの重い3ケースの最大中央値は0.5453秒、最大RSSは113152 KiB。これは自実装だけの測定で、上位提出との比較ではない。

生データ: [木分解](../benchmarks/results/tree_decomposition_width_2_official_comparison.json)、[マンハッタンMST](../benchmarks/results/manhattanmst_official_comparison.json)、[最短walk](../benchmarks/results/k_shortest_walk_official_comparison.json)。各JSONに取得時のランキング条件・source hash・各回の時間・最大RSS・入力とcheckerのhashを保存した。

今回、既存MSTを含め5問題の標準反復測定を追加・更新した。反復測定を保存済みの問題は累計115問で、全188問を反復済みという意味ではない。

## 回帰検査

PyPyの全968テストが通過した。小入力の消去順・頂点順列の全探索、完全グラフMSTとの比較、優先度キューによるwalk列挙との比較を専用testへ残した。長いパス・閉路、多重辺、重み0、巨大整数も検査する。

記事4件の例は、通常のimportとstandalone codeの両方で実行する。問題別driverの最小入力も、ライブラリをimportできない一時directoryから実行する。API説明監査は指摘0件、6162関数の監査で直接・相互再帰は検出されなかった。

`prepare_checkpoint.py --profile full` の全検査が成功した。CSR・区間データ構造・FPS998・多項式GCD・SortableSegTreeなど、既存のfull性能検査も閾値を変更せず通過した。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test tree_decomposition_width_2 st_numbering manhattanmst k_shortest_walk minimum_spanning_tree --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py tree_decomposition_width_2 st_numbering manhattanmst k_shortest_walk minimum_spanning_tree --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```

通常の反復測定は、全件検証で遅かった3ケースずつ。全公式ケースを5回測ったものではない。[問題別一覧](../../verify/library_checker/benchmarks/README.md)に各回の時間・RSS・sourceと入力のhashを保存する。

上位提出を再取得するには、各問題について `library_codex/benchmarks/library_checker.py fetch --problem NAME --top 1 --cache ../lc-matching-reference` を実行する。実行前に取得したsourceを確認する。下のIDは今回確認したもの。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/tree_decomposition_width_2-pypy3.json --reviewed 222630 --problem /home/harurun/.cache/harurun-library-checker/problems/graph/tree_decomposition_width_2 --cases max_cycle_00 outer_planer_fix_00 tree_00 --variant library=verify/library_checker/solutions/tree_decomposition_width_2.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/tree_decomposition_width_2_official_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/manhattanmst-pypy3.json --reviewed 400756 --problem /home/harurun/.cache/harurun-library-checker/problems/geo/manhattanmst --cases max_random_00 many_cluster_00 enclosed_00 --variant library=verify/library_checker/solutions/manhattanmst.py --variant previous=library_codex/benchmarks/baselines/manhattanmst_before.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/manhattanmst_official_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/k_shortest_walk-pypy3.json --reviewed 389046 --problem /home/harurun/.cache/harurun-library-checker/problems/graph/k_shortest_walk --cases dense_01 random_01 path_00 --variant library=verify/library_checker/solutions/k_shortest_walk.py --variant previous=library_codex/benchmarks/baselines/k_shortest_walk_before.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/k_shortest_walk_official_comparison.json
```
