# 親を先に並べる制約下の最小転倒数

木の頂点を親から子の順序を守って一列に並べ、後ろの0より前にある1の個数の合計を最小にする。各頂点に複数の0・1をまとめて持たせる場合も扱える。

## 主な機能

- `min_inversions(parent, labels, root=0, return_order=False)` — 各頂点が0か1のラベルを持つ場合のfunction。
- `min_block_inversions(parent, zero_count, one_count, root=0, return_order=False)` — 各頂点を「0をzero_count[v]個、その後ろに1をone_count[v]個」の塊とするfunction。塊の内部を分割して他の頂点を挿入することはできない。
- `return_order=True`なら、最小値に加えて、その値を達成する頂点の順列も返す。

N頂点に対してO(N log(N+1))回の整数演算、O(N)追加メモリ。入力の木や重みは変更しない。根の親の値は参照しない。

## 使い方

```python
from library_codex.tree.ZeroOneTree import min_block_inversions, min_inversions

parent = [-1, 0, 0]
assert min_inversions(parent, [1, 0, 1]) == 1
cost, order = min_block_inversions(parent, [0, 2, 0], [1, 0, 3], return_order=True)
assert cost == 2
assert order == [0, 1, 2]
```

- costは最小転倒数。上の例では根の1の後に頂点1の0が2個並ぶため2になる。
- order[i]はi番目に並べる頂点番号。頂点ごとの位置を返す配列ではない。
- 最適順序が複数あるときは、そのうち一つを返す。辞書順最小などの追加条件は付けない。
- return_orderを省略した場合は整数だけを返し、順序復元用の配列も作らない。

## 重みとして使う

頂点順orderに対し、最小化する値は次の式。cがzero_count、dがone_countに対応する。

$$
\sum_{j<i} d_{\mathrm{order}[j]}c_{\mathrm{order}[i]}
$$

c・dを個数ではなく非負整数の重みとして与えてもよい。実際に0/1列へ展開しないので、大きな重みも渡せる。

## 仕組み

0の個数と1の個数の比で優先度を決め、優先する塊を親側の塊の直後へ結合する。比の比較には整数の交差積を使い、浮動小数点の丸めを避ける。

優先度キューは整数IDを一つずつ保持し、親の重みが変わったらその位置を更新する。過去の優先度のobjectは残さない。順序は次の頂点と末尾を表す二つの配列で復元する。

## 注意点

- 親配列はrootへつながる一つの根付き木であること。親の番号が子より小さい必要はない。
- 負の重みは不可。両方0の空の塊も使える。
- 各塊は0が先、1が後。塊内部の転倒数が別にある場合は、その固定分を結果へ加える。
- 大きな整数では積・比較自体の時間も必要。これをTとするとO(N log(N+1) T)。
