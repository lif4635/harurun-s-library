# 巨大整数除算の検証とPyPy測定

`number_theory/BigIntegerDivision.py`は、10進・16進文字列の商と余りを求める。符号付きの入力に対してPythonの`divmod`と同じ切り下げ除算を行う。整数を直接扱う別名APIは作らず、すでに`int`の入力には標準の`divmod`を使う。

## 実装

整数の除算にはPyPy標準の`divmod`を採用する。16進の文字列変換も標準機能を使う。自前の整数Newton法による逆数近似と比較し、同じ公式入力で標準除算が速かったためである。

10進の文字列は512桁単位で読み、平衡な順序で整数へ結合する。整数から文字列への変換は10の冪で二分する。この除算は2の冪によるbitシフトと5の冪による除算に分ける。全体は反復処理で実装している。浮動小数点と外部packageは使わない。

入力の合計bit数をN、標準整数除算の時間をD(N)、整数乗算の時間をM(N)とする。16進版はO(D(N)+N)時間、10進版はO((D(N)+M(N)+N) log(N+1))時間が上界で、いずれも追加領域はO(N) bit。D(N)・M(N)は処理系によって異なる。10進変換の各段で処理する合計bit数はO(N)、段数はO(log(N+1))。文字列変換の上限設定は変更しない。

## 公式ケース

公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。依存込みの単独コードを公式checkerで検証した。オンライン提出はしていない。

| 問題 | 1整数の最大桁数 | 通過ケース | 制限時間 |
| --- | ---: | ---: | ---: |
| [10進除算](https://judge.yosupo.jp/problem/division_of_big_integers) | 2,000,000 | 26 / 26 | 10秒 |
| [16進除算](https://judge.yosupo.jp/problem/division_of_hex_big_integers) | 1,600,000 | 27 / 27 | 10秒 |

## 測定条件

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。新しいprocessで逐次測定し、起動・JIT・入出力を含める。入力・期待出力・source・checkerのhashと各回の時間・最大RSSをJSONへ記録する。反復ごとに実行順を入れ替え、毎回公式checkerで出力を確認する。メモリ制限は強制していない。

公式ベンチマークは、全件検証で遅かった各3ケースを各5回測る。全ケースの反復測定や、Library Checker上位提出との比較ではない。

| 問題 | ケース | 中央値 | 最大RSS |
| --- | --- | ---: | ---: |
| 10進 | length_ratio_integer_05 | 5.852秒 | 110,796 KiB |
| 10進 | length_ratio_integer_04 | 5.665秒 | 113,072 KiB |
| 10進 | length_ratio_integer_03 | 5.659秒 | 109,376 KiB |
| 16進 | length_ratio_integer_02 | 1.081秒 | 99,920 KiB |
| 16進 | length_ratio_integer_01 | 1.095秒 | 95,508 KiB |
| 16進 | length_ratio_integer_03 | 0.996秒 | 97,232 KiB |

採用版の反復測定で最も遅かった1回は、10進6.309秒、16進1.232秒だった。

## 比較する方式

- 採用版: 標準の`divmod`と、平衡な10進変換。
- Newton版: 除数の先頭bitから逆数を近似し、精度を倍増する。10進出力では同じ除数の逆数を共有する。
- 逆数再計算版: Newton版と同じだが、10進出力の分割ごとに逆数を求め直す。
- 16進の標準機能のみ: `int(..., 16)`、`divmod`、`format(..., 'X')`を直接呼ぶ。ライブラリの入力形式検査を含まない。

不採用のNewton版は[比較専用コード](../benchmarks/variants/big_integer_division_newton.py)へ残し、提出用bundleには含めない。

| 問題・ケース | 採用版の中央値 | Newton版 | 逆数再計算版 |
| --- | ---: | ---: | ---: |
| 10進 length_ratio_integer_03 | 6.068秒 | 7.926秒 | 9.091秒 |
| 10進 length_ratio_integer_05 | 6.175秒 | 8.049秒 | 10.011秒 |

10進の2ケースを各3回比較した結果、採用版は逆数を共有するNewton版より約23%短時間だった。逆数再計算版は10秒を超える回もあった。比較用の起動処理を含むため、公式driverだけの測定値とは区別する。

16進も3ケースを各5回比較する。`length_ratio_integer_00`では、採用版1.136秒、Newton版2.123秒、標準機能を直接呼ぶ版1.121秒だった。入力形式の検査を残したまま、除算本体を標準へ任せる方針を採用した。

## APIの検査

[専用test](../verify/number_theory/test_big_integer_division.py)で、標準`divmod`との比較、符号の全組合せ、0、割り切れる場合、除数直前の余り、桁数が大きく異なる入力、最大90万bit以上の既知の商と余りを検査する。10進・16進の先頭0、不正文字、ゼロ除算も検査する。10進変換上限を640桁にしたまま1万桁の除算ができ、設定が変わらないことを確認する。

## 記録と再実行

- 公式全件判定: [10進](../../verify/library_checker/results/division_of_big_integers.json)、[16進](../../verify/library_checker/results/division_of_hex_big_integers.json)
- 公式反復測定: [10進](../../verify/library_checker/benchmarks/division_of_big_integers.json)、[16進](../../verify/library_checker/benchmarks/division_of_hex_big_integers.json)
- 方式比較: [10進](../benchmarks/results/division_of_big_integers_comparison.json)、[16進](../benchmarks/results/division_of_hex_big_integers_comparison.json)
- 問題用driver: [10進](../../verify/library_checker/drivers/division_of_big_integers.py)、[16進](../../verify/library_checker/drivers/division_of_hex_big_integers.py)

```sh
pypy3 -m pytest -q library_codex/verify/number_theory/test_big_integer_division.py
pypy3 library_codex/tools/check_library_checker.py test division_of_big_integers division_of_hex_big_integers --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py division_of_big_integers division_of_hex_big_integers --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/big_integer_division_benchmark.py --radix 10 --cases length_ratio_integer_03 length_ratio_integer_05 --repeat 3 --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/big_integer_division_benchmark.py --radix 16 --repeat 5 --official /path/to/library-checker-problems
```
