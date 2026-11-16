# 範囲内の一次不定方程式

## 主な機能

次を満たす整数の組を、全列挙せずに数えます。

$$ax+by=c,\qquad x_l\le x<x_r,\qquad y_l\le y<y_r.$$

`count` で個数、`kth(k)` でx、次にyの昇順でk番目の組を取得できます。係数や範囲は負でも構いません。整数演算をO(1)とすると構築はO(log(max(|a|, |b|)+2))、取得はO(1)、保持空間はO(1)です。

## 使い方

```python
from library_codex.number_theory.LinearDiophantine import LinearDiophantine

solutions = LinearDiophantine(2, 3, 12, 0, 7, 0, 5)
assert solutions.count == 3
assert solutions.kth(0) == (0, 4)
assert solutions.kth(1) == (3, 2)
assert solutions.kth(2) == (6, 0)
```

- `kth(k)` の返り値は `(x, y)` の2整数です。
- 解がなければ `count == 0` です。
- `a == b == c == 0` なら長方形内の全点が解です。巨大な個数でも点の配列は作りません。

## 注意点

- `xl, xr` と `yl, yr` はいずれも半開区間の端点です。
- `count` はPythonの整数です。巨大な解集合でも `len` の上限に制限されません。
- 範囲外の順位は `IndexError`、左右が逆転した範囲は `ValueError` になります。

## 参考

[qandori/cp-library: 一次不定方程式](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/math/linear_diophantine.hpp)の、半開区間と辞書順取得の仕様を参照しています。

