# 長方形への一括加算後の長方形和

初期値0の整数格子へ複数の長方形加算を行い、別の長方形内の値の合計を求める。

## 主な機能

`add`で長方形加算を、`query`で集計する長方形を登録する。`solve()`はすべての加算を反映した答えを返す。`solve(mod)`なら指定した法での剰余を返し、中間の係数も剰余にして計算する。

加算数をR、問い合わせ数をQとして、登録は1回償却O(1)、計算はO((R+Q) log(R+Q+2))時間・O(R+Q)追加メモリ。整数の演算・比較をO(1)としている。

## 使い方

```python
from library_codex.spatial_structure.RectangleAddRectangleSum import RectangleAddRectangleSum

solver = RectangleAddRectangleSum()
solver.add(0, 0, 3, 2, 5)
solver.add(1, 0, 2, 2, -1)
solver.query(0, 0, 3, 2)
solver.query(1, 0, 3, 1)
assert solver.solve() == [28, 9]
assert solver.solve(7) == [0, 2]
```

- `solve`の返り値: `query`の登録順のlist。`result[i]`はi番目の問い合わせ領域の格子点値の合計。
- 領域: 加算・問い合わせの両方とも半開領域 `[left, right) × [bottom, top)`。重なった幅×高さ×加算値を、各加算について足したものになる。

## 注意点

- **操作順は考慮しない。** `query`より後の`add`も、すべての問い合わせに反映される。
- 座標・加算値は整数。負値も使える。
- 幅または高さが0以下の長方形は空として扱う。
- `mod`は正の整数。省略時は剰余を取らず、任意精度整数で計算する。
- `solve`は登録内容を変更しない。
