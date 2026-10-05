# 行列7問題の公式検査と高速化

2026-10-05。PyPy 7.3.16 / Python 3.10.14、WSL Linux、Ryzen 7 3700X。公式問題revisionは `1814c4e5205517e368bb57a8d1127eb961cfeaae`。オンライン提出は行っていない。

## 公式全ケース

| 問題 | ケース数 | 結果 |
| --- | ---: | --- |
| characteristic_polynomial | 28 | 全件通過 |
| matrix_det_arbitrary_mod | 20 | 全件通過 |
| hafnian_of_matrix | 11 | 全件通過 |
| pfaffian_of_matrix | 27 | 全件通過 |
| matrix_product | 22 | 全件通過 |
| pow_of_matrix | 43 | 全件通過 |
| sparse_matrix_det | 24 | 全件通過 |

計175ケースを追加し、累計143問題・3248ケース、未実装110問題。7問題とも既存APIを使うdriverを追加し、行列積と累乗の内部処理を改善した。

共通のMatrixモジュールが変わったため、既存の有向・無向全域木の数え上げ、逆行列、行列式、階数、連立方程式の6問題も全ケースを再検査した。変更のない問題はsource・公式問題・実行環境が一致する以前の全件通過を再利用した。

pfaffianのdriverは初回に入力のNを行列の次元と取り違えたため失敗した。公式形式の2N行2N列に修正した後で全27ケースを再検査した。アルゴリズム本体の修正ではない。

公式の時間制限とcheckerを使うが、メモリ制限はローカルでは強制していない。オンラインACと同じ意味ではない。

上位実装との同条件比較は行列積・行列累乗の2問題。任意modの行列式・疎行列の行列式のPyPy上位source、hafnianのC++上位sourceの該当関数も調べたが、今回は実装の置換や同条件比較は行っていない。残りの問題や全言語で最速という主張はしない。

各問題で遅かった公式3ケースを各5回再測定した。新規7問題で105回、依存先の既存6問題で90回。標準ベンチマークは累計67問題になった。143問題の全ケースを反復測定したわけではない。

| 問題 | 3ケース中の最大中央値 | 測定中の最大RSS |
| --- | ---: | ---: |
| characteristic_polynomial | 0.970秒 | 67328 KiB |
| matrix_det_arbitrary_mod | 0.646秒 | 66264 KiB |
| hafnian_of_matrix | 3.946秒 | 93204 KiB |
| pfaffian_of_matrix | 0.424秒 | 68080 KiB |
| matrix_product | 2.131秒 | 241800 KiB |
| pow_of_matrix | 2.075秒 | 93172 KiB |
| sparse_matrix_det | 2.523秒 | 95364 KiB |

全件の判定は `verify/library_checker/results/`、反復測定の各回の時間・RSS・CPU/OS/PyPy・入力とsourceのhashは[標準ベンチマーク](../../verify/library_checker/benchmarks/README.md)に保存した。

## 行列累乗

`matrix_power`の二分累乗法は変えず、内部の`matrix_multiply`を高速化した。変更前は内積をすべて足した後で剰余を取るため、998244353を法とする入力でも途中で64bitを超え、PyPyの多倍長整数演算が増えていた。

- 正の法が2の30乗以下なら入力を正規化し、非零項8個ごとに剰余を取る。
- 8個分の積と前回の余りの和は符号付き64bit整数の上限未満になる。
- 零項を飛ばす処理を残す。添字8個ごとに処理する試作では疎な入力が遅くなったため、非零項の個数で区切った。
- それより大きい法などは従来の一般の整数演算を使う。APIや計算結果を変えない。
- 時間計算量は引き続き行列積O(H D W)、N次正方行列の累乗O(N³ log(K+1))。

取得時点の最速PyPy提出 [389248](https://judge.yosupo.jp/submission/389248) を、変更前・採用版と同じ公式3ケースで各5回比較した。参照sourceは行列積提出389247との差分を含め全体を確認してから実行した。新規プロセスの起動・JIT・入出力を含む中央値で、実行順を入れ替え、各出力を公式checkerで検査した。

| ケース | 変更前 | 採用版 | 参照389248 | 採用版最大RSS | 参照最大RSS |
| --- | ---: | ---: | ---: | ---: | ---: |
| max_random_worst_00 | 16.383秒 | 2.108秒 | 1.996秒 | 93168 KiB | 90472 KiB |
| max_random_00 | 14.018秒 | 1.624秒 | 1.554秒 | 93132 KiB | 90344 KiB |
| perm_max_random_00 | 0.100秒 | 0.144秒 | 1.172秒 | 86400 KiB | 90068 KiB |

- 密な2ケースは約7.77〜8.63倍高速化した。上位提出よりは約4.5〜5.6%遅い。
- 順列行列のケースは変更前より約44ms遅い。入力の正規化と分岐が増えるためで、全入力での高速化ではない。参照提出よりは速い。
- 公式時間制限5秒とは別に、比較では変更前にも90秒のtimeoutを与えた。変更前の遅いケースを除外していない。
- [全測定値・snapshot・sourceと入力のhash](../benchmarks/results/matrix-power-comparison.json)と[変更前の公式検査](../benchmarks/results/pow_of_matrix-before.json)を保存した。

## 行列積

`strassen_matrix_multiply`でも8項ごとの剰余を使う。分割の打ち切りサイズ32、64、128、256、512、1024を、公式2ケースで各3回比較した。

| 打ち切りサイズ | max_random_00 | random_00 |
| --- | ---: | ---: |
| 32 | 3.122秒 | 2.845秒 |
| 64 | 2.590秒 | 2.168秒 |
| 128 | 2.287秒 | 1.894秒 |
| 256 | 2.182秒 | 1.823秒 |
| 512 | 2.222秒 | 1.724秒 |
| 1024 | 2.633秒 | 1.555秒 |

これは長方形の余白を省く変更前の中間実装の記録で、[各回の値](../benchmarks/results/strassen-thresholds.json)にsource hashも保存している。

大きな正方行列では256付近が速い一方、長方形では大きな正方形に埋める無駄が大きかった。そのため、既定値を256へ変更し、通常の長方形積の乗算回数がStrassenの末端での乗算回数以下なら、正方形へ拡張せず通常の積を使う。S次正方行列を1回分割すると末端の乗算回数が7/8になることから比較する。入力ごとの計測や固定の公式ケース名では分岐しない。

小さい法・負の入力・64bitを超える入力・大きな法・整数上の積・空行列・横長と縦長の行列・8項境界を単純解で検査する。入力を変更しないことも確認する。打ち切りサイズ0以下は無限に分割しないようValueErrorにする。

法の定数だけを得るためのFPSへの依存も除去した。Strassenのstandalone codeへFPS・NTTが混入しないことをテストする。

最終版を変更前および取得時点の最速PyPy提出 [389247](https://judge.yosupo.jp/submission/389247) と公式3ケースで各5回比較した。参照sourceは全体を確認してから実行した。条件は累乗と同じで、[各回の値とhash](../benchmarks/results/matrix-product-comparison.json)を保存した。

| ケース | 変更前 | 採用版 | 参照389247 | 採用版最大RSS | 参照最大RSS |
| --- | ---: | ---: | ---: | ---: | ---: |
| max_random_00 | 3.600秒 | 2.046秒 | 2.509秒 | 231700 KiB | 148016 KiB |
| random_00 | 3.325秒 | 1.020秒 | 1.017秒 | 96308 KiB | 110460 KiB |
| small_00 | 0.100秒 | 0.063秒 | 0.065秒 | 61548 KiB | 61832 KiB |

- 測定した3ケースでは変更前より約1.60〜3.26倍速かった。
- 最大正方行列では参照より約18%速いが、最大RSSは約57%多い。Strassenの中間行列を持つためで、メモリまで優位とはいえない。
- 長方形のケースでは参照とほぼ同じ時間。変更前の最大RSS204760 KiBから96308 KiBへ約53%減った。
- 打ち切り選定の3回測定と最終比較の5回測定は別の実験。測定値を混ぜて中央値を求めていない。

## 回帰検査

PyPyで全テスト869件が通過した。行列の単純解比較・境界値検査に加え、7問題の小さい入出力を通常の公式検査runnerのテストへ追加した。pfaffianの2N行2N列という入力形式も固定の回帰ケースで検査する。

行列とStrassenのテストを `verify/linear_algebra/` へ移し、Matrixのテストに混在していたBlackBoxLinearAlgebraの検査を専用ファイルへ分離した。既存の検査内容は削除していない。

API・catalog・提出コードの同期、説明監査、5186関数の再帰監査、fullプロファイルの性能回帰検査も通過した。READMEの検証件数の表記をcatalogが読む形式へ揃え、`stats.tests`に今回の869件を反映した。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test characteristic_polynomial matrix_det_arbitrary_mod hafnian_of_matrix pfaffian_of_matrix matrix_product pow_of_matrix sparse_matrix_det --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py characteristic_polynomial matrix_det_arbitrary_mod hafnian_of_matrix pfaffian_of_matrix matrix_product pow_of_matrix sparse_matrix_det --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/library_checker.py fetch --problem pow_of_matrix --language pypy3 --top 2 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/library_checker.py fetch --problem matrix_product --language pypy3 --top 2 --cache ../lc-matching-reference
```

参照sourceを確認した後、IDを指定して比較する。ランキング更新で同じIDが取得できない場合は、保存したsnapshotとsource hashで対象を確認する。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/pow_of_matrix-pypy3.json --reviewed 389248 --problem /home/harurun/.cache/harurun-library-checker/problems/linear_algebra/pow_of_matrix --cases max_random_worst_00 max_random_00 perm_max_random_00 --variant previous=library_codex/benchmarks/baselines/pow_of_matrix.py --variant library=verify/library_checker/solutions/pow_of_matrix.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/matrix-power-comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/matrix_product-pypy3.json --reviewed 389247 --problem /home/harurun/.cache/harurun-library-checker/problems/linear_algebra/matrix_product --cases max_random_00 random_00 small_00 --variant previous=library_codex/benchmarks/baselines/matrix_product.py --variant library=verify/library_checker/solutions/matrix_product.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/matrix-product-comparison.json
```

`benchmarks/experiments/strassen_thresholds.py`は、現在の実装で打ち切りサイズを再比較するために残している。中間実装の測定値とはsourceが異なる。
