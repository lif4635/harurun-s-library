# 一点代入を含む区間クエリ

## 主な機能

配列への一点代入と半開区間 `[left, right)` の問い合わせを、発生順に登録してまとめて答えます。利用者が用意するのは `add(value)`、`remove(value)`、`get()` の3つです。更新の巻き戻しや、更新位置が区間内かの判定はclassが担当します。

要素の順序によらない集計に使います。区間内の異なる値の個数、値ごとの頻度、和などが対象です。順序を区別する文字列連結には使えません。

長さ・更新数・クエリ数がそれぞれO(N)なら、callbackをO(1)としてO(N^(5/3))時間、O(N)空間が目安です。更新のない通常のMoは `algorithm/RangeQueries.py` から選べます。

## 使い方

```python
from library_codex.optimization.MoWithUpdates import MoWithUpdates

mo = MoWithUpdates([1, 2, 1])
mo.query(0, 3)
mo.set(1, 1)
mo.query(0, 3)
mo.query(1, 1)

frequency = {}
distinct = 0

def add(value):
    global distinct
    count = frequency.get(value, 0)
    distinct += count == 0
    frequency[value] = count + 1

def remove(value):
    global distinct
    frequency[value] -= 1
    distinct -= frequency[value] == 0

answers = mo.run(add, remove, lambda: distinct)
assert answers == [2, 1, 0]
assert distinct == 0
```

- `query` が返す整数は、`answers` の添字です。
- `set` はその後に登録するクエリだけに影響します。
- `run` の終了時には集計対象を空に戻します。空の状態から再実行できます。

## 注意点

- `get()` が可変listやdictを返す場合は、そのコピーを返してください。
- 値そのものを後から変更しないでください。一点代入は `set` で登録します。
- callbackが例外を投げた場合、集計状態の復元は保証しません。

## 参考

[qandori/cp-library: 更新付きMo](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/data_structure/mo_with_updates.hpp)。3方向の蛇行順序を参照し、値の保存と更新の巻き戻しをclass内へまとめています。

