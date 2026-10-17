# 2冪法の乗法畳み込みの検証とPyPy測定

`arithmetic_convolution/MultiplicativeConvolutionModPowerOfTwo.py`は、添字の積を配列長Lで割った余りごとに係数の積を集計する。Lは2の冪、係数の法は998244353。0と偶数も扱い、O(L log(L+1))時間・O(L)追加領域で計算する。

## 検証

Library Checkerの`mul_mod2n_convolution`を公式生成器・checkerで検証し、47 / 47ケースを通過した。公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`、制限時間は5秒。[公式解答](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/convolution/mul_mod2n_convolution/sol/correct.cpp)の2進付値による分解を使い、既存の`NTT998`で変換する。小さい法への折り返しには変換済み配列の一部を再利用する。

[専用test](../verify/arithmetic_convolution/test_multiplicative_convolution_mod_power_of_two.py)では、長さ1〜256のランダム列を二重ループと比較する。負の係数、同じ配列の平方、入力非破壊、単一要素だけが非零の全組、長さが異なる入力・空列・2の冪でない長さも検査する。

## 反復測定

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。全件検証で遅かった3ケースを、新しいprocessで各5回逐次測定した。起動・JIT・入出力を含み、ケース順は反復ごとに入れ替える。すべての出力を公式checkerで検査した。

| ケース | 中央値 | 最大RSS |
| --- | ---: | ---: |
| large_00 | 0.874秒 | 238,396 KiB |
| n_equals_20 | 0.814秒 | 241,744 KiB |
| large_01 | 0.853秒 | 242,888 KiB |

この環境での単独測定で、上位提出との速度比較ではない。オンライン提出と全ケースの反復測定は行っていない。メモリ制限は強制していない。

- [公式全件の判定](../../verify/library_checker/results/mul_mod2n_convolution.json)
- [各回の時間・RSS、入力・sourceのhash](../../verify/library_checker/benchmarks/mul_mod2n_convolution.json)
- [問題用driver](../../verify/library_checker/drivers/mul_mod2n_convolution.py)

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/arithmetic_convolution/test_multiplicative_convolution_mod_power_of_two.py
pypy3 library_codex/tools/check_library_checker.py test mul_mod2n_convolution --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py mul_mod2n_convolution --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
