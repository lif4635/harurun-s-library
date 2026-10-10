# 長方形への加算と一点の取得

平面上の登録点へ長方形単位で加算し、各点の現在値を取得する。

## 主な機能

`RectangleAddPointGet(points)`へ、今後値を読みたい点の座標を渡す。初期値はすべて0。`add`は半開領域 `[left, right) × [bottom, top)` に含まれる登録点へ加算し、`get(x, y)`はその点の現在値を返す。

入力点数をP、異なる登録点数をNとして、構築はO(P+N log(N+1))時間・O(N log(N+1))メモリ、加算・取得はO(log²(N+1))時間。hash処理は期待時間。長方形の境界は事前登録しなくてよい。

## 使い方

```python
from library_codex.spatial_structure.RectangleAddPointGet import RectangleAddPointGet

tree = RectangleAddPointGet([(0, 0), (1, 1), (2, 1)])
tree.add(0, 0, 2, 2, 5)
tree.add(1, 1, 3, 2, -2)
assert tree.get(0, 0) == 5
assert tree.get(1, 1) == 3
assert tree.get(2, 1) == -2
assert tree.items() == [(0, 0, 5), (1, 1, 3), (2, 1, -2)]
```

- `get(x, y)`: その点を含む、これまでの長方形加算の合計。
- `items()`: `(x, y, 現在値)`を座標の辞書順で並べたlist。重複登録した点は一度だけ返す。

## 仕組み

疎な二次元BITで、点加算と長方形和の処理を入れ替える。長方形の四隅ではなく、値を読みたい点だけを保存するため、更新する長方形が多くても構造の大きさは増えない。

## 注意点

- 座標・加算値は整数。負値も使える。
- 右端と上端は含まない。幅または高さが0以下なら加算しない。
- 未登録の点を`get`すると`KeyError`。登録済みのxとyを組み替えただけの点も、登録していなければ取得できない。
- 問い合わせを先に読める問題では、取得する点だけ集めて構築してから操作順に処理する。
