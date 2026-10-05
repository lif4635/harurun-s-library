# 三辺連結成分と辺追加時の強連結成分

無向グラフで辺を切ってもつながる頂点のまとまりと、有向グラフで辺を追加したときに合流する強連結成分を求めます。

## 主な機能

- `ThreeEdgeConnectedComponents(n, edges)` は無向グラフを分解するclassです。任意の2辺を取り除いても互いに到達できる頂点を同じ三辺連結成分にまとめます。二辺連結成分も同時に求めます。時間・領域は O(N+M)。
- `incremental_scc_offline(n, edges)` は有向辺を順番に追加したときの強連結成分の合流を求めるfunctionです。すべての追加辺を事前に渡します。時間は O((N+M) log(M+2))、追加領域は O(N+M)。

## 使い方

無向グラフの成分を調べる例です。

```python
from library_codex.graph_connectivity.AdvancedConnectivity import ThreeEdgeConnectedComponents

tree = ThreeEdgeConnectedComponents(3, [(0, 1), (0, 1), (0, 1), (1, 2)])
same = tree[0] == tree[1]
group = tree.groups[tree[0]]
```

- `same = True`: 頂点0と1は三辺連結です。
- `group = [0, 1]`: 頂点0が属する三辺連結成分の頂点一覧です。
- `groups2` と `component2`: 二辺連結成分の頂点一覧と、各頂点の成分番号です。

有向辺の追加に合わせて、Union-Findで強連結成分を管理する例です。

```python
from library_codex.graph_connectivity.AdvancedConnectivity import incremental_scc_offline
from library_codex.union_find.UnionFind import UnionFind

edges = [(0, 1), (1, 0), (1, 2), (2, 0)]
events = incremental_scc_offline(3, edges)
uf = UnionFind(3)
sizes = []
for bucket in events:
    for edge_id in bucket:
        uf.merge(*edges[edge_id])
    sizes.append(uf.size(0))
```

- `sizes = [1, 2, 2, 3]`: 各辺を追加した直後、頂点0と同じ強連結成分にいる頂点数です。
- `events[t]`: 時刻tで併合するための元の辺番号のlistです。頂点番号や成分一覧ではありません。空listなら新しい併合はありません。
- 同じ元の辺番号を複数回返すことはありません。N頂点が1個以上なら、全bucketを合わせた併合回数は高々 N−1 回です。

## 注意点

- 無向グラフの辺は両方向を登録せず、1本につき `(u, v)` を1個渡します。多重辺・自己ループを扱えます。
- 三辺連結と二重頂点連結は別の条件です。頂点を除いたときの連結性は `BiconnectedComponents` を使います。
- 辺追加SCCは追加予定がすべて分かる場合に使います。処理途中に未知の辺を渡すオンライン構造ではありません。
- 成分番号や併合に選ぶ辺の順序には依存しないでください。
