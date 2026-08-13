# 木の重心分解と距離query

## 主な機能

このmoduleには、目的の異なる三つの入口があります。

- `tree_centroid(tree)`: 一点を除いた各連結成分の大きさが元の木の半分以下になる頂点を求める。
- `CentroidDecomposition(tree)`: 重心を順に除いて得られる高さ $O(\log N)$ の重心分解木と、各元頂点から重心祖先への距離を構築する。
- `CentroidDistanceFenwick(tree, values)`: 各頂点の値を一点更新し、指定頂点からの距離が半開区間 $[l,r)$ に入る頂点の値を合計する。

単に木の重心だけが必要なら`tree_centroid`を使います。距離条件付きの更新・総和queryを処理したい場合は`CentroidDistanceFenwick`まで使います。

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
