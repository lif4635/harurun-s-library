# xの範囲とyの上限による点の列挙

## 主な機能

x座標を先に固定した点について、y座標の変更・無効化・再有効化を行いながら、次の条件を満たす点を列挙します。

$$
\mathrm{left}\le x_i<\mathrm{right},\qquad y_i<\mathrm{upper}
$$

たとえば各地点の現在の費用をyとして持ち、「指定した範囲内で予算未満の地点」を取り出せます。固定点数N、列挙数Kに対して更新はO(log N)、列挙はO(log N+K)。同じ横範囲でy最小の点を選ぶ操作もO(log N)です。

## 使い方

```python
from library_codex.spatial_structure.PrioritySearchTree import PrioritySearchTree

tree = PrioritySearchTree([10, 20, 20, 30], [7, 2, 5, None])
assert sorted(tree.report(10, 30, 6)) == [1, 2]
assert tree.min_y(10, 30) == 1
tree.set(1, 9)
tree.set(3, 1)
assert tree.min_y(10, 40) == 3
assert tree.erase(2)
assert tree.get(2) is None
assert tree.items() == [(0, 10, 7), (1, 20, 9), (3, 30, 1)]
```

- 点IDは入力順です。同じx座標の点も別IDとして管理します。
- `report`は点IDのlistで、順序は保証しません。座標やyの値そのものではありません。
- `min_y`も点IDを返します。最小yが同値なら最小IDを選び、対象がなければ`None`です。
- `items`は`(ID, x, y)`のlistをID順に返します。`str`・`repr`でも現在の有効な点を確認できます。

## 仕組み

x座標順に区間を二分し、各nodeにはその部分木でy最小の点を1個だけ置きます。全nodeは整数IDの配列で保持し、nodeごとのobjectは作りません。更新では点を取り除いて穴を埋め、新しいyで入れ直します。列挙では最小yが上限以上の部分木をまとめて除外します。

## 注意点

- x座標の変更や、構築時になかった点IDの追加はできません。
- yを省略すると全点無効、個別のyに`None`を渡すとその点だけ無効です。`set`で再有効化できます。
- x方向は半開区間、y方向は上限を含みません。yの下限は指定できません。
- 座標は全順序で比較できる値に限ります。NaNや比較中に意味が変わる値は使えません。
- 一般の矩形集約・矩形更新を行う`LazyKDTree`とは操作が異なります。
- PyPyで比較した更新混在・狭い範囲では、単純な最小値セグ木より遅くなりました。全範囲から少数の点を列挙するケースでは速く、全用途の高速版ではありません。

## 参考

[qandori/cp-libraryのPrioritySearchTree](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/data_structure/priority_search_tree.hpp)の点ID・固定x座標・y順heapを参照し、列挙と探索を反復処理にしています。
