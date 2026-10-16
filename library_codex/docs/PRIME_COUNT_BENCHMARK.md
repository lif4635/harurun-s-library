# 素数の個数の速度比較

`prime/Sieve.py`の`prime_count(number)`を使う。上限以下の素数を列挙せず、個数を整数で返す。

## 実装

商ごとの素数個数DPを、奇数だけの2配列に保存する。小さい値と大きい商を分け、辞書の検索、偶数の状態、別の合成数表を取り除いた。時間 O(N^(3/4) / log N)、追加メモリ O(√N)。整数演算をO(1)として数える。

[Nyaanの素数個数](https://nyaannyaan.github.io/library/multiplicative-function/prime-counting-faster.hpp.html)の2配列表現を参考にした。商は整数除算で求め、浮動小数点による除算の近似は使わない。

## 同一入力の比較

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。公式入力ごとに別processを起動し、起動・JIT・入出力を含めて各5回測定した。実行順を入れ替え、各回を公式checkerで検証している。

比較前はcommit `1e10e3a79dc07ac646a3ef4efb3f1a7bdf6942aa`の`prime_count`。関数と同じ入出力だけを保存して比較した。

| 公式ケース | 比較前の中央値 | 今回の中央値 | 比較前の最大RSS | 今回の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| max_00 | 2.498秒 | 0.299秒 | 119,864 KiB | 64,164 KiB |
| random_00 | 1.961秒 | 0.281秒 | 119,880 KiB | 64,020 KiB |

この2入力では約7〜8倍速くなり、最大RSSも小さくなった。外部最速提出との速度比較ではない。

- [各回の時間・RSS・hash・checker照合](../benchmarks/results/prime_count_comparison.json)
- [比較対象のrevision](../benchmarks/results/prime_count_snapshot.json)
- [比較前の実装](../benchmarks/baselines/prime_count_before.py)
- [公式全31ケースの検証](../../verify/library_checker/results/counting_primes.json)
- [公式の遅いケースの反復測定](../../verify/library_checker/benchmarks/counting_primes.json)

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test counting_primes --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py counting_primes --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/results/prime_count_snapshot.json --problem /path/to/library-checker-problems/number_theory/counting_primes --cases max_00 random_00 --variant before=library_codex/benchmarks/baselines/prime_count_before.py --variant after=verify/library_checker/solutions/counting_primes.py --repeat 5 --output library_codex/benchmarks/results/prime_count_comparison.json
```
