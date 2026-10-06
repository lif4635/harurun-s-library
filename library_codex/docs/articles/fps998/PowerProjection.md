# 多項式の冪から係数をまとめて取り出す

同じ多項式の0乗、1乗、2乗……について、指定した係数の重み付き和をまとめて求める。係数の法は998244353。

## 主な機能

- `power_projection(f, weights, count)` — fの各冪の係数にweightsを掛けて足す。
- `power_coefficient(f, multiplier=None, count=None)` — fの各冪にmultiplierを掛け、次数`len(f)-1`の係数だけを取り出す。
- Nを入力配列の長さと出力個数の最大値として `O(N log²(N+1))`。各冪を一つずつ展開する必要がない。

`power_projection`の返り値のi番目は次の値になる。

$$
\mathrm{result}[i]=\sum_{j=0}^{|\mathrm{weights}|-1}\mathrm{weights}[j]\,[x^j]f(x)^i.
$$

## 使い方

```python
from library_codex.fps998.PowerProjection import power_coefficient, power_projection

assert power_projection([0, 1, 1], [0, 0, 1], 4) == [0, 1, 1, 0]
assert power_coefficient([0, 1, 1], count=4) == [0, 1, 1, 0]
```

どちらも、f=x+x²の各冪におけるx²の係数を返す。

- 返り値: 長さcountの整数list。i番目はfのi乗に対応する。
- `multiplier`: 省略時は1。係数列を渡すと、各冪へその多項式を掛けてから係数を取り出す。
- `count`: `power_coefficient`では省略時に`len(f)`となる。

## 仕組み

冪ごとの係数を二変数の有理式で表し、xの次数を半分にする処理を繰り返す。偶数次・奇数次の取り出しをNTT後の配列上で行い、逆変換は半分の長さで済ませる。全段階で同じ長さの変換表を再利用し、次段階で不要になる係数の逆変換は省く。

## 注意点

- fの定数項は0でなくてもよい。
- 入力配列は変更しない。
- 必要なNTT長は重みの個数を2冪へ切り上げた値の4倍。NTT長が2²³を超える入力には対応しない。
