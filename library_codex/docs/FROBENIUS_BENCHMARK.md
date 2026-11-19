# Frobenius分解による行列累乗の比較

2026-11-20。PyPy 7.3.16 / Python 3.10.14、WSL2、Ryzen 7 3700X。新しい`linear_algebra/Frobenius.py`と既存の`Matrix.matrix_power`を比較した。通常の行列積・二分累乗は変更していない。

## 比較条件

- 法は998244353。各方式を新しいPyPy processで5回ずつ、順序を入れ替えて逐次実行した。CPU 2へ固定したが占有はしていない。
- 同じ行列・指数を渡し、入力と全結果のSHA-256が各回一致することを確認した。
- 下表は構築と全照会を含む中央値。import・入力生成・結果hashの作成は除く。起動込み時間もJSONへ保存した。RSSはprocess全体の最大値。
- Frobeniusの基底選択はseed=11で固定。乱数seedを変えたときの時間分布の比較ではない。
- 比較器も通常のimportで起動する。片方だけをexecした測定ではない。C++実装や現在のオンライン最速提出との比較ではない。

## 結果

| 入力 | 二分累乗 秒 | Frobenius 秒 | 最大RSS KiB: 二分 / Frobenius |
| --- | ---: | ---: | ---: |
| 密行列 N=16 | 0.027895 | 0.034277 | 75856 / 76076 |
| 密行列 N=64 | 0.113525 | 0.067638 | 78752 / 78136 |
| 密行列 N=128 | 0.662718 | 0.127439 | 96824 / 80140 |
| 密行列 N=256 | 4.700699 | 0.562758 | 102168 / 89072 |
| 密行列 N=128、K=3 | 0.034461 | 0.111479 | 77680 / 79560 |
| 順列行列 N=128 | 0.055667 | 0.143622 | 81976 / 79784 |
| 3倍の単位行列 N=128 | 0.059831 | 0.187605 | 82436 / 79976 |
| 同じJordanブロック32次×4 | 0.125702 | 0.157369 | 84404 / 79552 |
| 密行列 N=128、指数を変えて3照会 | 1.923458 | 0.190835 | 101964 / 81896 |

指数の指定がない行は10の18乗+37。3照会は10の18乗に37、77、137を足した指数で、Frobeniusだけ分解を再利用する。両者とも全結果を保持する。

密行列N=128で約5.2倍、N=256で約8.4倍速い。N=256の構築中央値は0.365211秒で、前計算を除外した比較ではない。一方、N=16、小さい指数、疎さを保つ行列では遅い。通常版を一律に置き換えたり、全入力で速いとは扱わない。

3照会で分解を再利用しても、1照会ごとに元の基底へ戻すO(N³)の行列積を行う。構築後の全行列の取得をO(N² log K)とはしない。

全測定値、構築・照会時間、環境、source・入力・結果のhashは[5回比較](../../verify/library_checker/benchmarks/comparisons/frobenius.json)へ保存した。[予備の3回比較](../../verify/library_checker/benchmarks/comparisons/frobenius-initial.json)も残している。両者は同じ実装の測定で、改善前後を表すものではない。

## 正しさと制約

- 小さいランダム行列を、2・3・5・101・998244353・1000000007・2の61乗-1の各素数で二分累乗と照合した。
- 空、1次、零・特異行列、Jordanブロック、同じ固有値、順列行列、負の成分、非常に大きい指数を含む。
- 分解の基底についてA P = P Cを独立に検査した。分解の失敗時に答えを返さず、試行上限で例外になることも検査した。
- 構築は1試行O(N³)、最大trials回。十分大きい素数では期待O(N³)だが、小さい素数での再試行や時間上限を保証しない。
- Library Checker `pow_of_matrix`は公式43ケースをローカル通過。公式checker・5秒の時間制限を使う。オンライン提出はしておらず、公式メモリ制限もローカルでは強制しない。

公式全ケースの判定は[結果](../../verify/library_checker/results/pow_of_matrix.json)、遅かった3ケース各5回の起動・JIT・入出力込み測定は[公式ベンチマーク](../../verify/library_checker/benchmarks/pow_of_matrix.json)へ保存した。`nontrivial_frobenius_form_01`・`02`・`03`の中央値はそれぞれ0.494273秒・0.470445秒・0.483609秒、全測定の最大RSSは72400 KiB。この公式測定はCPU固定をしておらず、上表の同条件比較とは別の記録。過去の別ケース・別環境の記録との比を高速化率には使わない。

## 再実行

```sh
/usr/bin/python3 library_codex/benchmarks/frobenius.py --python /path/to/pypy3 --repeat 5 --cpu 2
pypy3 -m pytest -q library_codex/verify/linear_algebra/test_frobenius.py
pypy3 library_codex/tools/check_library_checker.py test pow_of_matrix --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py pow_of_matrix --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
