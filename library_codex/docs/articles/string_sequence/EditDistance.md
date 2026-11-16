# 編集距離と編集手順

## 主な機能

文字の挿入・削除・置換をそれぞれ1回として、2つの列を一致させる最小回数を求めます。

- `edit_distance`: 距離だけをビット並列DPで計算します。
- `edit_distance_bounded`: 許す距離が小さいとき、対角線の近くだけを調べます。
- `edit_distance_with_path`: 距離と最短編集手順を通常のDPで復元します。

長い方をN、短い方をM、整数の内部1桁のbit数をwとすると、ビット並列版はO(N ceil(M/w))です。Pythonの多倍長整数の演算を使い、AVX命令や追加packageは必要ありません。

## 使い方

```python
from library_codex.string_sequence.EditDistance import edit_distance, edit_distance_bounded, edit_distance_with_path

assert edit_distance("kitten", "sitting") == 3
assert edit_distance_bounded("kitten", "sitting", 2) == 3
assert edit_distance_bounded("kitten", "sitting", 5) == 3
distance, steps = edit_distance_with_path("ab", "acb")
assert distance == 1
assert steps == [("match", 0, 0), ("insert", 1, 1), ("match", 1, 2)]
```

- bounded版の返り値が `limit + 1` なら「距離はlimitを超える」ことだけが分かります。正確な距離とは限りません。
- 手順は `(operation, first_index, second_index)` のlistです。添字は編集中の文字列ではなく元の2列を指します。
- `match` は一致、`replace` は置換、`delete` はfirst側の削除、`insert` はsecond側の文字の挿入です。

## 注意点

- strはUnicodeの文字単位、bytesはbyte単位で比較します。
- hash可能な要素の列ではビット並列版を使います。listのlistなどhash不能な要素では、等値比較を使うO(NM)時間・O(M)空間のDPに切り替えます。
- bounded版はO(N min(M+1, limit+1))時間・O(min(M+1, limit+1))空間です。
- 編集手順の復元にはO(NM)時間・空間を使います。

## 参考

[kemuniku/cplib: ビット並列編集距離](https://github.com/kemuniku/cplib/blob/f835598fec8e14039cf654a67f0244e0a654d035/src/cplib/str/edit_distance_bitset.nim)と[qandori/cp-library](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/string/edit_distance.hpp)を参照しています。

