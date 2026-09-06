# 同じ数の間に指定個数を挟む列を作る

## 主な機能

1から$n$までを2回ずつ並べ、二つの$k$の間にちょうど$k$個の位置を挟む列を作る。二つの出現位置を$i<j$とすると、$j-i=k+1$になる。

- `langford(n, hooked=False)` — 条件を満たす列を一つ、O(n)時間・領域で構築する。探索や再帰は使わない。

| 指定 | 構築できる$n \bmod 4$ | 長さ | 穴 |
| --- | --- | --- | --- |
| `hooked=False` | 0, 3 | $2n$ | なし |
| `hooked=True` | 1, 2 | $2n+1$ | 末尾から2番目 |

通常版が作れない$n$では、`hooked=True`で穴を一つ設ければ構築できる。

## 使い方

```python
from library_codex.combinatorics.Langford import langford

a = langford(3)
b = langford(2, hooked=True)
```

- `a`は`[2, 3, 1, 2, 1, 3]`。二つの1の間には1個、2の間には2個、3の間には3個の要素がある。
- `b`は`[1, 2, 1, 0, 2]`。0が穴を表す。二つの2の間には、1と穴の計2位置がある。

## 返り値

- 成功時は`list[int]`。1から$n$がそれぞれ2回現れる。
- 穴ありでは`result[2*n-1]`だけが0。穴も距離に数えるため、0を取り除いてはいけない。
- 指定した種類の列が存在しない場合は`None`。たとえば`langford(2)`や`langford(3, hooked=True)`。

## 注意点

- `hooked`は穴あり版を選ぶ指定で、通常版との自動切替ではない。穴の位置は固定。
- `n=0`は通常版なら`[]`、穴あり版なら`None`。負の`n`は`ValueError`。
- 返すのは決定的な一例。辞書順最小・一様ランダム・全列挙・個数の計算は行わない。
- 出現位置の差を$k$にしたい場合は`Skolem.py`の`skolem`を使う。

## 構築方法と参考文献

通常版は[Counting Skolem Sequences](https://dialectrix.com/langford/Assarpour-Liu/skolem.notes.pdf)のTable 2にあるDaviesの構築を使い、等差数列のブロックを連結する。

穴あり版は[Cyclic, Simple and Indecomposable Three-fold Triple Systems](https://arxiv.org/abs/1404.0528)のLemma 3.3、Table 3・4の位置公式を使う。先頭が二つの1となる位数$n+1$のhooked Skolem列から、先頭2要素を除いて正の値を1ずつ減らすと、必要なLangford列になる。実装では変換後の位置へ直接書き込む。小さい$n=1,2,5,6$は具体例を使う。
