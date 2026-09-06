# 木のパス・部分木を区間で扱う

## 主な機能

木の頂点をHLD順に並べ替え、segtreeなどで木の上の集計・更新を行うための区間を取得します。値の保持や加算自体はHLDの役割ではありません。

- 部分木は一つの半開区間として取得できます。
- パスは $O(\log N)$ 個の区間に分かれます。順序が必要な場合は、区間の並びと読む向きも取得できます。
- 頂点の値と辺の値を切り替えて扱えます。

## 使い方

```python
from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition

tree = [[1, 2], [0, 3, 4], [0], [1], [1]]
hld = HeavyLightDecomposition(tree)
values = [10, 20, 30, 40, 50]
ordered = [values[v] for v in hld.rev]
l, r = hld.subtree(1)
```

- `ordered`: HLD順に並べた値。この例では `[10, 20, 40, 50, 30]`。この配列でsegtreeを構築します。
- `l, r`: 部分木の半開区間 `[l, r)`。この例では `[1, 4)` で、頂点1・3・4を含みます。
- `hld.index(v)`: 頂点vの値を置く位置。元の頂点番号とは別です。

区間加算に設定した `LazySegTree` を `seg` とすると、部分木への加算は次のように書けます。

```python
l, r = hld.subtree(v)
seg.apply(l, r, delta)
```

区間を取る操作は $O(1)$、加算はLazySegTree側の $O(\log N)$ です。

## パスをたどる向き

- `path(u, v)`: 区間 `[l, r)` のリスト。区間の並びや向きを保証しないため、和・最小値・一括加算などに使います。
- `path_ordered(u, v)`: uからvへの順に並んだ `(l, r, reverse)` のリスト。`reverse=False` はlからr-1、`True`はr-1からlへ読む指定です。

この例の `path_ordered(3, 2)` は `[(0, 3, True), (4, 5, False)]`。頂点列に戻すと `[3, 1, 0, 2]` になります。非可換な集計では各区間の順方向・逆方向の集計を用意し、指定された向きの結果をリスト順に結合します。

## 辺を扱うとき

親pと子vを結ぶ辺の値は、`hld.index(v)` に置きます。根の位置には辺がないため、集計の単位元を置きます。

- `subtree(v, edge=True)`: 部分木内部の辺。区間は `[tin[v]+1, tout[v])` で、vと親を結ぶ辺は除きます。
- `path(u, v, edge=True)`: パス上の辺。LCAの位置を除くことで、パス外へつながる親辺を含めません。
- `path_ordered(u, v, edge=True)`: 辺をたどる順序も保ちます。`reverse=True` は子から親、`False`は親から子です。

向きによって異なる辺の値はHLDが自動変換するわけではありません。例えば方向別の行列を持つ場合は、それぞれの集計値を用意して使い分けます。

## 注意点

- 部分木・親子関係は構築時のrootを基準にします。
- 頂点パスは両端を含みます。u=vの辺パスと、葉の部分木の辺区間は空です。
- 区間の取得と、その区間に対する集計・更新は別の処理です。パスをsegtreeで集計すると、通常は合計 $O(\log^2 N)$ になります。
