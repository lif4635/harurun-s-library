# 有理数の木上の移動とLCA

## 主な機能

正の有理数を一度ずつ含むStern–Brocot木で、現在位置一つを管理する。根は1/1。左右の境界の分子どうし・分母どうしを足した分数が現在位置になり、左へ進むと小さい分数、右へ進むと大きい分数になる。

左右へ何段もまとめて進む、祖先へ戻る、二つの位置のLCAを求める操作ができる。木全体や全祖先のobjectは作らず、同方向への連続した移動を一つにまとめて保持する。

- 分数からの構築：分子・分母の最大値Aに対してO(log A)回の整数演算。
- 左右へのまとめた移動：償却O(1)回の整数演算。
- 深さ・現在値・境界の取得：O(1)。
- 祖先への移動：取り除く圧縮経路の要素数Kに対してO(1 + K)回の整数演算。
- LCA：二つの圧縮経路の短い方の長さに比例する整数演算。

## 使い方

```python
node = SternBrocotNode(6, 4)
assert node.get() == (3, 2)
assert node.path == [1, -1]
assert node.depth() == 2
assert node.lower_bound() == (1, 1)
assert node.upper_bound() == (2, 1)

other = SternBrocotNode(5, 3)
common = SternBrocotNode.lca(node, other)
assert common.get() == (3, 2)
assert node.go_parent(2)
assert node.get() == (1, 1)
```

## 返り値

- `get()`：現在の既約分数を表す、分子と分母の組。
- `lower_bound()`：現在位置の左境界の分子と分母。根では0/1。
- `upper_bound()`：右境界の分子と分母。根では1/0で、正の無限大の表現。
- `lca(a, b)`：共通祖先の位置を保持する新しいSternBrocotNode。`get()`で分数を取り出す。
- `go_parent(steps)`：移動に成功したかどうか。失敗なら状態は変わらない。

## 注意点

- 境界は登録集合のlower_bound・upper_boundではなく、現在位置を囲む二つの分数。
- 1/0は境界専用の表現。そのままPythonで除算しない。
- 分子・分母は正整数。自動で約分する。
- `path`の正数は右、負数は左への移動回数。読み取り用とし、listを直接変更しない。
- 多倍長整数が大きくなると整数演算自体の時間も増える。
- 条件を満たす有理数を探す用途には、別モジュール`FractionSearch`の探索関数がある。
