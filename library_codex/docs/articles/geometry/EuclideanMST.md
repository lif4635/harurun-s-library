# ユークリッド最小全域木

平面上の全点を、線分の長さの合計が最小になる木で結ぶ。

## 主な機能

`euclidean_mst(points)`へ整数座標の列を渡すと、選んだ辺を入力点の番号で返す。`N`点間の全辺を作らず、ドロネー三角形分割の辺だけを候補にしてKruskal法を行う。構築は`O(N log N)`時間、追加空間は`O(N)`。

距離の大小は距離の二乗で比較し、平方根や丸め誤差を使わずに辺を選ぶ。計算量は整数の算術演算を定数時間と数えたもので、巨大整数では桁数に応じた費用もかかる。

## 使い方

```python
from math import hypot
from library_codex.geometry.EuclideanMST import euclidean_mst

points = [(0, 0), (3, 0), (0, 4)]
edges = euclidean_mst(points)
length = sum(hypot(points[u][0] - points[v][0], points[u][1] - points[v][1]) for u, v in edges)
assert length == 7.0
```

- `edges`: 長さ`max(0, len(points) - 1)`のlist。各`(u, v)`は`points[u]`と`points[v]`を結ぶ無向辺。
- 辺は長さの短い順。同じ長さの辺の順序・向き・どの最小全域木を選ぶかは未規定。
- `length`: 使用例で別に計算した長さの合計。関数自体は合計値を返さない。

## 注意点

- 同じ座標も別の入力点として扱い、長さ0の辺で接続する。全点が一直線上でも使える。
- 空入力や一点なら`[]`を返す。入力の並びは変更しない。
- 距離の二乗で辺を選んでも同じ最小全域木になるが、二乗を足した値は元の距離の合計ではない。
- 浮動小数点座標は対象外。辺の選択は整数で厳密に行い、長さの表示に必要な平方根だけを呼出し側で計算する。
