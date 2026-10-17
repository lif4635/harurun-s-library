# 巨大整数乗算の検証とPyPy測定

`number_theory/BigIntegerMultiplication.py`は、符号付き10進・16進文字列の積を文字列で返す。入力長の合計をNとしてO(N log(N+1))時間、O(N)追加領域。小さい入力は組み込み整数、片方の桁数が少ない入力は直接の畳み込みを使う。

## 整数への復元

10進は5桁、16進は4桁ずつに分け、998244353と469762049を法とするNTTを使う。畳み込み後の係数数は2の23乗以下に制限する。このとき短い側の配列長は2の22乗以下で、10進の係数の上限は次を満たす。

$$
2^{22}(10^5-1)^2 < 998244353\cdot469762049.
$$

16進の基数は2の16乗で、係数の上限はさらに小さい。したがって中国剰余定理で非負整数の係数を一意に復元できる。復元後に繰り上がりを処理する。浮動小数点は使わない。

## 公式ケース

公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。問題用driverを依存込みの単独コードへ展開し、公式生成器とcheckerで検証した。

| 問題 | 1整数の最大桁数 | 通過ケース | 制限時間 |
| --- | ---: | ---: | ---: |
| [10進乗算](https://judge.yosupo.jp/problem/multiplication_of_big_integers) | 2,000,000 | 20 / 20 | 5秒 |
| [16進乗算](https://judge.yosupo.jp/problem/multiplication_of_hex_big_integers) | 1,600,000 | 22 / 22 | 5秒 |

## 反復測定

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。全件検証で遅かった各3ケースを、新しいprocessで各5回逐次測定した。起動・JIT・入出力を含み、ケース順は反復ごとに入れ替える。すべての出力を公式checkerで検査した。

| 問題 | ケース | 中央値 | 最大RSS |
| --- | --- | ---: | ---: |
| 10進乗算 | max_max_05 | 0.830秒 | 126,404 KiB |
| 10進乗算 | max_max_04 | 0.829秒 | 125,508 KiB |
| 10進乗算 | max_max_01 | 0.829秒 | 126,448 KiB |
| 16進乗算 | max_max_04 | 0.962秒 | 128,540 KiB |
| 16進乗算 | max_max_02 | 0.979秒 | 131,912 KiB |
| 16進乗算 | max_max_01 | 0.969秒 | 131,972 KiB |

この環境での単独測定で、上位提出や組み込み整数との速度比較ではない。オンライン提出と全ケースの反復測定は行っていない。メモリ制限は強制していない。

- 公式全件の判定: [10進](../../verify/library_checker/results/multiplication_of_big_integers.json)、[16進](../../verify/library_checker/results/multiplication_of_hex_big_integers.json)
- 各回の時間・RSSと入力・sourceのhash: [10進](../../verify/library_checker/benchmarks/multiplication_of_big_integers.json)、[16進](../../verify/library_checker/benchmarks/multiplication_of_hex_big_integers.json)
- 問題用driver: [10進](../../verify/library_checker/drivers/multiplication_of_big_integers.py)、[16進](../../verify/library_checker/drivers/multiplication_of_hex_big_integers.py)

## APIの検査

[専用test](../verify/number_theory/test_big_integer_multiplication.py)では、符号と長さを変えたランダム入力を組み込み整数と比較する。全桁で繰り上がる積、平方、片方だけ短い入力、先頭0、負の0、16進の大小文字、不正入力、疎な桁列も検査する。10進文字列変換の上限を640桁に設定しても、それを変更せず大きい積を返すことを確認する。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/number_theory/test_big_integer_multiplication.py
pypy3 library_codex/tools/check_library_checker.py test multiplication_of_big_integers multiplication_of_hex_big_integers --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py multiplication_of_big_integers multiplication_of_hex_big_integers --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
