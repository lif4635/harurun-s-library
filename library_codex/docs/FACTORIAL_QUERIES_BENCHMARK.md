# 大量の階乗問い合わせの検証とPyPy測定

`combinatorics/FactorialQueries.py`の`factorials`は、998244353を法とする階乗を入力順にまとめて返す。法の後半の添字をWilsonの定理で前半へ移し、等間隔評価で幅1024ごとの積を作る。同じ区切り内の問い合わせは途中結果を再利用する。多項式の評価は[Library Checker公式解の前計算](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/enumerative_combinatorics/many_factorials/sol/correct_log_time_multieval_faster.cpp)を参考にしている。問い合わせ側は多点評価ではなく、短い端数の乗算を使う。

## 公式ケース

公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。[Many Factorials](https://judge.yosupo.jp/problem/many_factorials)の12ケースすべてを、依存込みの単独コードと公式checkerで通過した。最大問い合わせ数100000、制限10秒。オンライン提出は行っていない。

## 区切り幅の比較

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。各ケース・方式を新しいprocessで5回ずつ逐次測定し、方式の順序を反復ごとに変えた。起動・JIT・入出力を含み、出力は毎回公式checkerで照合した。

| 公式ケース | 幅512 | 幅1024 | 幅2048 |
| --- | ---: | ---: | ---: |
| random_00 | 1.069秒 | 0.935秒 | 1.015秒 |
| many_bits_01 | 1.067秒 | 0.930秒 | 0.991秒 |
| near_half_00 | 0.981秒 | 0.809秒 | 0.746秒 |

時間は中央値。幅1024の最大RSSは124812 KiB。3ケース中2ケースで速い1024を採用したが、すべての分布で最速ではない。

先行比較では、添字をソートして先頭から掛け続ける方法は、random_00・near_max_00・many_bits_01で中央値4.125〜4.170秒。幅2048の方法は0.681〜0.947秒だった。この比較の記録は採用前の設定であり、最終版の速度とは分けて扱う。

## 最終版の反復測定

公式全件検証で遅かった3ケースを各5回測定した。最大中央値は0.709秒、最大RSSは112976 KiB。比較harnessのimport経路と違い、この測定は提出用standalone codeを実行する。

- [公式全件の判定](../../verify/library_checker/results/many_factorials.json)
- [最終版の各回の時間・RSS・入力とsourceのhash](../../verify/library_checker/benchmarks/many_factorials.json)
- [区切り幅512・1024・2048の比較](../benchmarks/results/factorial_queries_block_size.json)
- [順次乗算・幅2048・4096・8192の比較](../benchmarks/results/factorial_queries_comparison.json)

メモリ制限は強制していない。C++上位提出との実測比較ではない。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/combinatorics/test_factorial_queries.py
pypy3 library_codex/tools/check_library_checker.py test many_factorials --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py many_factorials --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/factorial_queries_benchmark.py --official /path/to/library-checker-problems --variants 512 1024 2048 --cases random_00 many_bits_01 near_half_00 --repeat 5 --output library_codex/benchmarks/results/factorial_queries_block_size.json
```
