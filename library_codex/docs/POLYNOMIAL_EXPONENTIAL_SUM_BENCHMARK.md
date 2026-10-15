# 等比重み付き多項式和の速度とメモリ

2026-10-15、WSLのPyPy 3.10 / 7.3.16、Ryzen 7 3700Xで測定。各入力を変更前後それぞれ5回、順序を入れ替えて実行した。時間は起動・JIT・入出力・冪表生成を含む中央値、メモリは5回の最大RSS。各回の出力を公式checkerで確認した。

| 公式問題とケース | 変更前 秒 | 変更後 秒 | 変更前 MiB | 変更後 MiB |
| --- | ---: | ---: | ---: | ---: |
| 有限和 `sum_of_exponential_times_polynomial/2_06` | 4.518 | 1.683 | 746.4 | 364.9 |
| 無限和 `sum_of_exponential_times_polynomial_limit/2_04` | 3.495 | 0.954 | 440.9 | 212.3 |

比較対象はcommit `fa2cf00275c11e35299bea5af0585f548d413aec` のPowerTable・PolynomialExponentialSum・Comb・連続点補間。必要な関数とclassをASTからそのまま抽出し、問題用の入出力を付けた。無関係なimportは省いている。外部の最速提出との速度比較ではない。

## 変更内容

- 冪表はすべての底で累乗せず、素数の冪から合成数の値を作る。因数を置く領域は、そのまま返り値の配列へ上書きする。
- 無限和では逆階乗の表だけを持ち、標本に掛ける係数を逆順に更新する。等比列・累積和・階乗の配列を保持しない。
- 有限和は逆階乗表を無限和と補間で共有する。補間の片側の積を走査中に更新し、大きな整数になる前に剰余を取る。
- 定数だけを使うFPSへのimportを外した。コピー用コードにNTTや組合せ表は含まれない。

公開関数名・引数順・返り値は変更していない。冪表は合成数の法にも対応し、多項式和は従来どおり標本数より大きい素数の法を前提とする。

## 検証範囲

有限和20ケース、無限和10ケースを公式時間制限の5秒以内で通過。さらに各問題の遅かった3ケースを5回ずつ測定した。前後比較の表は上記1ケースずつの結果であり、すべての入力で同じ倍率になるとは限らない。

専用テストは素朴な総和・組込みpowとの比較、0の0乗、公比0・1、負の標本、合成数の法、法の周期をまたぐ項数、大きな標本数を確認する。オンライン提出は行っていない。

- [有限和の前後比較](../benchmarks/results/sum_of_exponential_times_polynomial_comparison.json)
- [無限和の前後比較](../benchmarks/results/sum_of_exponential_times_polynomial_limit_comparison.json)
- [比較用の旧コード](../benchmarks/baselines/polynomial_exponential_sum_before.py)
- [有限和の公式全件結果](../../verify/library_checker/results/sum_of_exponential_times_polynomial.json) / [反復測定](../../verify/library_checker/benchmarks/sum_of_exponential_times_polynomial.json)
- [無限和の公式全件結果](../../verify/library_checker/results/sum_of_exponential_times_polynomial_limit.json) / [反復測定](../../verify/library_checker/benchmarks/sum_of_exponential_times_polynomial_limit.json)

## 再測定

リポジトリ直下から実行する。無限和の比較は問題名とsnapshot・after・outputの末尾を`sum_of_exponential_times_polynomial_limit`へ替え、ケースを`2_04`にする。

```sh
pypy3 library_codex/benchmarks/official_benchmark.py sum_of_exponential_times_polynomial sum_of_exponential_times_polynomial_limit --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/results/sum_of_exponential_times_polynomial_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/other/sum_of_exponential_times_polynomial --cases 2_06 --variant before=library_codex/benchmarks/baselines/polynomial_exponential_sum_before.py --variant after=verify/library_checker/solutions/sum_of_exponential_times_polynomial.py --repeat 5 --output library_codex/benchmarks/results/sum_of_exponential_times_polynomial_comparison.json
```
