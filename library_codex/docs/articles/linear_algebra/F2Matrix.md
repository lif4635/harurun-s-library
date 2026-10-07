# 0・1成分の行列

## 主な機能

`F2Matrix`は、行列積・階数・行列式・逆行列をmod 2で求めるclass。各行をPythonの整数1個で保持し、XORで行をまとめて加算する。

- `multiply`は通常のmod 2の積。密な入力では8列分をまとめた表を使い、疎な入力では1が立つ位置だけを処理する。
- `rank`は線形独立な行の本数、`inverse`は正方行列の逆行列を求める。大きい逆行列は8列ずつまとめて消去する。
- `solve(b)`は連立方程式Ax=bの解を一つと、自由に足せる零空間の基底を求める。解がなければNone。大きい行列は8列ずつまとめて消去する。
- `and_or_product`は、積をAND、和をORにした別の演算。到達可能性などを扱うときに使う。

N行N列なら、積・階数・逆行列の最悪計算量は次のとおり。

$$
O(N^3/w + N^2)
$$

wは多倍長整数の1桁のビット数であり、Pythonの整数演算を定数時間とは数えない。密な積の8ビット表は定数倍を減らすもので、このBig-Oは変わらない。

## 使い方

```python
from library_codex.linear_algebra.F2Matrix import F2Matrix

a = F2Matrix.from_lists([[1, 1], [0, 1]])
rank = a.rank()
b = a.inverse()
product = (a * b).to_lists()
```

- `rank`は2。
- `b`は逆行列。非可逆な行列では`None`になる。
- `product`は`[[1, 0], [0, 1]]`。

ビット列で直接作るなら`F2Matrix(2, 2, [0b11, 0b10])`も同じ行列になる。`rows[i]`の下位ビットから順に第0列、第1列を表すため、文字列`"01"`をそのまま`int(..., 2)`へ渡す場合とは左右が逆になる。

## 連立方程式

連立方程式は整数に詰めたビット列で扱う。

```python
from library_codex.linear_algebra.F2Matrix import F2Matrix

a = F2Matrix.from_lists([[1, 1, 0], [0, 1, 1]])
particular, kernel = a.solve([1, 0])
assert a.matvec(particular) == 1
assert kernel == [0b111]
assert a.matvec(particular ^ kernel[0]) == 1
```

- particular: 解を一つ表す整数。第jビットがxの第j成分。
- kernel: Ax=0を満たす独立なビット列のlist。各要素を任意にXORしてparticularへ加えると、ちょうど全解を得られる。
- kernelの長さ: 列数−rank。空なら解は一意。Noneは「解なし」で、空のkernelとは異なる。
- b: 行数と同じ長さの整数列、または第iビットが第i成分となる非負整数。返り値はどちらでも同じビット列形式。

N行M列のsolveは、基底の復元を含め `O((N+M) M ceil((M+1)/w))` 時間、`O((N+M) ceil((M+1)/w))` メモリが上界。解を全列挙する時間は含まない。

## 注意点

- `rank`・`multiply`・`inverse`・`solve`は元の行列を変更しない。
- `sweep`は自分の`rows`を簡約行階段形へ書き換える。
- `to_lists`は全成分を展開する。大きい行列の出力は`rows`の整数を直接文字列化すると、一成分ずつ取り出す負担を避けられる。
