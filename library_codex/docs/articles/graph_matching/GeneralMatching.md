# 一般グラフの最大マッチング

## 主な機能

奇数cycleを含んでよい無向グラフで、互いに端点を共有しない辺を最大本数選びます。blossomを縮約するため、二部グラフでない場合にも使えます。

構築時に最大マッチングまで計算し、`matching_size`、`mate`、`pairs()`から結果を取得できます。

## 使い方

```python
from library_codex.graph_matching.GeneralMatching import GeneralMatching

graph = [
    [1, 2],
    [0, 2],
    [0, 1, 3],
    [2],
]

matching = GeneralMatching(graph)
size = matching.matching_size
edges = matching.pairs()
```

- `size`: 最大マッチングの辺数。
- `edges`: 選ばれた無向辺`(first, second)`の列。各組は`first < second`。
- `mate[v]`: 頂点$v$とマッチした頂点。マッチされていなければ-1。

## 必ずマッチされる頂点

```python
essential = matching.essential_vertices()
```

`essential[v]`は、頂点$v$がすべての最大マッチングで必ず何らかの辺とマッチされる場合だけ`True`です。現在選ばれている相手と常に組になる、という意味ではありません。

## 計算量

- 構築: $O(VE)$
- `pairs()`: $O(V)$
- `essential_vertices()`: $O(VE)$
