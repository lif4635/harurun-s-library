# 多変数の循環畳み込み

各軸の指数を指定した長さで折り返しながら、多変数多項式を掛け合わせる。

## 主な機能

`multivariate_circular_convolution`は、指数の和が軸の長さ以上になった項を先頭側へ戻す。範囲外の項を捨てる`multivariate_multiplication`とは異なる。

`base=(2, 3)`なら、係数の並びは`[1, x, y, xy, y², xy²]`に対応する。次の関係で指数を折り返し、同じ6要素の並びで返す。

$$
x^2=1,\qquad y^3=1
$$

係数数をS、軸数をD、各軸の長さをbase[i]とすると、変換部分は`O(S * sum(log(base[i]+1)))`時間・`O(S+D)`領域。2点・3点の軸は直接計算し、それ以外はchirp-z変換を使う。法に応じた原始根の探索も初めに行う。

## 使い方

```python
from library_codex.convolution.MultidimensionalDFT import multivariate_circular_convolution

a = [1, 2, 3, 4, 5, 6]
x = [0, 1, 0, 0, 0, 0]
c = multivariate_circular_convolution(a, x, (2, 3), mod=7)
assert c == [2, 1, 4, 3, 6, 5]
```

xを掛けることで、各y次数の`[定数項, xの係数]`が入れ替わる。入力のlistは変更されない。

`multidimensional_dft`で変換値自体を取り出すこともできる。

```python
from library_codex.convolution.MultidimensionalDFT import multidimensional_dft

values = multidimensional_dft(a, (2, 3), mod=7)
assert multidimensional_dft(values, (2, 3), inverse=True, mod=7) == a
```

## 注意点

- `mod`は素数で、各軸の長さは`mod-1`の約数である必要がある。
- `base[0]`の指数が最も速く変わる。通常の多重listではなく、平坦な係数列を渡す。
- 軸がない`base=()`では、長さ1の係数列を渡す。
- 打ち切り畳み込みは`MultivariateMultiplication`を使う。循環版では範囲外の項が消えない。
