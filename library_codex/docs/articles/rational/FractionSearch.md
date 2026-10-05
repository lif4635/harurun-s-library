# 上限付きの分数近似と境界探索

## 主な機能

分子・分母がどちらも`limit`以下の正の既約分数から、条件の境界を挟む2つを求める。

- `rational_bounds(numerator, denominator, limit)`は、指定した有理数以下で最大の分数と、以上で最小の分数を返す。整数演算を定数時間として`O(log(max(numerator, denominator)+1))`時間、追加領域`O(1)`。
- `stern_brocot_binary_search(predicate, limit)`は、分数が増えると`False`から`True`へ変わる条件の境界を探す。判定1回を`T`として`O((T+1) log(limit+2))`時間。

分数そのものが分かっている場合は`rational_bounds`を使う。比較関数の呼び出しや、同じ方向への移動量を二分探索する処理を省ける。

## 使い方

```python
from library_codex.rational.FractionSearch import rational_bounds, stern_brocot_binary_search

lower, upper = rational_bounds(7, 5, 4)
assert (lower, upper) == ((4, 3), (3, 2))

lower, upper = rational_bounds(14, 21, 3)
assert lower == upper == (2, 3)

lower, upper = stern_brocot_binary_search(lambda f: f[0] ** 2 >= 2 * f[1] ** 2, 4)
assert (lower, upper) == ((4, 3), (3, 2))
```

- `lower`: 下側の分数。`(分子, 分母)`のtuple。
- `upper`: 上側の分数。同じ形式。
- 候補に下側が存在しなければ`(0, 1)`、上側が存在しなければ`(1, 0)`を返す。後者は正の無限大を表す。

## 注意点

- `rational_bounds`の対象は正の有理数。分子・分母・`limit`はすべて1以上。
- 対象の既約分数が上限内なら、`rational_bounds`は上下に同じ分数を返す。
- `predicate`は`(分子, 分母)`を受け取る。境界と等しい値を`True`にするかは利用側で決める。
- `stern_brocot_binary_search`で`predicate((0, 1))`が`True`なら上下とも`(0, 1)`。`limit=0`なら判定を呼ばず`((0, 1), (1, 0))`を返す。
