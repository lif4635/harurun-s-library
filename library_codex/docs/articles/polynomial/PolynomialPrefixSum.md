# 多項式の累積和を表す多項式

整数点での値を足し上げる操作を、多項式の係数に対して行う。

## 主な機能

`polynomial_prefix_sum(f)`は次を満たすgの係数を返す。

$$
g(n)=\sum_{i=0}^{n-1}f(i).
$$

gを一度作れば、その後は必要なnで評価できる。入力長Nに対し、998244353では `O(N log N)` で構築する。

## 使い方

```python
from library_codex.polynomial.PolynomialPrefixSum import polynomial_prefix_sum
from library_codex.fps.FormalPowerSeries import fps_evaluate

g = polynomial_prefix_sum([0, 1])
assert fps_evaluate(g, 10) == 45
inclusive = polynomial_prefix_sum([0, 1], inclusive=True)
assert fps_evaluate(inclusive, 10) == 55
```

- 入力 `[0, 1]`: f(x)=xの係数列。
- `g`: 0からn-1までの整数の和を表す多項式。返り値は値ではなく、定数項から順の係数列。
- `inclusive=True`: 末尾のf(n)も足す。積分ではなく整数点の和。

## 仕組み

Bernoulli数の指数型母関数をFPS逆数で作り、逆順にした係数との畳み込みで累積和の係数をまとめて計算する。

## 注意点

- 法は素数で、fの次数+1より大きくする。省略時は998244353。
- 零多項式の返り値は `[]`。それ以外は長さdeg(f)+2。
- 入力末尾の0は次数に数えない。入力配列は変更しない。

## 参考

- [Library Checker公式解法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/polynomial/prefix_sum_of_polynomial/sol/correct.cpp)
