# 同じ指数の冪をまとめて計算

0から上限までの整数を、すべて同じ指数で累乗した列を作る。

## 主な機能

`power_table(limit, exponent, mod)`は次の列を返す。底ではなく指数を固定する。

$$
\mathrm{result}[i] = i^{\mathrm{exponent}} \bmod \mathrm{mod},\qquad 0\le i\le\mathrm{limit}.
$$

正の法では、素数の冪を計算し、合成数は因数の冪の積から求める。N=limitとして、時間は `O(N log log(N+2) + π(N) log(exponent+1))`、メモリは返り値を含め `O(N)`。π(N)はN以下の素数の個数。小さい入力・指数では各要素を直接計算する。

## 使い方

```python
from library_codex.algebra.PowerTable import power_table

assert power_table(5, 3) == [0, 1, 8, 27, 64, 125]
assert power_table(5, 3, 7) == [0, 1, 1, 6, 1, 6]
assert power_table(3, 0, 7) == [1, 1, 1, 1]
```

- 返り値は長さlimit+1の整数list。上限limit自身も含む。
- `mod=None`では剰余を取らず整数を返す。この場合は各要素を直接累乗するため、指数が大きいと値の桁数に応じて時間とメモリが増える。
- `mod`は素数でなくてもよい。`mod=1`なら全要素0。
- 0の0乗は1。limit・exponentが負なら`ValueError`。

## 多項式の標本値として使う

```python
from library_codex.polynomial.PolynomialExponentialSum import sum_polynomial_exponential

samples = power_table(3, 3, 998244353)
assert sum_polynomial_exponential(samples, 2, 4) == 250
```

この例のsamplesは、3次多項式の整数点0, 1, 2, 3での値。係数列ではない。
