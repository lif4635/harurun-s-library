# 順列の共通区間を木にする

## 主な機能

順列`p`の連続部分列`p[left:right]`について、含まれる値も連続整数になる半開区間`[left, right)`をまとめて表します。木のnode数は`O(N)`で、構築は`O(N log N)`です。

- `PermutationTree(p)` — 共通区間分解木を構築するclass。
- `tree.nodes[tree.root]` — 順列全体を表すroot node。
- `tree.intervals()` — すべての共通区間を半開区間のlistとして列挙するmethod。返す区間数を`K`として`O(N + K)`。
- `tree.count_intervals()` — 共通区間の個数だけを`O(N)`で数えるmethod。

各nodeは位置の半開区間`[left, right)`、値の最小・最大、`parent`、左から右に並ぶ`children`を持ちます。

- `leaf`: 長さ1の区間。
- `linear_asc`: 子の値域が昇順につながる。連続する任意個の子をまとめても共通区間になる。
- `linear_desc`: 子の値域が降順につながる。連続する任意個の子をまとめても共通区間になる。
- `prime`: node全体だけが新しい共通区間になり、途中の連続した子だけをまとめた区間は共通区間にならない。

## 使い方

```python
from library_codex.algorithm.PermutationTree import PermutationTree

p = [1, 3, 0, 2]
tree = PermutationTree(p)

root = tree.nodes[tree.root]
print(root.kind)          # prime
print(root.left, root.right)  # 0 4
print(tree.count_intervals()) # 5
print(tree.intervals())       # (0, 1), (1, 2), ... を含むlist
```

`intervals()`の各`(left, right)`は、`p[left:right]`の最小値を`minimum`、最大値を`maximum`とすると次を満たします。

$$
\mathrm{maximum}-\mathrm{minimum}=\mathrm{right}-\mathrm{left}-1
$$

## 返り値

- `tree.root`: 順列全体を表すnodeの、`tree.nodes`内でのindex。
- `tree.nodes`: `PermutationTreeNode`を構築順に格納したlist。子は親より前に置かれる。
- `tree.intervals()`: 共通区間を`(left, right)`で並べたlist。区間は半開で、辞書順には整列しない。
- `tree.count_intervals()`: 長さ1と順列全体を含む、共通区間の総数。

## 注意点

- 入力は`0, 1, ..., N-1`を一度ずつ含む空でない順列に限る。
- `intervals()`の出力数`K`は`O(N^2)`になりうる。区間そのものが不要なら`count_intervals()`を使う。
- `prime`の子を途中だけまとめた区間が、別の方法で共通区間になることはない。
