# 中心の辺重みを更新する全域最小カット

## 主な機能

元の無向グラフに新しい中心を1頂点加え、中心と各元頂点を結ぶ辺の重みだけを変更する。変更するたびに、グラフ全体を空でない2つの側へ分ける最小カットを求められる。

元頂点同士の辺は固定で、すべての重みは非負整数。特定の始点・終点を分離する最大流ではなく、分ける位置も自由な全域最小カットを扱う。

構築は `O(N(N+M) log(N+2))`、中心の辺1本の置換は `O(log²(N+2))`。構築後は最小重みを `O(1)`、カットの頂点集合を `O(N)` で取得できる。Nは中心を除く頂点数、Mは固定辺数。

## 使い方

```python
from library_codex.graph_flow.DynamicStarMinCut import DynamicStarMinCut

graph = DynamicStarMinCut(2, [(0, 1, 5)], [2, 3])
weight = graph.min_cut()
vertices = graph.cut()
updated = graph.set(0, 10)
after = graph.cut()
```

- `weight` は `5`。元頂点0と1をまとめて中心から切り離す。
- `vertices` は `[0, 1]`。中心を含まない側の元頂点番号を返す。
- `updated` は `8`。中心と0の辺を10へ置換した後、頂点1だけを切り離すのが最小になる。
- `after` は `[1]`。固定辺の重み5と、中心から1への重み3がカットを横切る。

`tolist()` は現在の中心の辺重みを元頂点順に返す。この例では `[10, 3]`。`str` と `repr` でも確認できる。

## 仕組み

中心を含まない側をSとすると、そのカットの重みは次になる。

$$
\operatorname{cut}(S)=\operatorname{boundary}_G(S)+\sum_{v\in S}a_v.
$$

固定グラフのextreme setを含む二分木を前計算し、部分木ごとのカット重みを保持する。中心の辺重みが非負なので、この候補のどれかが最適解になる。1頂点の重み変更は、対応する葉から根までの候補への加算に変換できる。

## 注意点

- 元頂点同士の辺を変更する場合は作り直す。任意の辺を高速更新する構造ではない。
- 元グラフは非連結でもよい。中心の辺重み0も許す。
- `set` は差分加算ではなく置換で、更新後の最小重みも返す。
- 同じ最小重みを実現する集合が複数ある場合、`cut()` はそのうち1つだけを返す。

## 参考

- [Library Checkerの問題と公式実装](https://github.com/yosupo06/library-checker-problems/tree/1814c4e5205517e368bb57a8d1127eb961cfeaae/graph/global_minimum_cut_of_dynamic_star_augmented_graph)
