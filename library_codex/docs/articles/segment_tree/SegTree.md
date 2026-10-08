# 一点変更と区間積

配列の一か所を変更しながら、指定した半開区間を左から順にまとめた値を求める。

## 主な機能

- `SegTree(op, identity, values)` — 結合的な演算opと単位元identityで構築するclass。構築はO(N)。
- `set(index, value)`・`get(index)` — 一点の上書き・取得。
- `prod(left, right)` — values[left:right]の積。空区間ではidentityを返す。O(log N)回のopを使う。
- `max_right`・`min_left` — 積に対する条件が満たされる最大の範囲を探す。

opは可換でなくてもよい。文字列連結や関数合成でも、左から右の順番を保つ。

## 使い方

```python
from library_codex.segment_tree.SegTree import SegTree

tree = SegTree(lambda a, b: a + b, "", ["a", "b", "c"])
tree.set(1, "X")
assert tree.prod(0, 3) == "aXc"
assert tree.prod(1, 1) == ""
assert tree.tolist() == ["a", "X", "c"]
```

- `prod`: opでまとめた値を一つ返す。元の要素のlistではない。
- `tolist`: 現在の要素をindex順に並べたコピー。
- `all_prod`: 配列全体の積をO(1)で返す。

## 巨大な配列で更新する場所が少ない場合

初期値がすべてidentityで、更新位置を先に列挙できるなら、更新する座標だけを昇順に圧縮する。未登録の座標には単位元しかないため、積から省いてよい。

- 構築: `positions = sorted(set(更新位置))`とし、その長さのSegTreeを作る。
- 更新: 元の座標に対応する圧縮後のindexへsetする。
- 問い合わせ: leftとrightをそれぞれ`bisect_left(positions, ...)`で移し、prodへ渡す。
- 境界そのものがpositionsに存在しなくてもよい。更新がない区間の積はidentity。

更新位置数KならO(K)のセグ木で済む。初期値がidentityでない場合や、区間内の要素数にも意味がある場合には、そのまま省略できない。

## 注意点

- `add(index, value)`は数値の加算とは限らず、現在値を`op(value, current)`へ置き換える。
- 境界探索のpredicateはidentityに対してTrueで、区間を延ばしたときTrueからFalseへ一度だけ変わること。
- op自体がO(T)なら、区間積・一点更新はO(T log N)。長い文字列の連結などを定数時間とは数えない。
