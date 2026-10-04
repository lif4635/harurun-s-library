# 挿入・削除・反転できる列

## 主な機能

列の途中への挿入・削除、区間反転、区間の集約を期待 O(log(N+1)) 回程度の演算で扱う。区間更新用の `mapping` と `composition` を与えると、一括加算やアフィン変換などもできる。Nは現在の要素数で、初期構築は O(N) 回程度の演算。

`prod` は現在の左から右の順に集約する。文字列連結や行列積のように順序で答えが変わる演算も使える。和や最小値など順序によらない演算なら、`commutative=True` で逆順の集約計算を省ける。

## 使い方

```python
from library_codex.sequence_structure.ImplicitTreap import ImplicitTreap

seq = ImplicitTreap([1, 2, 3, 4], commutative=True)
seq.insert(2, 10)
seq.reverse_range(1, 4)
total = seq.prod(1, 4)
removed = seq.pop(2)
values = seq.tolist()
```

- 反転後の列: `[1, 3, 10, 2, 4]`。
- `total`: 半開区間 `[1, 4)` の和で15。
- `removed`: 削除した値10。
- `values`: 削除後の列 `[1, 3, 2, 4]` のコピー。

区間加算・区間和の場合は次のように作る。

```python
seq = ImplicitTreap(
    [1, 2, 3],
    op=lambda a, b: a + b,
    identity=0,
    mapping=lambda delta, total, size: total + delta * size,
    composition=lambda new, old: new + old,
    commutative=True,
)
seq.apply(0, 2, 5)
total = seq.prod()
```

`total` は `[6, 7, 3]` の和で16。作用の合成は `old` の後に `new` を適用する順序。

## 注意点

- 区間はすべて半開区間。挿入位置は先頭から末尾の直後まで指定できる。
- `mapping` は集約値と区間長から作用後の集約値を求められる必要がある。要素の位置ごとに異なる作用は扱わない。
- `commutative=True` は演算の可換性を検査しない。順序に依存する演算では使わない。
- 削除したノードの領域は再利用しないため、メモリは初期要素数と累計挿入数に比例する。
- 計算量はcallbackの実行時間を除く。文字列連結など、要素の大きさで演算時間が変わる場合はその分もかかる。
