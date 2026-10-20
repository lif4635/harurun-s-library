# GF(2^64)係数の畳み込み

64bit整数で表した二元拡大体の係数列を掛ける。Library Checkerの`convolution_F_2_64`と同じ体・同じbit表現を使う。

## 主な機能

- `multiply(first, second)` — 昇べき順の係数列を受け取り、積の全係数を返す。入力は変更しない。
- 加法FFTで計算する。時間は`O(S log^2(S+1))`、追加メモリは`O(S)`。Sは出力長以上の最小の2の冪。
- 同じobjectを両方へ渡す二乗は`O(N)`。片方が短い場合は短い側に合わせたブロック分割を使う。

## 使い方

```python
from library_codex.convolution.BinaryFieldConvolution import multiply

c = multiply([1, 2], [3, 4])
print(c)
print(multiply([1 << 63], [2]))
```

- `c`は`[3, 2, 8]`。中央の係数は`4 XOR 6 = 2`になる。
- 2つ目は`[27]`。体の中ではtの64乗をtの4乗+tの3乗+t+1へ置き換えるので、対応するbitは`11011`になる。

## 係数の表現

各整数のbit iを、体の生成元tのi乗の係数とする。たとえば`3`は1+tを表す。係数の加算はXORで、積は次の既約多項式で割った余りを取る。

$$
t^{64}+t^4+t^3+t+1
$$

そのため`multiply([3], [3])`は`[5]`になる。通常の整数積の9でも、nim積でもない。

## 注意点

- 入力の各要素は0以上2^64未満の整数。範囲外は`ValueError`。
- 出力は長さ`len(first)+len(second)-1`のlist。末尾の0も残す。片方が空なら空list。
- 加法FFTの定数倍は大きい。最大524,288項ずつの公式ケースは、現時点のPyPy測定で10秒制限に未達。[測定範囲と結果](https://github.com/lif4635/harurun-s-library/blob/main/library_codex/docs/BINARY_FIELD_CONVOLUTION_BENCHMARK.md)を確認して使う。

## 仕組み

Cantor基底に沿った加法FFTを使う。通常の次数順とFFT用の基底との変換はXORで行う。体の乗算ではbit間へ6bitの隙間を入れ、整数乗算の結果から各桁の偶奇を取り出す。この展開表現をFFTの途中でも保ち、毎回の展開・圧縮を避ける。

## 参考

- [Library Checkerの問題定義](https://judge.yosupo.jp/problem/convolution_F_2_64)
- [Lin・Chung・Hanによる多項式基底と加法FFT](https://arxiv.org/abs/1404.3458)
