# 彩色多項式の検証とPyPy測定

`graph_enumeration/ChromaticPolynomial.py`は、隣接リストから彩色多項式の係数を返す。既存の集合冪級数の転置合成で独立集合への分割を求め、下降階乗から通常の係数へ変換する。[公式解答](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/graph/chromatic_polynomial/sol/correct.cpp)を参考にした。

連結成分ごとに計算し、木と完全グラフでは既知の積を直接展開する。N頂点、入力の隣接要素数M、各成分の頂点数cに対してO(M + N² + Σ c²2^c)時間、O(N + max(c2^c))追加メモリ。木・完全グラフの成分はO(c²)時間。

## 検証

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`の`chromatic_polynomial`を、公式生成器・checkerで34 / 34ケース検証した。最大20頂点、制限時間10秒。

[専用test](../verify/graph_enumeration/test_chromatic_polynomial.py)では、小さいランダムグラフで色の全割り当てを数え、多項式の評価と比較する。合成数の法、空グラフ、自己ループ、重複辺、非連結グラフ、片方向だけの隣接記載、完全グラフ、閉路、不正な頂点番号、入力非破壊も検査する。

## 反復測定

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。全件検証で遅かった3ケースを、新しいprocessで各5回逐次測定した。起動・JIT・入出力を含み、ケース順は反復ごとに入れ替える。すべての出力を公式checkerで検査した。

| ケース | 中央値 | 最大RSS |
| --- | ---: | ---: |
| big_02 | 3.440秒 | 324,916 KiB |
| big_08 | 3.293秒 | 324,984 KiB |
| random_04 | 3.250秒 | 325,040 KiB |

この環境での単独測定で、上位提出との直接比較ではない。オンライン提出と全ケースの反復測定は行っていない。メモリ制限は強制していない。

- [公式全件の判定](../../verify/library_checker/results/chromatic_polynomial.json)
- [各回の時間・RSS、入力・sourceのhash](../../verify/library_checker/benchmarks/chromatic_polynomial.json)
- [問題用driver](../../verify/library_checker/drivers/chromatic_polynomial.py)

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/graph_enumeration/test_chromatic_polynomial.py
pypy3 library_codex/tools/check_library_checker.py test chromatic_polynomial --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py chromatic_polynomial --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
