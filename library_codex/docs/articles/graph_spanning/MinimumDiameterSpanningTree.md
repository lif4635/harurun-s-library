# 最小直径全域木

非負重みの無向グラフから、木の中で最も遠い2頂点の距離が最小になる全域木を選ぶ。

## 主な機能

`minimum_diameter_spanning_tree(n, edges)`に頂点数と`(u, v, weight)`の辺リストを渡す。返るのは最小直径と、採用した入力辺の番号。

辺の重みの合計を最小にする最小全域木とは目的が異なる。たとえば、どの2頂点間もなるべく短い経路で移動できる木を作りたいときに使う。

- 多重辺、重み0の辺を扱える。自己ループは選ばない。
- 非連結なら`None`を返す。
- 時間 O(V(V + E) log(V + E))、追加メモリ O(V² + E)。整数演算をO(1)として数える。

## 使い方

```python
from library_codex.graph_spanning.MinimumDiameterSpanningTree import minimum_diameter_spanning_tree

edges = [(0, 1, 3), (1, 2, 2), (2, 3, 4), (0, 3, 20)]
diameter, ids = minimum_diameter_spanning_tree(4, edges)
assert diameter == 9
assert ids == [0, 1, 2]
chosen_edges = [edges[i] for i in ids]
```

- `diameter`: 選んだ木の頂点間距離の最大値。距離は経路上の辺の重みの合計。
- `ids`: 入力`edges`の添字を昇順に並べたリスト。非空のグラフでは長さは`n - 1`。親頂点の配列ではない。
- `None`: 全頂点をつなぐ木が存在しない。tupleへ展開する前に確認する。

空のグラフと頂点数1のグラフには`(0, [])`を返す。

## 仕組み

全頂点からの最短距離を求め、全頂点までの距離の最大値が最小になる中心を探す。中心は頂点上に限らず辺の途中にも置ける。

中心が辺の途中にある場合は、その両端を出発点として最短路木を作り、中心のある辺でつなぐ。頂点ごとの距離順を使って候補を走査するため、辺の上を二分探索しない。

中心の位置は2倍した整数で扱う。重みが整数なら、半整数の中心でも浮動小数点の誤差を生じない。

## 注意点

- 辺の重みには0以上の整数を渡す。負辺には対応しない。
- 入力の辺リストは変更しない。最適な木が複数あれば1つを返す。
- 全頂点対の距離を保存するため、大きな頂点数ではメモリに注意する。

## 参考

- [Library Checkerの公式解法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/graph/minimum_diameter_spanning_tree/sol/correct.cpp)
