# 多項式の評価・補間・累積和の検証

2026-10-06。Library Checker公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`。
オンライン提出は行っていない。

## 追加した問題

| 問題 | 公式ケース | ライブラリ |
| --- | ---: | --- |
| prefix_sum_of_polynomial | 26 | PolynomialPrefixSum |
| multipoint_evaluation_on_geometric_sequence | 25 | GeometricMultipointEvaluation |
| polynomial_interpolation_on_geometric_sequence | 28 | GeometricMultipointEvaluation |
| shift_of_sampling_points_of_polynomial | 32 | MultipointEvaluation |

追加111ケースが最終版のstandalone解答で全件通過した。依存変更で古くなった `binomial_coefficient` の30ケースも再検査した。
全体は170 / 253問題、3980ケース通過。未実装83問題、古い公式検証結果0件。
通常形式の反復ベンチマークは96問題。過去に通過した残り74問題には、この形式の反復記録がまだない。

## 変更

- 等比数列上の補間を汎用の積木から専用のmiddle product・畳み込みへ変更した。計算量を `O(M(N) log N)` から `O(M(N))` にした。
- 等比数列上の評価は、必要な部分だけを計算するmiddle productを使う。初項0、公比0・1、出力1個を個別処理する。
- 多項式累積和は、多点評価と補間を経由せずBernoulli数の母関数を使う。計算量を `O(M(N) log N)` から `O(M(N))` にした。inclusiveの場合は元の多項式を加える。
- 標本点シフトは、逆元を要素ごとに求めず一括逆元を使う。通常の全畳み込みをmiddle productへ変更した。
- `sum_polynomial_exponential([1], 1, 2)` が1になる誤りを修正した。正しくは2。公比1では累積和の次数が一つ増えるため、先頭0を含むN+1個の標本から補間する。
- 4ページの記事・引数・返り値・計算量を更新した。変更対象のテストは `verify/polynomial/` へ分離した。
- 比較ツールは、外部提出が取得できない場合も `--variant` だけで比較できるようにした。外部コードの実行には引き続き明示的な `--reviewed` 指定とhash照合が必要。

M(N)は多項式積の時間。998244353では `O(N log N)`。
今回、指数付き総和のLibrary Checker 2問題は追加していない。次数1000万の標本生成・時間・メモリ検証が別途必要。

## 測定条件

- WSL Ubuntu、AMD Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。
- 新しいPyPyプロセスを各ケース5回起動。JIT・起動・入出力込みの実時間の中央値。
- 実装順を入れ替え、重い検査を同時実行しない。
- 全出力を公式checkerで検査。入力・ソース・checkerのhashと各回の時間・最大RSSをJSONへ保存。
- メモリ制限は強制していない。示すメモリは最大RSSで、オンラインACではない。

## アルゴリズム変更前後

ここでは出力方式を同じにした段階を比較した。変更前は `*_before.py`、変更後は `*_algorithm.py` に保存している。

| 問題・公式ケース | 変更前 | アルゴリズム変更後 |
| --- | ---: | ---: |
| 等比補間 max_random_00 | 18.372秒 | 0.970秒 |
| 等比補間 pow_rN_equal_1_00 | 9.674秒 | 0.817秒 |
| 多項式累積和 max_random_00 | 32.497秒 | 1.044秒 |
| 多項式累積和 max_random_01 | 32.446秒 | 1.000秒 |

等比補間は約11.8〜18.9倍、多項式累積和は約31.1〜32.4倍。最大ケースのRSSは等比補間で562620→180560 KiB、多項式累積和で623964→151396 KiB。

- [等比補間の生データ](../benchmarks/results/geometric_interpolation_algorithm_comparison.json)
- [多項式累積和の生データ](../benchmarks/results/prefix_sum_polynomial_algorithm_comparison.json)

最終driverでは係数列をまとめて出力する。アルゴリズム変更後との比較では改善は約1〜3%に留まり、主要な高速化はアルゴリズムの変更による。多項式累積和では一時的な出力文字列によりRSSが約6 MiB増える。

- [等比補間の最終版比較](../benchmarks/results/geometric_interpolation_official_comparison.json)
- [多項式累積和の最終版比較](../benchmarks/results/prefix_sum_polynomial_official_comparison.json)

## 上位PyPy提出との比較

2026-10-06に最新AC・判定時間昇順で取得した提出を、実行部分を確認してから同じ環境・入力で測定した。judge上の表示時間同士の比較ではない。

| 問題・公式ケース | 変更前 | 最終版 | 参照提出 |
| --- | ---: | ---: | ---: |
| 標本点シフト max_random_00 | 1.320秒 | 0.624秒 | 0.532秒 |
| 標本点シフト type2_random_00 | 1.125秒 | 0.535秒 | 0.468秒 |
| 等比評価 max_random_00 | 1.008秒 | 0.610秒 | 0.344秒 |
| 等比評価 near_pow_of_2_05 | 0.487秒 | 0.470秒 | 0.257秒 |
| 等比補間 max_random_00 | 別表 | 1.013秒 | 0.535秒 |
| 等比補間 pow_rN_equal_1_00 | 別表 | 0.854秒 | 0.484秒 |

参照は [標本点シフト389217](https://judge.yosupo.jp/submission/389217)、[等比評価401985](https://judge.yosupo.jp/submission/401985)、[等比補間401086](https://judge.yosupo.jp/submission/401086)。いずれもtyuyu62の提出。多項式累積和では該当するPyPy提出をAPIから取得できなかったため、外部最速比較済みとはしない。

標本点シフトは約2.1倍、等比評価は約1.04〜1.65倍速くなった。ただし参照との差はシフトで約14〜17%、等比評価・補間で約1.77〜1.89倍残る。全入力での最速性は示していない。参照は固定modの変換と専用の前後処理を使っているが、時間差の内訳は今回profileしていない。

シフトmax_random_00のRSSは変更前157572 KiB、最終版161456 KiB、参照211296 KiB。一括逆元による一時配列で変更前より約3.8 MiB増える。同じ問題のtype2_random_00では157304→146604 KiBへ減った。等比評価max_random_00は179200→165008 KiB、参照150400 KiB。

- [標本点シフトの生データ](../benchmarks/results/sampling_shift_official_comparison.json)
- [等比評価の生データ](../benchmarks/results/geometric_evaluation_official_comparison.json)

## 最終版の通常ベンチマーク

各問題の公式全件検証で遅かった3ケースを5回ずつ測定した。全ケースを反復したわけではない。

| 問題 | 3ケース中の最大中央値 | 最大RSS |
| --- | ---: | ---: |
| prefix_sum_of_polynomial | 1.034秒 | 157312 KiB |
| multipoint_evaluation_on_geometric_sequence | 0.572秒 | 165012 KiB |
| polynomial_interpolation_on_geometric_sequence | 0.953秒 | 181028 KiB |
| shift_of_sampling_points_of_polynomial | 0.647秒 | 161420 KiB |
| binomial_coefficient（依存更新） | 1.149秒 | 91188 KiB |

[問題別の測定記録](../../verify/library_checker/benchmarks/README.md)。

## 検査

- 変更関連の単純解照合・境界・回帰テスト: 34 passed。
- 公比0・1、空入力、1点、重複点、位数Nの根、公比0の2点補間、負の評価点、法をまたぐシフト、入力の非破壊性を検査。
- 公比1の有限和は大きいcountと法の周期を検査。一般の公比でもcountを1増やしたときの差分恒等式を検査。
- 通常検査: 168 passed。quick性能検査も通過。
- 提出コード・API・catalogの同期検査、説明監査、再帰監査が通過。説明の指摘0件、5838関数に直接・相互再帰なし。
- 4記事のPython使用例は、各1ブロックをそのまま実行して通過。
- 最終比較JSONのsource hashと現在の提出コードが一致。全170問題の公式結果も現在の提出コードと一致し、3980ケースに欠落・失敗なし。
- full検査は今回再実行していない。オンライン提出と公開サイトの再デプロイも行っていない。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test prefix_sum_of_polynomial multipoint_evaluation_on_geometric_sequence polynomial_interpolation_on_geometric_sequence shift_of_sampling_points_of_polynomial binomial_coefficient --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py prefix_sum_of_polynomial multipoint_evaluation_on_geometric_sequence polynomial_interpolation_on_geometric_sequence shift_of_sampling_points_of_polynomial binomial_coefficient --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/tools/prepare_checkpoint.py --profile quick
```

比較用sourceは `benchmarks/baselines/`、取得した参照sourceは `../lc-matching-reference/` に保存している。参照ID・取得時の順位条件・source hashは各比較JSONにも含まれる。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/polynomial_interpolation_on_geometric_sequence-pypy3.json --reviewed 401086 --problem /home/harurun/.cache/harurun-library-checker/problems/polynomial/polynomial_interpolation_on_geometric_sequence --cases max_random_00 pow_rN_equal_1_00 --variant algorithm=library_codex/benchmarks/baselines/polynomial_interpolation_on_geometric_sequence_algorithm.py --variant library=verify/library_checker/solutions/polynomial_interpolation_on_geometric_sequence.py --repeat 5 --output library_codex/benchmarks/results/geometric_interpolation_official_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/prefix_sum_of_polynomial-pypy3.json --problem /home/harurun/.cache/harurun-library-checker/problems/polynomial/prefix_sum_of_polynomial --cases max_random_00 max_random_01 --variant previous=library_codex/benchmarks/baselines/prefix_sum_of_polynomial_before.py --variant library=library_codex/benchmarks/baselines/prefix_sum_of_polynomial_algorithm.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/prefix_sum_polynomial_algorithm_comparison.json
```

[等比補間の公式C++解法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/polynomial/polynomial_interpolation_on_geometric_sequence/sol/correct.cpp)と[累積和の公式C++解法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/polynomial/prefix_sum_of_polynomial/sol/correct.cpp)を参照した。外部コードをそのままライブラリへ複製せず、既存の多項式演算を使い、境界条件とテストを追加した。
