# 最小全域木とマンハッタンMST

すべての頂点を、辺重みの合計が最小になるようにつなぐ。

## 主な機能

- `minimum_spanning_tree(n, edges)` — 重み付き無向グラフから最小全域木を選ぶ。非連結なら `None`。
- `minimum_spanning_forest(n, edges)` — 非連結でも、各連結成分を最小費用でつなぐ。成分数も返す。
- `kruskal(n, edges)` — 最小全域森の費用だけを返す。
- `manhattan_mst(points)` — 平面上の点をマンハッタン距離でつなぐ。全点対の辺を作らず `O(N log(N+1))` で求める。
- `second_spanning_tree(n, edges, strict=False)` — 最小全域木とは辺集合の異なる木を、一つの辺の交換で求める。

辺列から求める最小全域木・森は `O(N+M log(M+1))`。Mは入力辺数で、平行辺や負の重みも使える。

## 使い方

```python
from library_codex.graph_spanning.MinimumSpanningTree import minimum_spanning_tree, manhattan_mst

edges = [(0, 1, 5), (1, 2, 2), (0, 2, 10)]
cost, edge_ids = minimum_spanning_tree(3, edges)
assert cost == 7
assert set(edge_ids) == {0, 1}

points = [(0, 0), (2, 0), (2, 3)]
cost, pairs = manhattan_mst(points)
assert cost == 5
assert len(pairs) == 2
```

- `edge_ids`: 入力 `edges` の添字。端点の組ではない。
- `pairs`: マンハッタンMSTが選んだ `(u, v)` のlist。uとvは入力 `points` の添字。
- 最小全域森の第3要素: 連結成分数。選んだ辺数はNからこの値を引いた数になる。

## 注意点

- 解が複数ある場合の選び方や、返す辺の順序は保証しない。入力は変更しない。
- 同じ座標の点も別頂点として扱い、距離0の辺でつなぐ。
- `second_spanning_tree` の `strict=False` は同じ費用の別の木も許す。`True` は費用が真に大きい木だけを対象にする。
- マンハッタンMSTは4方向の走査と座標圧縮したBITで候補辺を絞る。全点対の辺を列挙する必要はない。
