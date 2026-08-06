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
| OrderedMap | key順のdict | `items()` |

`repr(obj)` は同じ内容へ型名を付けます。たとえば `FastSet([2, 5, 9])` のように表示します。

## 計算量について

これらはデバッグ用です。通常は保持要素数に対して線形時間が必要で、Heap・BinaryTrieなどはsortや1要素ずつの復元も行います。提出コードの反復処理内では呼ばず、状態確認に使ってください。

Lazy/Dual Segment TreeとSegment Tree Beatsの `tolist()` は、保留中の遅延更新をleafへ反映してから値を返します。集約結果は変わりません。
