# 木の重心分解と距離query

## 主な機能

- `tree_centroid(tree)` — 木全体の重心を求めるfunction。重心の頂点番号を並べたlistを返す。
- `CentroidDecomposition(tree)` — 高さ$O(\log N)$の重心分解木を構築するclass。`parent`・`depth`・`children`・`ancestors(v)`から分解結果を読む。
- `CentroidDistanceFenwick(tree, values)` — 点更新と距離区間和を処理するclass。内部に重心分解を持ち、指定頂点からの距離が半開区間$[l,r)$に入る頂点の値を合計する。

## 重心分解木の使い方

```python
from library_codex.tree.CentroidDecomposition import CentroidDecomposition

tree = [[1], [0, 2, 3], [1], [1, 4], [3]]
decomposition = CentroidDecomposition(tree)

assert decomposition.root == 1
assert decomposition.parent[4] == 3
assert decomposition.ancestors(4) == [(1, 2, 2), (3, 1, 0), (4, 0, -1)]
```

`ancestors(4)`のtupleは順に`(重心祖先, 元の木での距離, 枝番号)`です。先頭が重心分解木のroot側、末尾が頂点自身です。

## 距離queryの使い方

```python
from library_codex.tree.CentroidDecomposition import CentroidDistanceFenwick

tree = [[1], [0, 2, 3], [1], [1, 4], [3]]
values = [10, 20, 30, 40, 50]
query = CentroidDistanceFenwick(tree, values)

# 頂点1からの距離が1以上3未満の頂点: 0, 2, 3, 4
assert query.query(1, 1, 3) == 130

query.add(4, 5)
query.set(0, 0)
assert query.query(1) == 145
```

### 操作と返り値

- `query(vertex, l, r)`: `vertex`からの距離が半開区間$[l,r)$に入る頂点の値の合計。
- `query(vertex)`: 距離に上限を設けず、木全体の値の合計。
- `add(vertex, delta)`: `vertex`の現在値へ`delta`を加える。
- `set(vertex, value)`: `vertex`の値を`value`へ置き換える。

## 重心分解木の情報

- `parent[c]`: 重心分解木で重心`c`の親。
- `depth[c]`: 重心分解木での`c`の深さ。
- `ancestors(v)`: 元の頂点`v`から見た重心祖先を`(centroid, distance, branch)`の順に並べたlist。
  - `centroid`: 重心祖先の元の頂点番号。
  - `distance`: 元の木での`v`と`centroid`の距離。
  - `branch`: `centroid`を除いたときに`v`が入る隣接成分の番号。`v == centroid`だけ`-1`。

`branch`は、距離queryで同じ枝を二重に数えないために使われます。

## 計算量

重心分解の構築は $O(N\log N)$、`CentroidDistanceFenwick`の一点更新と距離区間和は $O(\log^2 N)$ です。
