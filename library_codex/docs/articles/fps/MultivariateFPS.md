# 2変数・多変数の形式的冪級数

## 主な機能

2種類の個数を同時に数える母関数などに使う。変数ごとの次数上限を指定し、和・積・逆数・log・exp・整数冪を計算できる。

`base=(W,H)`ならxの次数W未満、yの次数H未満の係数を保持する。積で範囲外になった項は捨てる。総次数による打ち切りではない。

$$
f(x,y)=\sum_{j=0}^{H-1}\sum_{i=0}^{W-1}\mathrm{coefficients}[i+Wj]x^iy^j,
\qquad \bmod (x^W,y^H).
$$

係数数N=W*Hに対し、2変数の積・逆数・log・expはO(N log(N+1))時間、O(N)追加領域。法998244353では専用の畳み込みを使う。入力の非零項が少ないときは、項数とサイズに応じて逆数・log・exp・定数項非0の冪をO(N*(K+1))の漸化式へ自動で切り替える。Kは非定数の非零項数。出力が密でも使える。

## 使い方

1/(1-x-y)のxとyの次数をそれぞれ2未満で求める。

```python
from library_codex.fps.MultivariateFPS import MultivariateFormalPowerSeries

f = MultivariateFormalPowerSeries([1, -1, -1, 0], base=(2, 2))
g = f.inverse()
assert g.coefficients == [1, 1, 1, 2]
assert g.get(1, 1) == 2
assert (f * g).coefficients == [1, 0, 0, 0]
assert f.logarithm().exponential().coefficients == f.coefficients

p = MultivariateFormalPowerSeries([0, 1, 1, 0], base=(2, 2))
assert p.power(2).coefficients == [0, 0, 0, 2]
```

- `g`: 逆数の係数を保持する別オブジェクト。元のfは変更しない。
- `g.coefficients`: `[定数項, xの係数, yの係数, xyの係数]`。ここでは1+x+y+2xy。
- `g.get(i,j)`: xのi乗・yのj乗の係数。
- `g.set(i,j,value)`: その係数だけを置き換える。

## 条件と打ち切り

- 逆数と負の冪では定数項が可逆であることが必要。998244353なら非0であればよい。
- logは定数項1、expは定数項0。積分・log・expには1からN−1までの逆元が必要で、998244353ならN<998244353で満たす。
- 正の整数冪は定数項0でも使える。x+yのような場合も扱う。0乗は定数1。
- 定数項0の冪は二分累乗を使うため、指数eに対してO(log(e+1))回の積が必要。定数項非0・998244353の大きな整数冪はlogとexpを使う。
- `/`は冪級数の除算。多項式の商と余りを求める操作ではない。
- 入力は平坦なlist。二重listは受け付けない。長さはproduct(base)と一致させる。
- `fps998/NTT2D.multiply2d`は二重listで打ち切らない積を返す別API。そちらのmatrix[i][j]に対応する係数は、このclassではcoefficients[i+W*j]に置く。
- 3変数以上も同じclassを使える。先に指定した変数の指数が先に増える順で係数を並べる。長さ1の軸を除いて3変数以上ある場合、乗算には必要な長さのNTTが使える法が必要。
- 他の法での2変数の積は汎用畳み込みを使う。CRTで復元できる係数範囲を超えるとOverflowErrorになる。

## derivativeとintegral

このclassの`derivative()`は普通の偏微分ではない。平坦化した位置kの係数をk倍する。2変数なら次の演算になる。

$$
D f=x\frac{\partial f}{\partial x}+Wy\frac{\partial f}{\partial y},
\qquad D(x^iy^j)=(i+Wj)x^iy^j.
$$

`integral()`は位置k>0の係数をkで割る。そのため`f.derivative().integral()`はfから定数項を取り除いたものになる。`integral()`自体は入力の定数項を変更しない。

## 仕組み

密な入力では、逆数とexpの計算精度を1,2,4,...と増やすNewton反復を使う。2変数の積は行間へ0を挟んで1変数の畳み込みへ変換し、xの次数の繰り上がりが次のyへ混ざらないようにする。

998244353の大きな2変数の逆数では、係数を2群に分けるNTTを使い、同じNewton更新内で変換済みの逆数を再利用する。小さい入力、1変数へ退化した形、他の法では従来の積を使う。

疎な冪g=f^eでは次の関係から、入力の非零項だけを走査して出力係数を順に求める。

$$
f\,Dg=e\,(Df)g.
$$

## 参考

- [Nyaanの多変数FPS](https://nyaannyaan.github.io/library/fps/multivariate-fps.hpp)
- [maspypyの疎な2変数冪](https://github.com/maspypy/library/blob/main/poly/2d/fps_pow_1_2d.hpp)
