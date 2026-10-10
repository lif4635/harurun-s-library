# st-numbering

無向グラフの頂点に順位を付け、各頂点を含むsからtへの有向パスが存在するようにする。

## 主な機能

`st_numbering(graph, source, target)` は、始点の順位を0、終点の順位をN-1にする。それ以外の各頂点には、順位が小さい隣接先と大きい隣接先が少なくとも一つずつ存在する。辺を順位の小さい側から大きい側へ向ければ、閉路のない有向グラフになる。

条件を満たす順位列がなければ `None`。隣接listまたは無向 `CSRGraph` を受け取り、`O(N+M)` 時間・追加メモリで求める。

## 使い方

```python
from library_codex.graph_connectivity.STNumbering import st_numbering

graph = [[1], [0, 2], [1, 3], [2]]
rank = st_numbering(graph, 0, 3)
assert rank == [0, 1, 2, 3]
assert st_numbering(graph, 0, 2) is None
```

終点を2にすると、頂点3を経由して2へ進むために同じ辺を逆に戻る必要がある。そのため、すべての頂点がs-tパスに乗る向き付けは作れない。

返り値は「順位順の頂点番号」ではなく `rank[v]` が頂点vの順位になる配列。順位順に読むなら `sorted(range(len(graph)), key=rank.__getitem__)` とする。

## 注意点

- 各頂点を含むパスは別々でよい。全頂点を一度ずつ通る一本のパスを求める機能ではない。
- sとtの間に辺がなくてもよい。二重連結グラフに限らず、パスなどでも指定したsとtに対して成立することがある。
- 隣接listは対称な無向グラフを渡す。多重辺・自己辺は可。入力は変更しない。
- 頂点が一つなら `[0]`。二つ以上でs=tなら `None`。
