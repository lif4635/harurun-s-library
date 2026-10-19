# 乗法的関数の総和の検証

`number_theory/MultiplicativeFunctions.py`の`MultiplicativePrefixSum.run`で、素数上の累積和と素数冪の値から乗法的関数の総和を求める。公開APIは変更していない。

## 実装

[公式のMin 25実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/number_theory/sum_of_multiplicative_function/sol/min_25_sieve.cpp)を参考に、既存の反復探索を修正した。

- 各状態で全素数を走査していた処理を、残りの上限の平方根で打ち切る。
- 子に続く分岐がない場合は、状態を積まずに素数の集計表から直接足す。
- 素数の1乗・2乗に対するcallbackの値を共有する。
- 法指定時は探索中の係数を法で減らす。法省略時の整数・Fraction計算も維持する。
- 再帰は使わない。

素数の集計表は`O(N^(3/4)/log(N+2))`回の算術演算。`run`は`O((D+1)(T+1))`時間で、Dは`x*最大素因数(x)≤N`を満たす2以上の整数の個数、Tはcallbackの1回の時間。探索も表作成と同じ計算量だとは保証していない。

## 公式全件と反復測定

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae` の`sum_of_multiplicative_function`を30ケースすべて通過した。上限N=10¹¹、制限10秒。依存込みの単独コードをPyPyで実行し、公式checkerで照合した。オンライン提出は行っていない。

全件検証で遅かった3ケースを各5回、毎回新しいprocessで逐次実行した。PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。起動・JIT・入出力・素数表作成を含む。

| ケース | 時間の中央値 | 最大RSS |
| --- | ---: | ---: |
| random_00 | 3.189秒 | 191204 KiB |
| boundaryB_00 | 3.175秒 | 191236 KiB |
| max_00 | 3.171秒 | 195180 KiB |

15回すべて公式checkerで通過。最大RSSは約191 MiBで、メモリ制限は強制していない。上限10¹³の`sum_of_multiplicative_function_large`は、この結果の検証範囲に含めない。

- [公式全件の判定](../../verify/library_checker/results/sum_of_multiplicative_function.json)
- [各回の時間・RSS・入力とsourceのhash](../../verify/library_checker/benchmarks/sum_of_multiplicative_function.json)

## 変更前との比較

変更前のcommit `ccc0335adba8522f9f66e0a351a6a5e1cd9d7c54`から`run`だけを取り出して比較した。関数は`f(p**e)=123*e+456*p`、法469762049で共通。素数の集計表を準備してから計測を始め、毎回新しいPyPy processで各5回、実行順を混ぜて測った。

| N | 変更前の中央値 | 変更後の中央値 |
| --- | ---: | ---: |
| 10⁸ | 1.739秒 | 0.0317秒 |
| 10⁹ | 25.045秒 | 0.0483秒 |

全回で新旧の答えが一致した。この表は総和探索部分だけで、素数表作成・起動・入出力を含まない。提出全体が同じ倍率で速くなるという意味ではない。C++上位提出との速度比較でもない。

[比較の各回の記録とsourceのhash](../../verify/library_checker/benchmarks/multiplicative_sum_comparison.json)を保存している。

## 独立した正しさの検査

専用テスト7件で、全整数の素因数分解から求めた値との照合、φ関数・約数関数、ランダムな素数冪の値、負値、法1・合成数の法、Fraction、N=0・1、素数冪境界、繰り返し呼出し、入力表の非破壊を検査する。既存のDirichlet積・除算・累積和復元のテストも同じファイルで維持した。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/number_theory/test_multiplicative_functions.py
pypy3 library_codex/tools/check_library_checker.py test sum_of_multiplicative_function --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py sum_of_multiplicative_function --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/multiplicative_sum_comparison.py
```
