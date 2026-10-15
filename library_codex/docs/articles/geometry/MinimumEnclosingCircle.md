# 最小包含円

点集合をすべて含む最小の円と、その円周上にある点を求める。

## 主な機能

- `minimum_enclosing_circle(points)` は中心・半径・円を決める点の番号を返す。中心と半径は浮動小数点数。
- `minimum_enclosing_circle_boundary(points)` は整数座標専用。入力点ごとに、円周上なら1、内部なら0を返す。浮動小数点数や誤差許容幅を使わず、円周の直近にある内点も区別する。

どちらもランダムな順番で点を追加する。演算回数は期待 O(N)、最悪 O(N^3)。境界判定ではPythonの多倍長整数を使うため、座標の桁数にも実行時間が依存する。

## 使い方

```python
points = [(5, 0), (0, 5), (-5, 0), (0, -5), (3, 4), (0, 0)]
flags = minimum_enclosing_circle_boundary(points)
assert flags == [1, 1, 1, 1, 1, 0]
boundary = [i for i, flag in enumerate(flags) if flag]
assert boundary == [0, 1, 2, 3, 4]
center, radius, support = minimum_enclosing_circle(points)
assert center == (0.0, 0.0)
assert radius == 5.0
```

- `center`: 中心の座標。
- `radius`: 半径。
- `support`: 円を決定する1〜3個の点の入力番号。円周上の点すべての一覧ではない。
- `flags[i]`: 入力のi番目の点が円周上にあるか。

## 注意点

- 空の入力は`ValueError`。同じ点が複数あってもよい。全点が同じなら半径0で、全点が円周上になる。
- 中心・半径を返す関数は近似計算。整数座標での厳密な境界判定には`minimum_enclosing_circle_boundary`を使う。
- `seed`で点の処理順を変えられる。既定値は再現性のため固定されており、特定の入力に対して最悪計算量を排除するものではない。
