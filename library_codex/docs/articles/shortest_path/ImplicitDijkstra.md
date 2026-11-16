# 辺をその場で作る最短路

## 主な機能

盤面の位置や「頂点・残り資源」の組を状態にし、到達した状態からの移動だけを生成して最短路を求めます。全状態の隣接listや、整数IDへの変換は不要です。

- `implicit_dijkstra(starts, adjacent)` は全到達状態の距離と経路復元用の親を返します。
- `implicit_shortest_path(starts, adjacent, finish)` は条件を満たす終点で終了し、距離と経路を返します。

発見状態数V、生成辺数E、始点数S、callbackの合計時間Gに対し、期待O(S+(V+E) log(V+E+2)+G)時間・O(V+E)空間です。整数IDと隣接listが既にある場合は通常の`Dijkstra`を使えます。

## 使い方

```python
from library_codex.shortest_path.ImplicitDijkstra import implicit_shortest_path

def adjacent(position):
    row, column = position
    if row < 2:
        yield (row + 1, column), 1
    if column < 2:
        yield (row, column + 1), 1

cost, path = implicit_shortest_path([(0, 0)], adjacent, lambda p: p == (2, 2))
assert cost == 4
assert path[0] == (0, 0) and path[-1] == (2, 2)
assert len(path) == 5
```

- `cost`: 最も近い始点からの距離。到達不能なら`float("inf")`です。
- `path`: 両端を含む状態list。到達不能なら空listです。
- 全探索版の`distance[state]`は最短距離、`previous[state]`は直前の状態です。始点は`previous`に含めません。

## 注意点

- 状態はhash可能である必要があります。tuple・文字列・`None`も使え、大小比較は不要です。
- 単一のtuple状態も`[(row, column)]`と始点列に入れます。
- 重みは非負、callbackは探索中に同じグラフを表す必要があります。調べた負辺はエラーにします。
- 全探索版は到達範囲が有限、早期終了版も終了までの探索が有限である必要があります。

## 参考

[kemuniku/cplibの暗黙Dijkstra](https://github.com/kemuniku/cplib/blob/f835598fec8e14039cf654a67f0244e0a654d035/src/cplib/utils/implicit_dijkstra.nim)の状態表現と終了条件を参照しています。
