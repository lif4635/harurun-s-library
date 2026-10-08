# すべてのクリークを列挙する

選んだどの2頂点間にも辺がある頂点集合を、重複なくすべて取り出す。極大クリークだけでなく、その部分集合もそれぞれ列挙する。

## 主な機能

- `enumerate_cliques(graph, callback=None, include_empty=False)` — 隣接listから列挙するfunction。
- callbackを省略すると全結果をlistで返す。指定すると一つずつcallbackへ渡し、最後に列挙数を返す。
- 列挙数自体が指数的に大きくなる場合がある。完全グラフでは空でないクリークが2^N-1個ある。

## 使い方

```python
from library_codex.graph_enumeration.EnumerateCliques import enumerate_cliques

graph = [[1], [0, 2], [1]]
assert sorted(enumerate_cliques(graph)) == [[0], [0, 1], [1], [1, 2], [2]]
sizes = []
assert enumerate_cliques(graph, lambda vertices: sizes.append(len(vertices))) == 5
assert sum(sizes) == 7
```

- 各結果は昇順の頂点番号list。クリーク同士の列挙順は保証しない。
- include_empty=Trueなら空listも一度渡す。
- callbackでは渡された頂点listを保存・変更してよい。別の列挙結果とは共有しない。

## 注意点

- 時間は列挙する頂点数とcallbackの処理量に依存する。結果を保存しない場合でも、列挙そのものの時間は必要。
- 大きな頂点番号を含むとbit集合も大きくなる。巨大な疎グラフ向けの局所番号圧縮は行っていない。
