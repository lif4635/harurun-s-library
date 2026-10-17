# 三角形の内部にある点の個数

三角形の頂点候補と数える対象の点を固定し、頂点候補から3点を選ぶ問い合わせに答える。辺上・頂点上の点は数えない。

## 主な機能

`TrianglePointCounter(vertices, points)`で前計算し、`count(a, b, c)`で`vertices`の3点からなる三角形内の点数を取得する。三角形ごとに対象点を走査し直す必要はなく、問い合わせはO(1)。頂点の順序は時計回り・反時計回りのどちらでもよい。

候補点数をN、対象点数をMとすると、構築はO((N+1)(N+M) log(N+M+2))時間、追加メモリはO(N²+M)。整数座標の四則演算・比較をO(1)として数える。

## 使い方

```python
from library_codex.geometry.TrianglePointCounter import TrianglePointCounter

vertices = [(0, 0), (4, 0), (0, 4)]
points = [(1, 1), (1, 1), (2, 2), (0, 1), (5, 5)]
counter = TrianglePointCounter(vertices, points)
inside = counter.count(0, 1, 2)
degenerate = counter.count(0, 0, 2)
```

- `inside`は`2`。内部の`(1, 1)`が2個あり、両方を数える。
- `(2, 2)`と`(0, 1)`は辺上なので含めない。`(5, 5)`は外部。
- `degenerate`は`0`。面積が0の三角形に内部はない。

## 仕組み

各候補点を基準に偏角順と高さ順で走査し、2点の間の高さにある対象点を「線分より左」「線分上」に分けて前計算する。問い合わせでは3辺に対応する点数を加減し、境界上の点を除く。偏角の比較には整数の外積を使う。

## 注意点

- 入力は整数座標の`(x, y)`列。候補点も対象点も重複でき、両方に同じ座標があってもよい。
- 点集合は構築時に固定する。元の入力列を変更しても前計算は変わらない。
- 3頂点が一直線上の場合も`0`。存在しない候補点の添字は`IndexError`。
- 候補点の組ごとに表を持つため、メモリはNの2乗に比例する。

## 参考

[Library Checker公式高速解答](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/geo/count_points_in_triangle/sol/fast.cpp)の前計算と境界処理を参考にしている。
