# 過去版を残す列の編集と連結

## 主な機能

両端への追加・削除、一点代入、分割、連結を行います。更新は新しい版番号を返し、元の版を残します。探索木の探索状態ではなく、列そのものの履歴を分岐させたい場合に使います。

構築はO(N)、要素取得と更新はO(log(N+2))。連結は2列の合計長に対してO(log(N+M+2))です。任意の古い版から更新でき、同じ版同士の連結も可能です。

## 使い方

```python
from library_codex.sequence_structure.PersistentDeque import PersistentDeque

q = PersistentDeque([10, 20, 30])
v1 = q.push_front(5, 0)
v2 = q.set(1, 99, 0)
left, right = q.split(2, v1)
joined = q.concat(right, left)
assert q.tolist(0) == [10, 20, 30]
assert q.tolist(v2) == [10, 99, 30]
assert q.tolist(joined) == [20, 30, 5, 10]
assert q.get(0, v1) == 5
v3 = q.pop_front(v1)
assert q.tolist(v3) == [10, 20, 30]
```

- `push_front`・`push_back`・`pop_front`・`pop_back`・`set`・`concat`の返り値は、新しい版番号です。取り除いた値ではありません。
- `split`は前半と後半の版番号を返します。切れ目indexに対し、区間はそれぞれ半開区間`[0, index)`と`[index, N)`です。
- `version`省略時は最後に作成した版を参照します。`split`後なら後半の版です。
- `tolist(version)`は要素順のlist、`get(index, version)`は1要素を返します。

## 仕組み

32要素以下の葉と、整数IDによるAVL木を共有します。変更した経路だけを作り直し、版ごとの列全体はコピーしません。要素ごとのNodeクラスは作りません。読み取りで内部nodeは増えません。

## 注意点

- 版は同じinstance内だけで使えます。初期版は0です。
- 要素自体は浅く保持します。可変objectを外から変更すると、その要素を共有する版にも影響します。
- 保存した版や内部記録を自動で破棄しません。更新回数に応じてメモリが増えます。
- 長さの上限は2の60乗です。自己連結で巨大な列を表せても、`tolist`・`str`は全要素を展開します。
- `PersistentQueue`は片側の追加・反対側の削除に絞った構造です。文字列の比較・LCPなどは`PersistentString`を使います。

## 参考

[qandの永続deque](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/data_structure/persistent_deque.hpp)の版共有・分割連結を確認し、既存`PersistentString`のAVL joinを整数IDと小さい葉へ組み直しています。
