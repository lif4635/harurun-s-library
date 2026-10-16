# φ関数の総和の速度比較

`prime/Sieve.py` の `sum_totient(limit, mod=None)` を使う。`mod=None`なら整数の総和、正の整数を指定するとその余りを返す。合成数の法も使える。既存の `MultiplicativeFunctions.sum_totient_fast` も同じ実装を利用する。

## 実装

N^(2/3)までのφの表を累積和へ上書きし、それより大きい商について総和を小さい順に計算する。辞書・再帰・最小素因数表・Möbius表は使わない。時間 O(N^(2/3) log log N)、メモリ O(N^(2/3))。整数演算をO(1)として数える。

参照は [Library Checkerの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/number_theory/sum_of_totient_function/sol/correct.cpp)。小さい値の前計算と商の総和DPを分ける方針を確認し、Pythonでは整数配列と平方根で分けたループを使った。C++実装との時間比較ではない。

## 同一入力の比較

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。公式入力ごとに別processを起動し、起動・JIT・入出力を含めて各5回測定した。実行順を入れ替え、各回を公式checkerで確認している。

比較前はcommit `822fe443` の `sum_totient_fast`。O(N)メモリを使う旧 `sum_totient` ではなく、以前からあった商DPの高速版と比較した。

| 公式ケース | 比較前の中央値 | 今回の中央値 | 比較前の最大RSS | 今回の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| max_00 | 2.396秒 | 0.520秒 | 93,864 KiB | 98,200 KiB |
| random_07 | 2.471秒 | 0.573秒 | 93,724 KiB | 97,968 KiB |

少し多めの前計算領域を使い、計算時間を短縮している。全入力での速度比や外部最速提出との比較を示すものではない。

- [各回の時間・RSS・hash・checker照合](../benchmarks/results/sum_totient_comparison.json)
- [比較対象のrevision](../benchmarks/results/sum_totient_snapshot.json)
- [比較前の実装](../benchmarks/baselines/sum_totient_before.py)
- [公式全ケースの検証](../../verify/library_checker/results/sum_of_totient_function.json)
- [公式の遅いケースの反復測定](../../verify/library_checker/benchmarks/sum_of_totient_function.json)

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test sum_of_totient_function --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py sum_of_totient_function --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/results/sum_totient_snapshot.json --problem /path/to/library-checker-problems/number_theory/sum_of_totient_function --cases max_00 random_07 --variant before=library_codex/benchmarks/baselines/sum_totient_before.py --variant after=verify/library_checker/solutions/sum_of_totient_function.py --repeat 5 --output library_codex/benchmarks/results/sum_totient_comparison.json
```
