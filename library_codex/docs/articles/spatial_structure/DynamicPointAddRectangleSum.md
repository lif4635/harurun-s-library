# 点加算と長方形和をまとめて処理

点への加算と長方形和の問い合わせを登録し、操作順を保って答えをまとめて求める。

## 主な機能

`add`と`query`を実際の操作順に呼び、最後に`solve()`を呼ぶ。各問い合わせに反映されるのは、その`query`より前に登録した加算だけ。

点加算数をU、問い合わせ数をQとして、登録は1回償却O(1)、`solve`はO((U+Q) log²(U+2))時間、O(U log(U+2)+Q)追加メモリ。

## 使い方

```python
from library_codex.spatial_structure.DynamicPointAddRectangleSum import DynamicPointAddRectangleSum

solver = DynamicPointAddRectangleSum()
solver.add(1, 2, 7)
solver.query(0, 0, 3, 3)
solver.add(1, 2, -2)
solver.query(0, 0, 3, 3)
assert solver.solve() == [7, 5]
```

- `solve()`の返り値: `query`の登録順に長方形和を並べたlist。`add`に対応する要素は含まない。
- 問い合わせの領域: 半開領域 `[left, right) × [bottom, top)`。

## 注意点

- 座標・加算値は整数。負値も使える。
- `solve`を繰り返しても操作列は消えない。新しい操作を追加して再計算もできる。
- 即座に問い合わせへ答えたい場合は、更新点を事前登録する`CompressedFenwick2D`を使う。
