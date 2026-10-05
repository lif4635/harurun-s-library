# 区間クエリの公式検査と高速化

2026-10-05。PyPy 7.3.16 / Python 3.10.14、WSL Linux、Ryzen 7 3700X。
公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。オンライン提出は行っていない。

## 公式全ケース

| 問題 | ケース数 | 結果 |
| --- | ---: | --- |
| static_range_lis_query | 15 | 全件通過 |
| range_linear_add_range_min | 28 | 全件通過 |
| range_add_range_min | 23 | 全件通過 |
| static_range_sum_with_upper_bound | 10 | 全件通過 |

76ケースを追加し、累計154問題・3516ケース。残り99問題。
変更のない問題は、source・公式問題・実行環境が一致する既存結果を引き継ぐ。
公式checkerと時間制限で判定した。メモリ制限は強制していないため、オンラインACの確認とは区別する。

## WeightedWaveletMatrix

`count_sum_lt(left, right, upper)`を追加した。
位置が半開区間内にあり、値がupper未満である要素の`(個数, 重み和)`を、一度の探索で返す。
重みを省略したときは値自身を合計する。問い合わせはO(log S)、Sは値の種類数。
公式問題は上限を含む整数条件なので、driverでは上限に1を加える。

当初は最大3ケースで5秒を超過した。ビット列を64ビットから32ビット単位に変更し、
符号付き64ビット整数を超えるビットマスクの多倍長整数化を避けた。
この変更は既存の値域和・順位和にも適用される。
重みそのものは任意精度の整数のままで、桁数の制限は追加しない。
負の重み、重複、文字列key、大きな整数、空区間、32/64ビット境界を含む単純解比較を追加した。

## RangeLinearAddRangeMin

各nodeの接線座標と遅延一次式を、tupleの組から整数配列へ変更した。
共通する一次式加算は凸包の形を変えないため、接線再計算で祖先の一次式を足す処理を省いた。
同じ祖先を左右の境界から二度再計算する処理も省いた。

再帰は使わず、更新直後に必要な接線を再計算する。
構築はO(N)、加算・最小値取得はそれぞれ最悪O(log² N)、領域はO(N)。
query時にまとめて再構築する方式には変更していない。

paddingを含む区間はquery対象にならないため、padding用の無限大は不要になった。
constructorは`RangeLinearAddRangeMin(values)`とし、旧`infinity`引数を削除した。
内部の`lazy`・`bridges`属性は係数・座標ごとの配列へ変更した。
既存の`add`・`query`の意味は変更していない。
`tolist`・`str`・`repr`は、状態を変えずに現在の列を取得・表示する。

小さい列の全区間と更新列、大きな整数、空・無効区間、2の累乗でない長さ、
デバッグ表示後のqueryを検査した。
接線計算だけを簡略化した中間版では、更新が多い公式ケースの約8秒はほとんど改善しなかった。
整数配列化した採用版で約4秒になった。

## Range Add Range Min のdriver

最初は加算・代入・和・最小値・最大値を持つ`RangeAddAssignRangeStats`を使用し、
最大5ケースで5秒を超過した。
必要な最小値と加算だけを指定した既存`LazySegTree`へ切り替えた。
さらに、公式制約で全値の絶対値が5.1×10^14未満に収まるため、
driverの単位元を浮動小数点の無限大から`1 << 60`へ変更した。
LazySegTree本体の仕様や扱える型は変更していない。

## 参照実装

2026-10-05にAPIから、各問題の最新問題版でACかつ実行時間順で先頭のPyPy提出を取得した。
実行前にsource全体を確認した。オンラインの記録時間とローカル測定値は直接比較しない。

- [236263](https://judge.yosupo.jp/submission/236263): 一次式加算。凸包の接線再構築を必要になるまで遅延する。参照のnode object・再帰をそのまま移植してはいない。
- [308952](https://judge.yosupo.jp/submission/308952): 区間加算・最小値。整数単位元の汎用lazy treeと専用入力処理。
- [313793](https://judge.yosupo.jp/submission/313793): 上限付き区間和。問い合わせを上限順に並べて2本のBITで処理するオフライン解法。採用版は問い合わせを事前に集めず、任意の順でその場で返せるため、同一APIの比較ではない。

## 同じ入力での比較

各caseを変更前・採用版・参照の3実装で5回ずつ測定し、実行順を毎回シャッフルした。
旧版のTLEケースも90秒の測定timeoutで最後まで実行し、公式checkerで正解を確認する。
このtimeoutは、公式全件検査の時間制限を緩めるものではない。
表の時間は中央値（秒）。

### 一次式加算・区間最小値

| case | 変更前 | 採用版 | 参照236263 |
| --- | ---: | ---: | ---: |
| max_random_00 | 4.339 | 2.348 | 3.291 |
| almost_t0_00 | 7.679 | 3.770 | 2.081 |
| almost_t1_00 | 1.125 | 0.822 | 1.737 |

旧版比で約1.4〜2.0倍高速化した。更新中心のcaseでは参照より約1.8倍遅く、
参照の遅延再構築に改善の余地がある。一方、採用版は更新後に接線を確定させるため、
その後の1回のqueryへ多数の更新分の再構築が集中しない。
上位実装をすべての入力で上回ったとはしていない。
生データは[比較JSON](../benchmarks/results/linear-add-official-comparison.json)に保存した。

最大RSSは採用版90,536〜92,660 KiB、旧版106,460〜121,128 KiB、
参照124,512〜131,608 KiB。同一caseでは旧版から約13〜24%減った。

### 区間加算・区間最小値

| case | 最初のdriver | 採用版 | 参照308952 |
| --- | ---: | ---: | ---: |
| max_random_00 | 6.13 | 1.68 | 1.01 |
| random_01 | 4.55 | 1.35 | 0.83 |
| max_lazy_00 | 0.54 | 0.39 | 0.42 |

ランダムな更新・問い合わせで約3.4〜3.7倍高速化した。
参照にはなお約1.6〜1.7倍の差がある。専用入力処理や作用の保持方法も異なるため、
差の全てをtreeの演算速度だけには帰さない。
生データは[比較JSON](../benchmarks/results/range-add-min-official-comparison.json)に保存した。

最大ランダムcaseのRSSは旧版252,080 KiB、採用版135,576 KiB、参照106,932 KiB。
使わない集約と遅延代入の状態を持たなくなったことで、旧driverから約46%減った。

### 上限付き区間個数・和

| case | 64ビット版 | 32ビット版 | 参照313793（オフライン） |
| --- | ---: | ---: | ---: |
| max_random_00 | 5.469 | 3.173 | 2.374 |
| random_01 | 4.463 | 2.600 | 1.896 |
| small_a_x_00 | 0.741 | 0.579 | 0.870 |

大きい2ケースで約1.7倍高速化した。採用版のRSSは、順に350,324 / 327,868 / 176,364 KiB。
旧版は349,428 / 329,256 / 179,852 KiBで、メモリ使用量はほぼ同じ。
参照は202,760 / 191,856 / 137,852 KiBと少ない。
参照はqueryをすべて先読みして並べ替えるため、オンラインquery用のWavelet Matrixと用途が異なる。
速度・メモリともに参照へ全面的に並んだとはしない。
生データは[比較JSON](../benchmarks/results/weighted-wavelet-official-comparison.json)に保存した。

## 公式ケースの反復測定

起動・JIT・入出力を含む5回の中央値。RSSは測定中の最大値、単位はKiB。

| 問題 | 最も遅いケースの中央値（秒） | 最大RSS |
| --- | ---: | ---: |
| static_range_lis_query | 3.512 | 132784 |
| range_linear_add_range_min | 3.962 | 90736 |
| range_add_range_min | 1.635 | 135688 |
| static_range_sum_with_upper_bound | 3.087 | 351280 |

全4問題とも、選択した3ケースを各5回測定した。
各回の時間・入力hash・source hashは[問題別JSON](../../verify/library_checker/benchmarks/README.md)に保存している。

## 検証範囲

- 変更関連・driver契約のPyPyテスト58件が通過した。
- `prepare_checkpoint.py --profile quick`の通常テスト166件とquick性能検査が通過した。
- standalone・API・catalog同期検査、説明監査が通過した。再帰監査は5289関数で直接・相互再帰なし。
- 今回full検査は再実行していない。直近のfull検査869件通過は、同日の行列7問題追加時の結果。
- 4問題の公式結果・反復ベンチマークのsource hashが、最終提出コードと一致することを確認した。
- 全体の反復ベンチマーク記録は78問題。公式全件通過の154問題とは別に数える。

## 再実行

repository rootで実行する。公式問題の生成器・checkerは既存キャッシュを再利用する。

```sh
pypy3 library_codex/tools/check_library_checker.py test static_range_lis_query range_linear_add_range_min range_add_range_min static_range_sum_with_upper_bound --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py static_range_lis_query range_linear_add_range_min range_add_range_min static_range_sum_with_upper_bound --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```

各問題の遅かった3ケースを5回ずつ、直列の新規PyPyプロセスで測る。
起動・JIT・入出力を含む時間と最大RSSを保存し、毎回公式checkerで出力を確認する。
全76ケースを5回測ったという意味ではない。

上位提出のsnapshotは次で取得する。ランキングが変わった場合も、今回使用した提出ID・取得時刻・source hashは比較JSON内のsnapshotに残る。
取得したsource全体を確認してから比較する。

```sh
pypy3 library_codex/benchmarks/library_checker.py fetch --problem range_linear_add_range_min --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/library_checker.py fetch --problem range_add_range_min --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/library_checker.py fetch --problem static_range_sum_with_upper_bound --language pypy3 --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/range_linear_add_range_min-pypy3.json --reviewed 236263 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/range_linear_add_range_min --cases max_random_00 almost_t0_00 almost_t1_00 --variant previous=library_codex/benchmarks/baselines/range_linear_add_range_min.py --variant library=verify/library_checker/solutions/range_linear_add_range_min.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/linear-add-official-comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/range_add_range_min-pypy3.json --reviewed 308952 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/range_add_range_min --cases max_random_00 random_01 max_lazy_00 --variant previous=library_codex/benchmarks/baselines/range_add_range_min.py --variant library=verify/library_checker/solutions/range_add_range_min.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/range-add-min-official-comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/static_range_sum_with_upper_bound-pypy3.json --reviewed 313793 --problem /home/harurun/.cache/harurun-library-checker/problems/data_structure/static_range_sum_with_upper_bound --cases max_random_00 random_01 small_a_x_00 --variant previous=library_codex/benchmarks/baselines/static_range_sum_with_upper_bound.py --variant library=verify/library_checker/solutions/static_range_sum_with_upper_bound.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/weighted-wavelet-official-comparison.json
```
