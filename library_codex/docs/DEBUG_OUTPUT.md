# デバッグ出力

主要なデータ構造は、内部node配列ではなく利用者から見える論理的な内容を `str(obj)` と `repr(obj)` で表示します。

```python
segment = SegTree(lambda a, b: a + b, 0, [1, 2, 3])
print(segment)  # [1, 2, 3]
segment         # SegTree([1, 2, 3])
```

## 出力形式

| 構造 | `str(obj)` | 内容を直接取得するAPI |
| --- | --- | --- |
| Segment Tree・Lazy/Dual Segment Tree・Segment Tree Beats | `[value0, value1, ...]` | `tolist()` |
| Persistent Segment Tree | 最新versionの`[value0, value1, ...]` | `tolist(version)` |
| 2D Segment Tree | `[[row0...], [row1...], ...]` | `tolist()` |
| Dynamic Segment Tree | `{index: value, ...}` | `items()` |
| Fenwick Tree | `[value0, value1, ...]` | `tolist()` |
| SWAG Queue・Deque | 先頭または左端からのlist | `tolist()` |
| Erasable Heap・FastSet・BinaryTrie | 昇順のlist。multisetは重複を残す | `tolist()` |
| Union-Find | 連結成分ごとの2次元list | `groups()` |
| Implicit Treap・Dynamic Wavelet Matrix | 現在の列 | `tolist()` |
| TreapSet | keyの昇順list | `tolist()` |
| PointSetRangeFrequency | 更新後の列を添字順に並べたlist | `tolist()` |
| OrderedMap | key順のdict | `items()` |
| Permutation Tree | node index順のdict list | `tolist()` |
| XorBasis | 昇順の簡約基底。表現できる値の全列挙ではない | `tolist()` |
| UnionRectangle | 追加順の長方形list | `tolist()` |

`repr(obj)` は同じ内容へ型名を付けます。たとえば `FastSet([2, 5, 9])` のように表示します。

## 計算量について

これらはデバッグ用です。通常は保持要素数に対して線形時間が必要で、Heapなどはsortも行います。提出コードの反復処理内では呼ばず、状態確認に使ってください。

圧縮BinaryTrieの`tolist()`は重複を含む昇順listをO(N)で返します。BinaryTrieMonoidの`items()`はキーの昇順の`(key, value)`のlistをO(D)で返し、strは同じ順序のdict、reprは`BinaryTrieMonoid({...})`です。どちらも全体XORを反映し、表示によって状態は変わりません。

Lazy/Dual Segment TreeとSegment Tree Beatsの `tolist()` は、保留中の遅延更新をleafへ反映してから値を返します。集約結果は変わりません。

## 両端回文木

`DequePalindromicTree.tolist()`と`str(obj)`は現在の列を先頭から末尾の順で示します。`repr(obj)`は`DequePalindromicTree([...])`です。列の長さをNとしてO(N)時間で、回文のカウンタや更新状態は変更しません。

## 群の差・木の距離更新・区間最頻値

`PotentialUnionFind.tolist()`は頂点番号順の`(代表頂点, その代表からの群の差)`を返します。`str`は同じlist、`repr`は`PotentialUnionFind([...])`です。経路圧縮だけを行い、制約は変更しません。

`CentroidDistanceFenwick`・`CentroidDistanceAdd`・`StaticRangeMode`の`tolist()`は現在値を元の頂点番号・添字順に返します。`str`は同じlist、`repr`は型名を付けます。`CentroidDistanceAdd`ではO(N log² N)、他2つではO(N)かかります。

## 両端キュー

`Deque.tolist()`は左端から右端の順の浅いコピーをO(N)時間・追加メモリで返す。`str`は同じlist、`repr`は`Deque([...])`。表示で列の内容や両端は変わらない。

## 区間代入

`RangeAssignSegTree.tolist()`は区間代入を反映した現在値をindex順に返す浅いコピー。`str`は同じlist、`repr`は`RangeAssignSegTree([...])`。O(N)時間で、opを呼び出さずに遅延情報を下ろし、論理値を変更しない。

## 一次式の区間加算

`RangeLinearAddRangeMin.tolist()`は、保留中の一次式加算も含めた現在値をindex順に返します。
`str`は同じlist、`repr`は`RangeLinearAddRangeMin([...])`です。時間・追加メモリはO(N)で、内部の遅延状態は変更しません。

## Tree Wavelet Matrix

`TreeWaveletMatrix.tolist()`と`str(obj)`は、constructorへ渡した頂点値を頂点番号順のlistで返します。`repr(obj)`は`TreeWaveletMatrix([...])`の形です。内部のHLD順や圧縮後のrankは表示しません。

## Permutation Tree

`PermutationTree.tolist()`は、内部の平坦な配列から各nodeの`kind`、`left`、`right`、`minimum`、`maximum`、`parent`、`children`を読み出し、node index順のdict listで返します。`children`はcopyなので、返り値を変更しても木の親子関係は変わりません。`repr(obj)`は`PermutationTree([...])`の形です。
