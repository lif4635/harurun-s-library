# 整数キーの点更新と区間積

## 主な機能

整数キーへ値を一つずつ設定し、指定した半開区間のキーに属する値を集約する。和・最小値だけでなく、文字列連結や行列積などの非可換モノイドも、キーの昇順で計算できる。

点更新・削除・区間積はビット幅Bに対してO(B)回の演算。全体の積はO(1)。分岐しない経路を省略し、削除した領域を再利用する。確保領域は過去に同時保持したキー数の最大値に比例し、通常版BinaryTrieへの依存はない。

## 使い方

```python
from operator import add

tree = BinaryTrieMonoid(add, 0, 30, commutative=True)
tree.set(3, 10)
tree.set(8, 20)
assert tree.prod(3, 8) == 10
assert tree.all_prod() == 30
tree.xor_all(1)
assert tree.items() == [(2, 10), (9, 20)]
assert tree.get(2) == 10
assert tree.discard(9)
assert tree.all_prod() == 10
```

非可換の場合も特別なラッパーは不要。

```python
tree = BinaryTrieMonoid(lambda a, b: a + b, "", 30)
tree.set(8, "B")
tree.set(3, "A")
assert tree.prod(0, 10) == "AB"
```

## 注意点

- 同じキーへの`set`は上書き。重複を数えるmultisetではない。
- `prod(left, right)`は半開区間[left, right)。対象なしなら単位元。
- `identity`を設定してもキーは登録されたまま。`discard`で削除する。
- `op`は結合則と単位元の条件を満たし、引数のobjectを直接変更しないこと。
- 全体XORはキーだけを変更し、紐づく値は変更しない。`commutative=True`と宣言した可換モノイドに限る。非可換で非ゼロのXORを指定するとValueError。
- 任意範囲の整数座標を使う既存の`DynamicSegmentTree`と用途は近い。この構造は非負整数の圧縮経路とキーの全体XORを扱う。
