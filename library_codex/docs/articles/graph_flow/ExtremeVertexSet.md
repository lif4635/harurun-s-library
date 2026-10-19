# 全域カットの候補をまとめる木

## 主な機能

非負重みの無向グラフから、全extreme setを部分木として含む二分木を作る。各部分木の葉が元グラフの頂点集合を表し、その集合の内外を結ぶ辺の重みも同時に得られる。

extreme setとは、その中のどの非空な真部分集合を選んでも、元の集合より境界重みが大きくなる集合のこと。

$$
\varnothing\ne T\subsetneq S
\quad\Longrightarrow\quad
\operatorname{boundary}(T)>\operatorname{boundary}(S).
$$

返る木には条件を満たさない候補も含まれる。条件を満たす集合だけを抽出する関数ではない。構築は `O(N(N+M) log(N+2))` 時間、追加メモリは `O(N+M)`。

中心の辺更新と全域最小カットを処理したい場合は、これを内部で使う `DynamicStarMinCut` を利用する。

## 使い方

```python
from library_codex.graph_flow.ExtremeVertexSet import extreme_vertex_tree

children, boundary = extreme_vertex_tree(2, [(0, 1, 5)])
```

- `children` は `[(), (), (0, 1)]`。葉0と1が元頂点、ノード2が両方を含む根。
- `boundary` は `[5, 5, 0]`。1頂点だけの側は重み5の辺を切り、元頂点すべての側は固定グラフの辺を切らない。
- どちらの配列も長さは `2*N-1`。根IDは `2*N-2`。
- 内部ノードの子IDは必ず親IDより小さい。小さいIDから処理すれば部分木の集計を計算できる。

## 注意点

- 葉は元頂点の番号をそのまま使う。ノードごとのobjectは作らない。
- 負の辺重みは使えない。多重辺は重みを合算し、自己ループは無視する。
- 非連結グラフと頂点1個も扱える。頂点0個は `ValueError`。
- これはGomory–Hu木ではない。2頂点間の最小カットを木の経路の最小辺から求める用途には使わない。

## 参考

- [Library Checkerの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/graph/global_minimum_cut_of_dynamic_star_augmented_graph/sol/correct.cpp)
