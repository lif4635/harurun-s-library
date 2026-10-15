# Newton基底への変換

通常の多項式係数と、指定した点列で定まるNewton基底の係数を相互変換する。法は998244353。

## 主な機能

点列の先頭から順に因子を掛けた基底を使う。

$$
B_0(x)=1,\qquad B_i(x)=\prod_{j=0}^{i-1}(x-p_j).
$$

- `to_newton(polynomial, points)` は通常の昇べき順の係数から、各基底に掛かる係数を求める。
- `from_newton(coefficients, points)` は通常の係数へ戻す。
- どちらも長さNの列を受け取り、時間 O(N log² N)、追加メモリ O(N log N)。点の重複も扱える。

## 使い方

```python
from library_codex.polynomial.NewtonBasis998 import to_newton, from_newton

a = [2, 3, 1]
p = [1, 2, 99]
b = to_newton(a, p)
assert b == [6, 6, 1]
assert from_newton(b, p) == a
```

この例は次の等式を表す。

$$
2+3x+x^2=6+6(x-1)+(x-1)(x-2).
$$

- `a[i]`: 通常の多項式でのi次の係数。
- `b[i]`: 基底B_iに掛かる係数。点列の順番を変えると基底も変わる。
- 返る列の長さは入力と同じ。末尾の0も省かず、係数は0以上998244353未満。

## 注意点

- 2つの引数の長さを揃える。空の列どうしなら空の列を返す。
- `points`の最後の値は、返るN個の基底では使われない。
- 関数値を点列上で評価する処理ではない。`polynomial`には評価値ではなく通常の係数を渡す。

## 仕組み

因子の積を二分木にまとめ、逆数の計算を根で一度だけ行う。その後は必要な区間の畳み込みで係数を伝播させる。各節点で多項式除算をやり直すことはしない。

## 参考

[Library Checkerの公式解法](https://github.com/yosupo06/library-checker-problems/blob/master/polynomial/conversion_from_monomial_basis_to_newton_basis/sol/correct.cpp)
