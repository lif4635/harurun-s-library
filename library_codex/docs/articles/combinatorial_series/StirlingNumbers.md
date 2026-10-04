# Stirling数

順列のサイクル数や、集合を分割する個数をまとめて数える。

## 主な機能

- 第一種（符号なし）: `n` 個の要素の順列のうち、サイクルがちょうど `k` 個あるものの個数。
- 第二種: `n` 個の異なる要素を、ちょうど `k` 個の空でない集合へ分割する方法の個数。分割した集合どうしの順序は区別しない。
- `*_row(n)` は `n` を固定し、すべての `k` を求める。
- `*_column(k, upper)` は `k` を固定し、要素数が `upper` までの答えを求める。

既定のmod 998244353では、行は `O(n log n)`。列は `O(upper + L log L)` で、`L=upper-k+1`。`k` が0・1・2なら列は `O(upper)` で求める。

## 使い方

```python
from library_codex.combinatorial_series.StirlingNumbers import (
    stirling_first_row,
    stirling_second_row,
    stirling_first_column,
    stirling_second_column,
)

cycles = stirling_first_row(4)
partitions = stirling_second_row(4)
two_cycles = stirling_first_column(2, 4)
two_blocks = stirling_second_column(2, 4)
```

- `cycles`: `[0, 6, 11, 6, 1]`。たとえば4要素の順列でサイクルが2個あるものは11個。
- `partitions`: `[0, 1, 7, 6, 1]`。4要素を2集合へ分ける方法は7通り。
- `two_cycles`: `[0, 0, 1, 3, 11]`。添字が要素数で、2サイクルになる順列の個数。
- `two_blocks`: `[0, 0, 1, 3, 7]`。添字が要素数で、2集合への分割数。

## 注意点

- 第一種の行は、`signed=True` を指定すると符号付きのStirling数を返す。列は符号なし。
- 列の先頭の0も省かない。通常は長さ `upper+1` のlistを返すが、`upper < k` のときは空list。
- `mod` を変更する場合は、求める要素数の上限より大きい素数を指定する。
- 空集合を0集合に分ける方法、空の順列の個数はともに1。
