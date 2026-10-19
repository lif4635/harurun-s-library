# 区間内の転倒数

## 主な機能

更新のない配列に対して、指定区間の転倒数を繰り返し求める。転倒とは、左側の要素が右側の要素より大きい組のこと。同じ値の組は数えない。

`StaticRangeInversions(values)`で前計算し、`query(left, right)`で半開区間 `[left, right)` の答えを取得する。問い合わせを先にまとめる必要はなく、直前の答えで次の区間を決めてもよい。

配列長をNとすると、既定の分割幅では構築にO(N sqrt(N))時間・メモリ、queryにO(sqrt(N))時間。区間内だけを昇順に並べるための、隣接要素の最小交換回数もこの値になる。

問い合わせ区間がすべて先に分かるなら、別モジュール`OfflineRangeInversions`の`range_inversions(values, queries)`も選べる。そちらは区間を一括処理し、O(N+Q)メモリで済む。Qは問い合わせ数。

## 使い方

```python
from library_codex.range_query.StaticRangeInversions import StaticRangeInversions

table = StaticRangeInversions([3, 1, 2, 2, 0])
table.query(0, 5)
table.query(1, 4)
table.query(2, 5)
table.query(2, 2)
```

- `query(0, 5)`は`7`。3より小さい後続要素が4個、1より小さい後続要素が1個、二つの2それぞれに0が1個ある。
- `query(1, 4)`は`0`。対象は`[1, 2, 2]`で、同じ値の2同士は転倒しない。
- `query(2, 5)`は`2`。対象は`[2, 2, 0]`。
- `query(2, 2)`は`0`。空区間も指定できる。

返るのは組数を表す整数で、要素や添字の組のlistではない。定義は次のとおり。

$$
\#\{(i,j)\mid \mathrm{left}\le i<j<\mathrm{right},\ a_i>a_j\}.
$$

## メモリと分割幅

大きな頻度表は通常のPython整数listではなく整数配列に詰めて保持する。それでもメモリは線形ではない。N=100,000、既定の幅317の場合、この表だけで約121 MiBを使い、元の配列・補助表・PyPy本体は別途必要になる。

`block_size`を大きくすると頻度表は小さくなり、問い合わせとブロック内の前計算は重くなる。幅Bに対して、構築はO(N log(N+1) + NB + N²/B)時間、メモリはO(N + N²/B)、queryはO(B)。

## 注意点

- 要素の更新には対応しない。元の入力listを書き換えても、構築済みの答えは変わらない。
- `tolist()`と`str(table)`は元の配列を添字順に示す。圧縮後の順位や内部の頻度表は表示しない。
- 要素は互いに大小比較できるものを渡す。比較結果が後から変化するオブジェクトやNaNは対象外。
- 転倒数は32bitを超えることがある。返り値は剰余を取らないPython整数。

## 仕組み

配列を連続したブロックに分け、ブロック境界どうしの転倒数と、各境界までに現れた値の順位別累積個数を前計算する。問い合わせでは両端の不完全なブロックだけを補正する。

重複値には元の出現順に異なる順位を与える。この順序では等しい値の前後関係が反転しないため、元の転倒数を保ったまま順位を一意にできる。

[Library Checkerの公式解法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/data_structure/static_range_inversions_query/sol/correct.cpp)の平方分割を基に、PyPy用の配列構成で実装している。
