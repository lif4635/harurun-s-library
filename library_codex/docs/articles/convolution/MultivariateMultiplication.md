# 次数を打ち切る多変数多項式の積

## 主な機能

多変数多項式を掛け、指定した次数範囲だけを返す。2変数でbase=(W,H)なら、xの次数W未満・yの次数H未満の項を残す。上限を超えた項は捨て、低い次数へ循環させない。

係数は平坦なlistで与える。位置i+W*jがxのi乗・yのj乗の係数。2変数では係数数N=W*Hに対してO(N log(N+1))時間、O(N)追加領域で求める。998244353では専用の畳み込みを使う。

## 使い方

```python
from library_codex.convolution.MultivariateMultiplication import multivariate_multiplication

first = [1, 1, 1, 0]
second = [1, -1, 1, 0]
result = multivariate_multiplication(first, second, base=(2, 2))
assert result == [1, 0, 2, 0]
```

これは(1+x+y)(1-x+y)の積からxの2乗・yの2乗の項を捨て、1+2yだけを残したもの。

- `result`: 入力と同じ長さの新しい係数list。firstとsecondは変更しない。
- 配置: `[定数項, xの係数, yの係数, xyの係数]`。
- 逆数・log・expなども使う場合: 同じ係数の並びを使う`fps/MultivariateFPS`のclassを利用する。

## 注意点

- 入力の長さは両方ともproduct(base)。異なる長さを直接渡すことはできない。
- 3変数以上でも先の変数の指数から順に増やす。例えばbase=(A,B,C)では位置i+A*j+A*B*kに係数を置く。
- 長さ1の軸を除いて3変数以上では、必要な長さのNTTが使える法が必要。2変数で他の法を指定すると汎用畳み込みを使い、CRTの復元範囲を超える場合はOverflowErrorになる。
- 打ち切らない2変数の積には`fps998/NTT2D.multiply2d`がある。こちらは二重listを受け取り、行数・列数ともに入力サイズの和から1を引いた大きさで返す。
