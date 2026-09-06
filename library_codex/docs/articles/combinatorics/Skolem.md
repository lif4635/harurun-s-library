# 二つのkを距離kで配置する

## 主な機能

1から$n$までを2回ずつ並べ、二つの$k$の出現位置$i<j$が$j-i=k$を満たす列を作る。たとえば二つの1は隣り合い、二つの2は1位置を挟む。

- `skolem(n, hooked=False)` — Skolem列を一つ、O(n)時間・領域で構築する。

| 指定 | 構築できる$n \bmod 4$ | 長さ | 穴 |
| --- | --- | --- | --- |
| `hooked=False` | 0, 1 | $2n$ | なし |
| `hooked=True` | 2, 3 | $2n+1$ | 末尾から2番目 |

## 使い方

```python
from library_codex.combinatorics.Skolem import skolem

a = skolem(4)
b = skolem(2, hooked=True)
```

- `a`は`[1, 1, 3, 4, 2, 3, 2, 4]`。3は位置2と5にあり、その差が3になる。
- `b`は`[1, 1, 2, 0, 2]`。0は穴。二つの2の位置の差は、穴を含めて2になる。

## 返り値

- 成功時は`list[int]`。1から$n$がそれぞれ2回現れる。
- 穴ありでは`result[2*n-1]`だけが0。0を取り除くと距離条件が崩れる。
- 指定した種類の列が存在しない場合は`None`。

## 注意点

- `hooked`による自動切替はしない。穴の位置は固定。
- `n=0`は通常版なら`[]`、穴あり版なら`None`。負の`n`は`ValueError`。
- 返すのは決定的な一例。辞書順最小や一様ランダムな列ではない。
- 間に挟む位置数を$k$にしたい場合は、出現位置の差が$k+1$となる`langford`を使う。

## 構築方法

位数$n-1$のLangford列の正の値を1ずつ増やし、先頭に`[1, 1]`を置く。元の値$k$の位置の差$k+1$が、新しい値に一致する。穴は0のまま残す。同じ変換を通常版・穴あり版に使う。

構築の出典は[Langfordの記事](https://haruruns-library.star-mido-322.chatgpt.site/library/combinatorics/Langford)にまとめている。提出用コードには、依存する`langford`も含まれる。
