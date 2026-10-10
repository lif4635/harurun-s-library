# 木幅2以下の木分解

グラフを、最大3頂点ずつの小さな集合に分け、その集合同士を木でつなぐ。

## 主な機能

`tree_decomposition_width2(n, edges)` は、無向グラフの木幅が2以下なら木分解を返す。木幅が3以上なら `None`。頂点数N・入力辺数Mに対して期待 `O(N+M)` 時間・メモリ。

辺の両端は必ずどこか一つの集合に入り、同じ頂点を含む集合は木の上でつながっている。この性質を使い、独立集合や彩色などのDPを、各集合の高々3頂点の状態で進められる。DPそのものはこの関数には含まない。

## 使い方

```python
from library_codex.graph_connectivity.TreeDecompositionWidth2 import tree_decomposition_width2

edges = [(0, 1), (1, 2), (2, 0), (2, 3)]
bags, parent = tree_decomposition_width2(4, edges)
assert len(bags) == len(parent) == 4
assert all(len(bag) <= 3 for bag in bags)
tree_edges = [(i, p) for i, p in enumerate(parent) if p >= 0]
assert len(tree_edges) == 3
```

- `bags[i]`: 木分解の頂点iが持つ、元の頂点番号のlist。各listの長さは1〜3。
- `parent[i]`: 木分解側の親番号。元のグラフの頂点番号ではない。最後の集合が根で、その値は `-1`。
- 根以外は必ず `i < parent[i]`。子の結果を親へ渡すDPは、iを小さい順に処理できる。

## 仕組み

次数が2以下の頂点を順に取り除く。隣接先が2個なら、それらの間に辺を補う。最後まで取り除ければ、そのときの頂点と隣接先が各集合になる。途中で次数3以上の頂点しか残らなければ、木幅は3以上。

## 注意点

- 平行辺は一本へまとめ、自己辺は無視する。入力は変更しない。
- 非連結でも使える。成分ごとの分解をつなぎ、一つの木にする。
- 孤立頂点も一つの集合へ含める。N=0は `([], [])`。
- 木幅0・1を最小化して返すAPIではない。保証するのは幅2以下の分解。
