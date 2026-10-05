# 木・区間・群の差の公式検査

2026-10-05。PyPy 7.3.16 / Python 3.10.14、WSL Linux、Ryzen 7 3700X。公式revisionは `1814c4e5205517e368bb57a8d1127eb961cfeaae`。オンライン提出はしていない。

## 公式全ケース

| 問題 | ケース数 | 結果 |
| --- | ---: | --- |
| common_interval_decomposition_tree | 30 | 全件通過 |
| vertex_add_range_contour_sum_on_tree | 36 | 全件通過 |
| vertex_get_range_contour_add_on_tree | 46 | 全件通過 |
| unionfind_with_potential | 18 | 全件通過 |
| unionfind_with_potential_non_commutative_group | 18 | 全件通過 |
| range_chmin_chmax_add_range_sum | 33 | 全件通過 |
| static_range_mode_query | 11 | 全件通過 |

計192ケースを追加し、累計150問題・3440ケース。残り103問題。変更のない問題はsource・公式問題・実行環境が一致する既存の検証結果を引き継ぐ。公式の時間制限とcheckerで判定するが、メモリ制限は強制していないため、オンラインACを保証するものではない。

順列木とSegment Tree Beatsは既存APIのdriverを追加した。順列木の内部の半開区間を公式出力の閉区間に直し、親が子より前になる順序で出力する。小さい入出力も通常検査の回帰ケースへ追加した。

## 追加したAPI

### PotentialUnionFind

群の差を指定する制約を追加する。演算・逆元・単位元を受け取り、非可換な群も扱う。`merge(a,b,d)`の意味は次のとおり。

$$
x_b=x_a\cdot d.
$$

矛盾する制約は拒否する。`diff(a,b)`は次の差を返し、未接続ならNoneを返す。

$$
x_a^{-1}\cdot x_b.
$$

整数専用の既存WeightedUnionFindは変更せず、その通常操作にcallbackの負担を加えない。非可換な順列群によるランダム検査では、受理した制約のグラフをBFSでたどる単純解と比較する。公式の非可換版では行列式1の2行2列行列を使う。

### CentroidDistanceAdd

距離が半開区間に入る頂点へ加算し、頂点値を取得する。点更新・距離範囲和のCentroidDistanceFenwickとは別クラス・別モジュールとした。構築O(N log N)、更新・取得O(log² N)。単純な全頂点走査による更新と比較し、負の更新・空範囲・上限なし・1頂点・大きな整数を検査する。

## 距離範囲和の高速化

旧CentroidDistanceFenwickは公式36ケースのうち二分木2ケース・鎖2ケースで10秒の時間制限を超えた。

- 重みなし木では距離が連続した整数なので、座標圧縮と、重心ごとの距離の二分探索を除去した。
- 枝を辞書のtupleキーではなく、重心分解木の子の整数IDで管理する。
- 初期値を距離ごとに集計し、各Fenwick木を線形に構築する。初期化をO(N log² N)からO(N log N)へ変更した。
- 各部分木のFenwick配列を直接操作し、区間和では共通するprefix部分の計算を省く。
- 公開methodの引数と返り値は変更しない。内部のcoordinates・branch_coordinatesは廃止し、branch_bitsは子の整数IDで引く配列へ変更した。

最終確認で、旧版が受け付けていた小数境界が高速化版では整数添字として使われる問題を検出した。非整数の境界だけを入口で距離の整数境界に変換し、float・Fraction・Decimal・正負の無限大を追加検査した。整数境界では変換を行わない。修正後、距離操作2問題の公式82ケースと、該当する比較・反復測定をやり直した。

上位PyPy提出[388478](https://judge.yosupo.jp/submission/388478)のsource全体を確認した。参照は重心ごとの距離情報を平坦化した実装。採用版では既存CentroidDecompositionが公開する祖先情報を保持しており、この部分には追加の軽量化余地が残る。

## 区間最頻値の高速化

旧StaticRangeModeは公式11ケースのうち2ケースで5秒の時間制限を超えた。

- 値を整数IDへ変換し、前処理中の出現回数を辞書ではなく整数配列で管理する。
- 完全ブロックの最頻回数・先頭位置と、各位置の出現順位を前計算する。
- 両端の候補が現在の最頻回数を超えるかを、出現位置の配列から直接判定する。
- 候補ごとの二分探索をなくし、問い合わせをO(B log N)からO(B)へ変更した。Bの既定値は約sqrt(N)。
- 同数の場合は区間内で最初に現れる値を返す仕様を維持した。2値の全列・全区間と複数のブロック幅を全探索し、ランダム列・文字列・None・tupleも検査した。

参照した最速PyPy提出[348574](https://judge.yosupo.jp/submission/348574)は全queryを先に受け取って並べ替えるオフライン方式。参照と同じ方式へそのまま置き換えると、前の答えから次の区間を決める既存APIの使い方ができなくなるため、採用版はオンライン問い合わせを維持した。参照は最頻値が同数の場合の先頭出現も保証しない。比較は問題の出力条件を満たすか公式checkerで確認するが、APIの条件まで同一ではない。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test common_interval_decomposition_tree vertex_add_range_contour_sum_on_tree vertex_get_range_contour_add_on_tree unionfind_with_potential unionfind_with_potential_non_commutative_group range_chmin_chmax_add_range_sum static_range_mode_query --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py common_interval_decomposition_tree vertex_add_range_contour_sum_on_tree vertex_get_range_contour_add_on_tree unionfind_with_potential unionfind_with_potential_non_commutative_group range_chmin_chmax_add_range_sum static_range_mode_query --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```

変更前の提出コードは `benchmarks/baselines/`、公式全件の判定は `verify/library_checker/results/`、反復計測は `verify/library_checker/benchmarks/` に保存する。

## 同条件の比較

公式3ケースについて各実装を5回ずつ、新規PyPyプロセスで実行した。順番は入れ替え、起動・JIT・入出力を含む壁時計時間の中央値を使う。すべての出力を公式checkerで検査した。時間超過した旧版も除外せず、比較のtimeoutだけ90秒に広げた。

### 距離範囲和

| ケース | 旧版 | 採用版 | 参照388478 | 旧版最大RSS | 採用版最大RSS | 参照最大RSS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| random_max_2_00 | 6.773秒 | 2.777秒 | 1.053秒 | 338724 KiB | 218112 KiB | 105508 KiB |
| binary_2_00 | 10.206秒 | 4.134秒 | 1.409秒 | 412256 KiB | 259356 KiB | 103540 KiB |
| line_2_00 | 14.956秒 | 4.764秒 | 1.804秒 | 448116 KiB | 289676 KiB | 129088 KiB |

旧版から約2.4〜3.1倍速くなり、最大RSSは約35〜37%減った。一方で参照より約2.6〜2.9倍遅く、メモリも約2.1〜2.5倍必要。参照との格差を解消したとはいえない。重心分解自体の辞書・祖先tupleの平坦化が残る改善候補。

[全測定値とsource・入力のhash](../benchmarks/results/contour-official-comparison.json)。

### 区間最頻値

| ケース | 旧版 | 採用版 | 参照348574（オフライン） | 旧版最大RSS | 採用版最大RSS | 参照最大RSS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| random_02 | 3.588秒 | 0.582秒 | 0.220秒 | 99500 KiB | 93392 KiB | 91000 KiB |
| random_04 | 5.137秒 | 0.818秒 | 0.325秒 | 98132 KiB | 91480 KiB | 93028 KiB |
| random_05 | 10.615秒 | 1.510秒 | 0.369秒 | 109116 KiB | 116388 KiB | 116116 KiB |

旧版から約6.2〜7.0倍速くなった。ただしrandom_05では追加の出現順位・最頻回数表のため最大RSSが約6.7%増えた。参照よりは約2.5〜4.1倍遅い。オンライン問い合わせと先頭出現を返す仕様を維持した実装であり、同一API条件の比較ではない。

[全測定値とsource・入力のhash](../benchmarks/results/range-mode-official-comparison.json)。

### 比較の再実行

取得した参照sourceの全体を確認してから実行する。記録したIDがランキングから外れた場合は、結果JSON内のsnapshot・URL・hashで対象を確認する。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem vertex_add_range_contour_sum_on_tree --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/library_checker.py fetch --problem static_range_mode_query --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/vertex_add_range_contour_sum_on_tree-pypy3.json --reviewed 388478 --problem /home/harurun/.cache/harurun-library-checker/problems/tree/vertex_add_range_contour_sum_on_tree --cases random_max_2_00 binary_2_00 line_2_00 --variant previous=library_codex/benchmarks/baselines/vertex_add_range_contour_sum_on_tree.py --variant library=verify/library_checker/solutions/vertex_add_range_contour_sum_on_tree.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/contour-official-comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/static_range_mode_query-pypy3.json --reviewed 348574 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/static_range_mode_query --cases random_02 random_04 random_05 --variant previous=library_codex/benchmarks/baselines/static_range_mode_query.py --variant library=verify/library_checker/solutions/static_range_mode_query.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/range-mode-official-comparison.json
```

## 標準ベンチマーク

7問題それぞれについて、公式全件検証で遅かった3ケースを5回ずつ測定した。計105回。比較実験とは別の測定で、中央値を混ぜていない。標準ベンチマークは累計74問題であり、全150問題を反復測定したわけではない。

| 問題 | 3ケース中の最大中央値 | 測定中の最大RSS |
| --- | ---: | ---: |
| common_interval_decomposition_tree | 1.617秒 | 324000 KiB |
| vertex_add_range_contour_sum_on_tree | 4.597秒 | 289740 KiB |
| vertex_get_range_contour_add_on_tree | 3.935秒 | 287640 KiB |
| unionfind_with_potential | 0.288秒 | 83084 KiB |
| unionfind_with_potential_non_commutative_group | 0.535秒 | 97972 KiB |
| range_chmin_chmax_add_range_sum | 9.523秒 | 165544 KiB |
| static_range_mode_query | 1.286秒 | 116420 KiB |

Segment Tree Beatsは制限10秒に対する余裕が小さい。今回アルゴリズム本体は変更しておらず、上位実装との比較・定数倍削減を次の改善候補として残す。距離範囲和の祖先情報の平坦化、区間最頻値のオフライン一括APIも未採用。今回扱った7問題を、いずれも最速実装と同等にしたという意味ではない。

次の調査用に上位PyPy提出[376851](https://judge.yosupo.jp/submission/376851)のsource全体を確認したが、まだ手元で実行比較していない。参照は整数の固定番兵を使い、現在の実装は第2最大・最小の配列へfloatの無限大を混在させている。PyPyで整数配列として保持できる形にするのが候補だが、固定番兵をそのまま採用して扱える整数の範囲を狭める変更は行わない。これは未検証の改善仮説で、今回の計測結果には含めない。

## 回帰検査と同期

変更関連の28テストと通常保守の161テストがPyPyで通過した。通常プロファイルの性能回帰検査も通過。最後の距離境界の修正後は、変更関連28件と公式82ケース・該当ベンチマークを再検査した。重心分解と区間最頻値の検査を、追加時期でまとまっていたファイルから対応モジュールごとのファイルへ移した。

提出コード・API・catalogの同期、説明監査、5242関数の再帰監査を確認した。catalogは367モジュール・505関数・226クラス・1424メソッド。新規2モジュールと更新した区間最頻値の記事には、使い方・返り値・境界条件を記載している。

今回は局所変更のためfullプロファイルは再実行していない。READMEのfull検証869件は、同日の行列追加時の結果として残した。
