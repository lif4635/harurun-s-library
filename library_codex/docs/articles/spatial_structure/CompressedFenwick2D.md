# 疎な二次元の点加算・長方形和

事前登録した平面上の点へ加算し、長方形内の点の重みの合計を求める。

## 主な機能

`CompressedFenwick2D(points)`へ、今後更新する点の座標を渡す。`add(x, y, value)`で一点へ加算し、`sum(left, bottom, right, top)`で半開領域 `[left, right) × [bottom, top)` 内の合計を返す。

入力点数をP、異なる登録点数をNとして、構築はO(P+N log(N+1))時間・O(N log(N+1))メモリ、更新・取得はO(log²(N+1))時間。hash処理は期待時間。長方形の境界は事前登録しなくてよい。

## 使い方

```python
from library_codex.spatial_structure.CompressedFenwick2D import CompressedFenwick2D

tree = CompressedFenwick2D([(0, 0), (3, 2)])
tree.add(0, 0, 7)
tree.add(3, 2, -2)
assert tree.sum(0, 0, 3, 3) == 7
assert tree.prefix_sum(4, 3) == 5
```

- `sum`: 指定長方形に含まれる登録点の現在値の合計。
- `prefix_sum(x, y)`: x座標がx未満、y座標がy未満の登録点の合計。

## 注意点

- 座標・重みは整数。負値も使える。
- 同じ座標の重複登録は一つにまとめ、初期値は0。
- 未登録の点への`add`は、状態を変えずに`KeyError`。登録済みのxとyの組合せでも、その点自体が未登録なら更新できない。
- 空または逆向きの長方形の合計は0。
