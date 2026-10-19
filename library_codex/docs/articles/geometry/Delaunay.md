# ドロネー三角形分割

平面上の整数座標を結び、どの三角形の外接円の内部にも他の点がない三角形分割の辺を返す。

## 主な機能

`delaunay_edges(points)`は、全点対を列挙せずに`O(N)`本の候補辺を作る。ユークリッド最小全域木を作るのに十分な辺が含まれるため、距離で結ぶ完全グラフを小さくして扱いたいときに使える。最小全域木だけが必要なら、`geometry/EuclideanMST`の`euclidean_mst`を直接使う。

構築は`O(N log N)`時間、追加空間は`O(N)`。整数の算術演算を定数時間と数えた計算量で、巨大整数では桁数に応じた費用もかかる。

## 使い方

```python
from library_codex.geometry.Delaunay import delaunay_edges

points = [(0, 0), (3, 0), (0, 4)]
edges = delaunay_edges(points)
assert sorted(tuple(sorted(edge)) for edge in edges) == [(0, 1), (0, 2), (1, 2)]
```

- `edges`: 無向辺のlist。各`(u, v)`は`points[u]`と`points[v]`を結ぶ。
- 辺の順序と向きは未規定。三角形のlistや、頂点を巡る順序ではない。
- 全点が一直線上なら、座標順に隣り合う点を結ぶ鎖を返す。空入力や一点では`[]`。

## 重複点と同一円周上の点

- 同じ座標は一つの代表点で三角形分割し、残りの入力点は代表点へ長さ0の辺で結ぶ。返る番号は重複を除く前の入力番号で、代表点にはその座標が最初に現れた番号を使う。
- 4点以上が同じ円周上にある場合、対角線の選び方は一意ではない。そのうち一つの三角形分割を返す。取り得る全対角線を列挙するAPIではない。
- 浮動小数点座標は対象外。向きと外接円の判定には整数演算だけを使う。

## 参考

[Library Checkerの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/geo/euclidean_mst/sol/correct.cpp)の分割統治法を基にしている。standalone codeにもApache License 2.0の表記を含む。
