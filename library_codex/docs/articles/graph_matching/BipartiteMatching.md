# 二部グラフの最大マッチング

## 主な機能

二部グラフで、互いに端点を共有しない辺を最大本数選びます。無向隣接リストをそのまま渡せば二部彩色は自動で行い、結果も元の頂点番号で取得できます。左右の頂点数を自分で指定することもできます。

最大マッチングに加え、最小頂点被覆、最大独立集合、最小辺被覆、DM分解、辺と頂点の必須性を取得できます。

## 使い方

```python
from library_codex.graph_matching.BipartiteMatching import BipartiteMatching

graph = [[1, 3], [0, 2], [1], [0]]
matching = BipartiteMatching(graph)
size = matching.solve()
edges = matching.pairs()
mate = matching.mates()
required = matching.essential_vertices()
cover = matching.minimum_vertex_cover()
```

- `size`: 選べる辺数。この例では2。
- `edges`: 元の頂点番号で表したペアのリスト。この例では`[(0, 3), (2, 1)]`。
- `mate[v]`: 頂点`v`の相手。未マッチは-1。この例では`[3, 2, 1, 0]`。
- `required[v]`: 頂点`v`がどの最大マッチングでも必ずマッチされるか。
- `cover`: 最小頂点被覆に含まれる元の頂点番号の昇順リスト。

グリッドで上下左右の隣接関係を作る例です。壁以外のマスを`row * width + col`のまま扱えます。

```python
grid = ["...", ".#."]
height, width = len(grid), len(grid[0])
graph = [[] for _ in range(height * width)]
for row in range(height):
    for col in range(width):
        if grid[row][col] == "#":
            continue
        u = row * width + col
        for dr, dc in ((1, 0), (0, 1)):
            r, c = row + dr, col + dc
            if r < height and c < width and grid[r][c] != "#":
                v = r * width + c
                graph[u].append(v)
                graph[v].append(u)

matching = BipartiteMatching(graph)
cells = [(divmod(u, width), divmod(v, width)) for u, v in matching.pairs()]
```

- `cells`: 選ばれた隣接マスのペア。各マスは`(row, col)`。
- 壁は孤立頂点として残るので、マッチングの辺数には影響しない。最大独立集合には壁も入るため、その結果を使う場合は壁を除く。最小辺被覆は壁があれば`None`になる。

## 左右を自分で指定する場合

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

- 上のように左右の頂点数を指定した場合は二つのリストを返す。隣接リストを渡した場合は`required[v]`の一つのリストになる。
- `left_flags[left]`: 左頂点`left`が、どの最大マッチングでも必ず何らかの辺に使われるか。
- `right_flags[right]`: 右頂点`right`が、どの最大マッチングでも必ず何らかの辺に使われるか。
- 必ず使われる辺を調べる`essential_edges()`とは異なり、相手が変わっても頂点が常にマッチされるなら`True`になる。

## allowed_verticesがない理由

「少なくとも一つの最大マッチングでマッチされる頂点」は、孤立頂点でないすべての頂点です。最大マッチングで頂点$v$が未マッチなら、その隣接頂点$u$は必ず別の頂点とマッチされています。その辺を$(u,v)$へ交換すれば、大きさを変えずに$v$をマッチできます。

したがって無向隣接リスト`graph`の頂点`v`については`bool(graph[v])`だけで判定できます。

## 注意点

- 入力の隣接リストには各辺を両端へ入れる。入力自体は変更しない。
- 奇閉路・自己ループがあるグラフは`ValueError`。斜めの移動や上下左右以外の辺を足したグリッドは、二部グラフでなくなる場合がある。
- 自動彩色後の`add_edge(u, v)`も元の頂点番号で指定する。同色の頂点同士を結ぶ場合は全体を彩色し直し、保持していたマッチングを再計算前の状態に戻す。二部性を壊す追加は`ValueError`となり、追加前の状態を保つ。
- `graph`・`match_left`・`match_right`属性は内部の左右別の番号を使う。自動彩色した場合の結果は`pairs()`・`mates()`などから取得する。

## 計算量

- 隣接リストからの構築: $O(V+E)$。番号の対応に追加で$O(V)$領域を使う。
- `solve()`: $O((V+E)\sqrt{V})$。$V=L+R$。孤立頂点がなければ$O(E\sqrt{V})$。
- `add_edge()`: 通常$O(1)$。自動彩色で同色の二頂点を結ぶ場合は再構築に$O(V+E)$。
- `essential_vertices()`: 最大マッチング計算後は $O(L+R+E)$
