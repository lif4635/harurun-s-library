# 指定頂点だけを結ぶ Auxiliary Tree

## 主な機能

大きな木から、指定した頂点集合と、それらを結ぶために必要なLCAだけを抜き出した小さな木を作ります。Virtual Treeとも呼ばれる構造です。

指定頂点数を $K$ とすると、圧縮後の頂点数は高々 $2K-1$ です。同じ元の木に対してqueryを繰り返せます。前処理後、一回の構築は $O(K\log K)$ と $O(K)$ 回のLCA queryです。

## 使い方

```python
from library_codex.tree.AuxiliaryTree import AuxiliaryTree

tree = [[1, 2], [0, 3, 4], [0], [1], [1]]
builder = AuxiliaryTree(tree)
auxiliary, original_vertices = builder.get([2, 3, 4])
```

## 返り値

- `original_vertices[i]`: 圧縮木の頂点`i`に対応する、元の木の頂点番号。
- `auxiliary[i]`: 圧縮木で`i`の子になる頂点番号のlist。
- 圧縮木の辺`i -> j`: 元の木では`original_vertices[i]`が`original_vertices[j]`の祖先になる。
- `with_distance=True`の場合: `auxiliary[i]`の要素が`(j, distance)`になり、`distance`は元の二頂点間で通る辺の本数を表す。

## 注意点

- `auxiliary`内の頂点番号は、元の木の頂点番号ではありません。元へ戻すときは`original_vertices`を使います。
- 入力した頂点の重複は一つにまとめられます。
- 空入力では`([], [])`を返します。
