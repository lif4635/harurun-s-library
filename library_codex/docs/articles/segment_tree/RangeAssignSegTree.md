# 区間代入と区間積

配列の指定区間を同じ値で上書きしながら、区間和・最小値・関数合成などを求める。

## 主な機能

- `RangeAssignSegTree(op, identity, values)` — 集計の演算だけを指定する区間代入用のclass。LazySegTreeのmapping・composition・idは不要。
- `assign(left, right, value)` — 半開区間[left,right)の全要素をvalueにする。
- `prod(left, right)` — 現在の要素を左から右へopでまとめる。opは可換でなくてもよい。
- `set`・`add`・`get` — 一点の上書き、opによる更新、現在値の取得。

opがO(1)なら構築O(N)、区間代入・区間積はO(log N)。同じ値を何個並べたときの積も内部で計算するため、区間長に比例する代入処理は行わない。

## 使い方

```python
from library_codex.segment_tree.RangeAssignSegTree import RangeAssignSegTree

tree = RangeAssignSegTree(lambda a, b: a + b, 0, [1, 2, 3, 4])
tree.assign(1, 4, 7)
tree.add(0, 5)
assert tree.prod(0, 3) == 20
assert tree.all_prod() == 27
assert tree.tolist() == [6, 7, 7, 7]
```

- prodはopで集計した値を一つ返す。空区間ならidentity。
- getは指定位置の要素、tolistは現在の全要素をindex順に並べた浅いコピー。
- strは同じlistを表示し、reprは`RangeAssignSegTree([...])`の形になる。

## 関数合成にも使う

一次関数を係数(a,b)で表す場合、左の関数の後に右の関数を適用する演算は次のように書ける。

```python
from library_codex.segment_tree.RangeAssignSegTree import RangeAssignSegTree

def op(left, right):
    a, b = left
    c, d = right
    return a * c, b * c + d

tree = RangeAssignSegTree(op, (1, 0), 3)
tree.assign(0, 3, (2, 1))
assert tree.prod(0, 3) == (8, 7)
tree.set(1, (1, 5))
assert tree.prod(0, 3) == (4, 13)
```

返り値(8,7)は、2x+1を3回合成した関数8x+7の係数。傾きが0・1でも扱え、割り算や逆元は必要ない。modを使う場合はopの中で係数を剰余へ戻す。

## 仕組み

一回の代入につき、同じ値1個・2個・4個、と繰り返し二乗で積を作る。各段は「その積」と「半分の長さの段」への参照だけを保持する。子へ代入を下ろすときは半分の段を参照するだけなので、opを計算し直さない。

過去の全更新の表は保持しない。高さhのnodeが保持する段数はh+1以下で、全nodeについて足してもO(N)。値そのものの大きさを除き、保持する値・参照の個数はO(N)。配列要素ごとのnode classや再帰は使わない。

## 注意点

- 代入以外の区間加算・affine変換なども必要ならLazySegTreeを使う。
- opは結合的で、引数の値を破壊しないこと。可変objectを格納した場合、取得したobjectの内部を書き換えると集計を壊すため、変更はset・assignで行う。
- addは`op(value, current)`。非可換な場合は順番に注意する。
- opがO(T)なら代入と区間積はO(T log N)。長い文字列や巨大整数を扱う場合、その演算・保持コストも含める。
- Noneも通常の値として扱える。空区間の代入は何も変更しない。
