# 同じ長さの区間を対応位置ごとに併合する

## 主な機能

`merge(a, b, length)`で、半開区間`[a, a + length)`と`[b, b + length)`の対応する要素を同じ成分へまとめます。すでに併合済みの区間は内部で省略するため、長い区間を繰り返し指定する場合に使います。

構築は`O(N log N)`時間・領域。`Q`回の併合は全体で`O((N log N + Q) alpha(N))`時間です。`find`・`same`・`size`は償却`O(alpha(N))`。

## 使い方

```python
from library_codex.union_find.RangeParallelUnionFind import RangeParallelUnionFind

uf = RangeParallelUnionFind(6)
uf.merge(0, 3, 3)
connected = uf.same(1, 4)
count = uf.size(1)
```

- `connected`: `True`。この操作で`{0, 3}`、`{1, 4}`、`{2, 5}`の3成分になる。
- `count`: `2`。頂点1を含む成分の要素数。
- `find(v)`: 頂点`v`を含む成分の代表番号。併合すると変わることがある。
- `merge(...)`: 値は返さず、連結状態を更新する。

成分の和などを持つ場合は、実際に併合が起きたときだけ呼ばれるcallbackを使います。

```python
uf = RangeParallelUnionFind(6)
totals = [1, 2, 3, 4, 5, 6]

def joined(root, old):
    totals[root] += totals[old]

uf.merge(0, 3, 3, joined)
value = totals[uf.find(1)]
```

- `root`: 併合後の代表番号。
- `old`: 代表でなくなった成分の、併合前の代表番号。
- `value`: `7`。頂点1と4の値の合計。
- callbackの返り値は使わない。すでに同じ成分なら呼ばず、全操作を通して最大`N-1`回呼ぶ。その実行時間は上記計算量へ別途加わる。

## 仕組み

長さが2の冪の区間を階層別に管理します。同じ階層の2区間が初めて併合されたときだけ、それぞれの前半・後半へ処理を下ろします。階層ごとの親と成分サイズは、単一の固定幅整数配列へまとめています。全要素の番号が32ビットで収まる場合は1要素4バイト、それより大きければ64ビットを使います。

## 注意点

- `length`が正なら、両区間は`[0, N)`内に収める。範囲外は`IndexError`。
- 区間同士は重なってもよい。`length <= 0`は何もしない。
- 1回の呼出しだけで償却`O(alpha(N))`になるわけではない。初めて長い区間を併合する場合は、その長さに比例した処理が必要。
