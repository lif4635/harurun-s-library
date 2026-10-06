# 多項式を法とする逆元と累乗

素数の法で係数を計算し、指定した多項式で割った余りとして逆元や累乗を求める。

## 主な機能

- `polynomial_inverse_mod(f, g)` — `f*h`を`g`で割った余りが1になる`h`を求める。fとgが互いに素でなければ`ZeroDivisionError`。
- `polynomial_pow_mod(f, k, g)` — fのk乗をgで割った余りを返す。負の指数にも対応する。
- 累乗では法多項式を反転した係数列の逆数を再利用する。入力の最大次数をL、法多項式の次数をN、多項式積の時間をM(N)とすると、非負指数では `O(M(L) + M(N) log(k+1))`。

## 使い方

```python
from library_codex.polynomial.PolynomialModularPower import polynomial_inverse_mod, polynomial_pow_mod

g = [1, 0, 1]
assert polynomial_pow_mod([0, 1], 4, g) == [1]
assert polynomial_inverse_mod([0, 1], g) == [0, 998244352]
```

法多項式が次の場合、xの2乗の余りは-1、4乗の余りは1になる。

$$
g(x)=x^2+1.
$$

- 返り値: 定数項から順に並ぶ剰余の係数列。次数はg未満。
- 零多項式: 空list `[]`。
- 係数の法: 省略時は998244353。`mod`を指定して別の素数でも使える。

## 注意点

- 法多項式gの次数は1以上。定数や零多項式では`ValueError`。
- ここでの逆元は、gで割った余りとしての逆元。xの次数で打ち切るFPS逆数とは条件が異なる。
- 入力配列は変更しない。
