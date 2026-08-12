# 指定頂点だけを結ぶ Auxiliary Tree

## 主な機能

大きな木から、指定した頂点集合と、それらを結ぶために必要なLCAだけを抜き出した小さな木を作ります。Virtual Treeとも呼ばれる構造です。

指定頂点数を $K$ とすると、圧縮後の頂点数は高々 $2K-1$ です。同じ元の木に対してqueryを繰り返せます。前処理後、一回の構築は $O(K\log K)$ と $O(K)$ 回のLCA queryです。

## 使い方

```python
from library_codex.tree.AuxiliaryTree import AuxiliaryTree

tree = [
    [1, 2],
    [0, 3, 4],
    [0],
    [1],
    [1],
]
builder = AuxiliaryTree(tree)
auxiliary, original_vertices = builder.get([2, 3, 4])
```

返り値`original_vertices[i]`は、圧縮木の頂点`i`が元の木のどの頂点かを表します。`auxiliary[i]`には、圧縮木で`i`の子になる頂点番号が入ります。つまり、圧縮木の辺`i -> j`を元の木へ戻すと、`original_vertices[i]`は`original_vertices[j]`の祖先です。

`with_distance=True`なら、`auxiliary[i]`の各要素は`(j, distance)`になります。`distance`は対応する元の二頂点間で通る辺の本数です。

## 注意点

返り値の頂点番号は元の木の番号ではありません。元の頂点へ戻すときは必ず`original_vertices`を使います。入力した頂点に重複があっても一つにまとめられ、空入力では`([], [])`を返します。

