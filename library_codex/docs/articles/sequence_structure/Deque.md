# 両端の追加・削除と添字アクセス

列の先頭と末尾を追加・削除しながら、途中の要素も一定時間で取得・変更する。

## 主な機能

- `Deque(values=())` — 初期列をコピーして構築するclass。空からでも始められる。
- `append`・`appendleft` — 右端・左端への追加。償却O(1)。
- `pop`・`popleft` — 右端・左端の値を返して削除。償却O(1)。
- `queue[index]`・`queue[index] = value` — 途中の位置の取得・変更。O(1)。負のindexも使える。

標準の`collections.deque`では中央付近への添字アクセスがO(N)になる。途中の値を頻繁に読む場合はこちらを使う。全体のモノイド積も必要ならSWAGDequeを使う。

## 使い方

```python
from library_codex.sequence_structure.Deque import Deque

queue = Deque([2, 3])
queue.appendleft(1)
queue.append(4)
queue[1] = 8
assert queue[-1] == 4
assert queue.popleft() == 1
assert queue.pop() == 4
assert queue.tolist() == [8, 3]
assert list(queue) == [8, 3]
```

- pop・popleftは削除した要素を返す。空ならIndexError。
- tolistは現在の要素を左から右へ並べた浅いコピー。表示も同じ順序。
- indexは-length以上length未満。範囲外はIndexErrorで、sliceには対応しない。

## 仕組み

左側を逆順のlist、右側を順方向のlistへ分ける。削除する側が空になったときだけ、反対側のおよそ半分を移す。各追加は償却O(1)、各削除も償却O(1)だが、移し替える一回だけはO(N)かかる。

## 注意点

- 保持する要素数に比例するメモリを使う。最大操作数に合わせた固定配列の事前確保はしない。
- 中央への挿入・削除や区間反転は扱わない。
- 要素objectはコピーしない。格納した可変objectの変更は元のobjectにも反映される。
