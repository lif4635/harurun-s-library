# 多変数の循環畳み込みの比較

`MultidimensionalDFT`の2点・3点の軸を直接計算する実装と、全軸でchirp-z変換を使う変更前の実装を比較した。API、係数の並び、逆変換の正規化は変えていない。

## 測定条件

- 測定日：2026-10-15 JST。
- WSL2、AMD Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。
- 変更前はlibrary revision `eebbfbfc1e1a27a3ddb0ebc96c55934571f5bd30`の実装と同じ入出力driverを展開し、[比較用コード](../benchmarks/baselines/multivariate_convolution_cyclic.py)へ保存。
- Library Checker公式の同じ入力を使い、新規PyPyプロセスで各5回、実装順を入れ替えて逐次実行。時間は起動・JIT・入出力込みの中央値。
- 各回の出力を公式checkerで検査。sourceと入力のhash、各回の時間・最大RSSは[測定JSON](../benchmarks/results/multivariate_circular_official_comparison.json)へ保存。

## 結果

| 公式ケース | 軸の長さ | 変更前 | 変更後 | 最大RSS 変更前→変更後 |
|---|---|---:|---:|---:|
| twos_00 | 2が18軸 | 4.808秒 | 0.215秒 | 99.7→104.4 MiB |
| threes_00 | 2と3が14軸 | 2.719秒 | 0.175秒 | 105.5→105.4 MiB |
| dim2_01 | 199と1317 | 4.068秒 | 4.171秒 | 104.3→101.6 MiB |

2点・3点の軸では、短い配列の確保、逆数の計算、汎用畳み込みの呼び出しを省ける。大きな軸は従来の処理を使い、このケースでは速度改善はない。最大RSSはPyPy・JIT・入出力も含む。

循環畳み込みは変更後の公式24ケースを全件通過。部分和の個数計算は24ケース、打ち切り畳み込みは17ケースを既存実装で通過した。これら3問題の定期的な測定は[公式ケースのベンチマーク一覧](../../verify/library_checker/benchmarks/README.md)にある。オンライン提出は行っていない。

## 再実行

公式ケースを生成済みの状態で、リポジトリ直下から実行する。

```sh
pypy3 library_codex/tools/check_library_checker.py test sharp_p_subset_sum multivariate_convolution multivariate_convolution_cyclic --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/results/multivariate_circular_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/multivariate_convolution_cyclic --cases twos_00 threes_00 dim2_01 --variant before=library_codex/benchmarks/baselines/multivariate_convolution_cyclic.py --variant after=verify/library_checker/solutions/multivariate_convolution_cyclic.py --repeat 5 --output library_codex/benchmarks/results/multivariate_circular_official_comparison.json
pypy3 library_codex/benchmarks/official_benchmark.py sharp_p_subset_sum multivariate_convolution multivariate_convolution_cyclic --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```
