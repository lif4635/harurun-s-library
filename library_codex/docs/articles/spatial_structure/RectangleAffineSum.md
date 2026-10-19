# 二次元点の矩形アフィン変換と矩形和

二次元点の重みを持ち、矩形内の重みへの一次変換と、矩形内の重みの和を処理する。点ごとの置換、有効化、無効化にも対応する。

## 主な機能

- 構築時に`(x, y, weight)`を登録する。同じ座標に複数の点を置ける。
- `apply`で矩形内の有効な重みを`a*weight+b`へ変更し、`sum`で矩形和を求める。
- `set(i, value)`で入力順のi番目の重みを置き換える。`None`は無効な点を表し、後から数値を設定すれば有効になる。
- 構築O(N log N)、点の取得・置換O(log N)、保持する整数O(N)。矩形操作は訪問する部分に依存し、最悪O(N)。通常の二次元KD-treeではO(sqrt N)程度が目安になるが、保証ではない。

矩形は左右・上下とも半開区間で、次の点が対象になる。

$$
\mathrm{left}\le x<\mathrm{right},\qquad
\mathrm{down}\le y<\mathrm{up}.
$$

## 使い方

```python
from library_codex.spatial_structure.RectangleAffineSum import RectangleAffineSum

points = RectangleAffineSum([(0, 0, 2), (1, 0, 3), (0, 1, None)])
points.apply(0, 2, 0, 2, 2, 1)
first = points.sum(0, 2, 0, 2)
points.set(2, 4)
second = points.sum(0, 1, 0, 2)
points.set(0, None)
weights = points.tolist()
```

- `first`は12。2と3をそれぞれ5と7へ変更した和。無効な点には何も加えない。
- `second`は9。右端のx=1を含まず、x=0の5と4だけを足す。
- `weights`は`[None, 7, 4]`。`None`は重み0とは異なり、加算や一次変換の対象にならない。
- `get(i)`は現在の重みの整数、無効なら`None`を返す。

計算は既定ではmod 998244353。別の法は構築時の`mod`へ渡せる。

## 点を後から追加する場合

追加予定の座標を最初から`weight=None`で登録し、追加する時点で`set`する。座標だけ先読みできれば、重みの更新と問い合わせはその後に与えられる順で処理できる。

- 追加前に行った矩形更新は、後から有効化した点に反映されない。
- 一度無効化した点を再び有効化すると、`set`で指定した新しい重みになる。
- 未登録の座標を処理途中で追加する操作はない。

## 仕組み

点群をKD-treeで分割し、各部分に重みの和、有効な点の数、保留中の一次変換を持つ。矩形が部分全体を含めば、個々の点を触らずに更新・集計する。

末端では少数の点を配列へまとめ、境界にかかる部分だけ点を直接調べる。片方の座標の種類が極端に少ない場合は、その座標で先に分ける。点やノードごとのclass instance、再帰、逆元計算は使わない。

## 注意点

- `apply(left, right, down, up, a, b)`と`sum(left, right, down, up)`は、xの両端を先に渡す。Library Checkerの入力順`left, down, right, up`とは異なる。
- 矩形の幅や高さが0なら更新は何もせず、和は0。左端が右端を超える場合などは`ValueError`。
- 重み・係数は負数でもよい。係数0や合成数の法でも動作する。
- `tolist()`と`str`は現在の重みを入力順で表示する。`repr`は座標・重み・法を型名付きで表示する。表示後も更新や問い合わせを続けられる。
- 任意の集約や作用を渡したい場合は`LazyKDTree`を使う。このmoduleは法付き一次変換と和に特化している。
