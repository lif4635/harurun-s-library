# 三角形内の点数え上げの検証とPyPy測定

`geometry/TrianglePointCounter.py`は、固定した頂点候補と対象点から、指定した三角形の内部の点数を返す。候補数N、対象点数Mに対して構築はO((N+1)(N+M) log(N+M+2))時間・O(N²+M)追加領域、問い合わせはO(1)。整数座標の四則演算・比較をO(1)として数える。

## 検証

Library Checkerの`count_points_in_triangle`を公式生成器・checkerで検証し、10 / 10ケースを通過した。公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`、制限時間は5秒。[公式高速解答](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/geo/count_points_in_triangle/sol/fast.cpp)の偏角・高さによる前計算と境界処理を参考にした。

[専用test](../verify/geometry/test_triangle_point_counter.py)では、ランダム点集合の全三点組を外積による総当たりと比較する。10の30乗程度の座標、水平辺、重複した候補・対象点、辺上の点、退化した三角形、空の点集合、入力変更、不正な添字も検査する。

## 反復測定

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。全件検証で遅かった3ケースを、新しいprocessで各5回逐次測定した。起動・JIT・入出力を含み、ケース順は反復ごとに入れ替える。すべての出力を公式checkerで検査した。

| ケース | 中央値 | 最大RSS |
| --- | ---: | ---: |
| dense_01 | 1.723秒 | 137,240 KiB |
| dense_00 | 1.571秒 | 136,920 KiB |
| max_random_01 | 1.485秒 | 146,824 KiB |

この環境での単独測定で、上位提出との速度比較ではない。オンライン提出と全ケースの反復測定は行っていない。メモリ制限は強制していない。

- [公式全件の判定](../../verify/library_checker/results/count_points_in_triangle.json)
- [各回の時間・RSS、入力・sourceのhash](../../verify/library_checker/benchmarks/count_points_in_triangle.json)
- [問題用driver](../../verify/library_checker/drivers/count_points_in_triangle.py)

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/geometry/test_triangle_point_counter.py
pypy3 library_codex/tools/check_library_checker.py test count_points_in_triangle --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py count_points_in_triangle --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
