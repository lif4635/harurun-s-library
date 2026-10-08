# 区間更新と区間積

配列の半開区間へまとめて作用を適用し、指定区間の和・最小値・関数合成などを求める。

## 主な機能

- `LazySegTree(op, identity, mapping, composition, id, values)` — 集計方法と更新方法を指定して構築するclass。
- `apply(left, right, action)` — 区間内の各要素へactionを適用する。
- `prod(left, right)` — 現在の区間積を左から右の順序で返す。
- `set`・`get`・`tolist` — 遅延中の更新も反映した要素を上書き・取得する。

op・mapping・compositionがO(1)なら、構築はO(N)、区間更新と区間積はO(log N)。

## 使い方

```python
from library_codex.segment_tree.LazySegTree import LazySegTree

tree = LazySegTree(
    lambda a, b: a + b, 0,
    lambda delta, total, length: total + delta * length,
    lambda new, old: new + old, 0,
    [1, 2, 3],
)
tree.apply(0, 2, 5)
assert tree.prod(0, 3) == 16
assert tree.tolist() == [6, 7, 3]
```

- op: 隣り合う集計値を、左・右の順にまとめる。
- mapping(action, value, length): 要素数lengthの区間にactionを適用した後の集計値。
- composition(new, old): oldの後にnewを適用する作用。引数の順番を逆にしない。
- id: 何も変更しない作用。集計値の単位元identityとは別物。

## 座標圧縮した区間への更新

巨大配列で更新と問い合わせの端点を先に集められるなら、隣り合う端点の間を一つの葉にする。ただし、mappingへ渡されるlengthは**元の座標幅ではなく葉の個数**。元の幅は集計値に含める。

```python
from library_codex.segment_tree.LazySegTree import LazySegTree

tree = LazySegTree(
    lambda a, b: (a[0] + b[0], a[1] + b[1]), (0, 0),
    lambda f, s, length: (f[0] * s[0] + f[1] * s[1], s[1]),
    lambda f, g: (f[0] * g[0], f[0] * g[1] + f[1]), (1, 0),
    [(0, 3), (0, 7)],
)
tree.apply(0, 2, (1, 5))
tree.apply(1, 2, (2, 1))
assert tree.prod(0, 2) == (92, 10)
assert tree.get(1) == (77, 7)
```

- 葉0は元の区間[0,3)、葉1は[3,10)を表す。
- 集計値の第1要素は元の配列の和、第2要素は元の座標幅。
- 最後の返り値(92,10)は、値5が3個、値11が7個ある区間の和と幅。
- getやtolistも、元の各点の値ではなく圧縮した葉の集計値を返す。

## 同じ一次関数で区間を上書きする場合

更新が代入だけなら、RangeAssignSegTreeへ合成演算を渡せばよい。mapping・compositionを別に定義する必要はない。

集計値を一次関数の係数(a,b)とし、opで右側の関数を後から合成する。上書き作用ではcomposition(new,old)はnewだけを返す。

長さLの区間へ同じ関数fを設定した後の集計値は、fのL回合成。単に係数をL倍するのではない。f、fの2回合成、4回合成、と繰り返し二乗した結果を更新ごとに再利用すると、各nodeで冪を計算し直す負担を減らせる。逆元を使う式に頼らなければ、傾き0・1でも同じ計算で扱える。

## 注意点

- mappingは区間をまとめてから適用しても、各部分へ適用してからopでまとめても同じ結果になること。
- affine更新`x -> a*x+b`では更新順が重要。加算だけのtestでは順序の誤りを検出できない。
- mappingなどが重い場合、その呼出しコストも計算量へ含める。
- tolistはO(N)で子へ更新を反映する。論理的な要素は変わらない。
