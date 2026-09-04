# 二部グラフの最大マッチング

## 主な機能

左側に $L$ 頂点、右側に $R$ 頂点を持つ二部グラフで、互いに端点を共有しない辺を最大本数選びます。辺を後から追加して再び`solve()`することもできます。

最大マッチングに加え、最小頂点被覆、最大独立集合、最小辺被覆、DM分解、辺と頂点の必須性を取得できます。

## 使い方

```python
from library_codex.graph_matching.BipartiteMatching import BipartiteMatching

matching = BipartiteMatching(3, 4)
matching.add_edge(0, 1)
matching.add_edge(0, 2)
matching.add_edge(1, 0)
matching.add_edge(2, 2)

size = matching.solve()
edges = matching.pairs()
```

- `size`: 最大マッチングの辺数。
- `edges`: 選ばれた`(left, right)`の列。左右の頂点番号はそれぞれ0から始まる。
- `match_left[left]`: 対応する右頂点。マッチされていなければ-1。
- `match_right[right]`: 対応する左頂点。マッチされていなければ-1。

## 必ずマッチされる頂点

```python
left_flags, right_flags = matching.essential_vertices()
```

- `left_flags[left]`: 左頂点`left`が、どの最大マッチングでも必ず何らかの辺に使われるか。
- `right_flags[right]`: 右頂点`right`が、どの最大マッチングでも必ず何らかの辺に使われるか。
- 必ず使われる辺を調べる`essential_edges()`とは異なり、相手が変わっても頂点が常にマッチされるなら`True`になる。

## allowed_verticesがない理由

「少なくとも一つの最大マッチングでマッチされる頂点」は、孤立頂点でないすべての頂点です。最大マッチングで頂点$v$が未マッチなら、その隣接頂点$u$は必ず別の頂点とマッチされています。その辺を$(u,v)$へ交換すれば、大きさを変えずに$v$をマッチできます。

したがって頂点についてのallowed判定は、左側なら`bool(matching.graph[left])`、右側ならいずれかの左頂点から辺が来ているかを調べるだけです。専用APIにはせず、情報量のある`essential_vertices()`だけを提供します。

## 計算量

- `solve()`: $O(E\sqrt{L+R})$
- `essential_vertices()`: 最大マッチング計算後は $O(L+R+E)$
