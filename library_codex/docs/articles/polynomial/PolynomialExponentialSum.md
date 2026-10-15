# 多項式に等比重みを付けた和

多項式fの連続した標本値f(0), f(1), …, f(d)から、rのべき乗を重みとして付けた和を計算する。

## 主な機能

`sum_polynomial_exponential(values, r, count)`は、countが大きくても項を一つずつ足さずに有限和を求める。

$$
\sum_{i=0}^{\mathrm{count}-1} r^i f(i).
$$

`limit_sum_polynomial_exponential(values, r)`は、無限和の母関数を有理関数として評価する。

$$
F(z)=\sum_{i\ge0} f(i)z^i,\qquad F(r)\pmod p.
$$

標本数Nに対し、有限和は `O(N + log p + log(max(1, count)))`、無限和は `O(N + log p)`。係数の列から標本値を作る時間は含まない。

## 使い方

```python
from library_codex.polynomial.PolynomialExponentialSum import sum_polynomial_exponential, limit_sum_polynomial_exponential

samples = [0, 1]
assert sum_polynomial_exponential(samples, 2, 4) == 34
assert sum_polynomial_exponential(samples, 1, 4) == 6
assert limit_sum_polynomial_exponential(samples, 2) == 2
```

冪の和では、`power_table`で標本値をまとめて作れる。

```python
from library_codex.algebra.PowerTable import power_table

samples = power_table(3, 3, 998244353)
assert sum_polynomial_exponential(samples, 2, 4) == 250
```

- `samples = [0, 1]`: f(0)=0, f(1)=1なので、次数1以下という条件のもとでf(x)=xを表す。
- 有限和: 0+2+8+24=34。
- 無限和: F(z)=z/(1-z)²へz=2を代入した値。実数上で級数が収束するという意味ではない。
- 返り値: 法で割った余りを表す整数1個。

## 注意点

- `values`は係数列ではなく、整数点0, 1, …での値。
- `len(values)=N`ならfの次数はN未満。標本は1個以上。
- 有限和はr=0・1にも対応する。countが0以下なら0。
- 無限和ではrが法上で1になる場合は `ValueError`。
- 法はNより大きい素数。省略時は998244353。

## 仕組み

無限和の分母は次数dに対して次の形になる。

$$
(1-r)^{d+1}.
$$

分子を標本値の線形結合で求める。逆階乗を共有し、等比列や累積和の配列を無限和用に保持しない。有限和は定数項を除くと「多項式の値×等比重み」に分離でき、その多項式を連続した整数点から補間する。補間の左右の積も両方の配列を作らず、片側は走査中に計算する。

## 参考

- [Library Checkerの公式実装](https://github.com/yosupo06/library-checker-problems/blob/master/other/sum_of_exponential_times_polynomial/sol/correct.cpp)
- [Nyaanの等比重み付き多項式和](https://nyaannyaan.github.io/library/fps/sum-of-exponential-times-poly.hpp.html)
