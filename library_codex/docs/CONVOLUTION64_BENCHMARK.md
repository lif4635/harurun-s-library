# 64bit整数畳み込みの検証とPyPy測定

`convolution/Convolution64.py`の`convolution_u64`は、通常の整数の畳み込みを2の64乗で割った余りで返す。NTTを5つの素数で実行し、中国剰余定理で係数を復元する。結果の長さLに対して`O(L log(L+2))`時間、`O(L)`追加メモリ。片方が32要素以下なら直接積和を計算する。

## 復元可能な範囲

結果の長さは2の21乗以下に制限する。このとき短い入力の長さは2の20乗以下なので、係数の上限は5素数の積未満になる。

$$
2^{20}(2^{64}-1)^2
<998244353\cdot1012924417\cdot1224736769\cdot754974721\cdot469762049.
$$

NTT後の係数は非負整数として一意に復元できる。2の64乗で割った余りにするのは最後だけで、途中で上位bitを捨てない。浮動小数点は使わない。

## 公式ケース

公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。[Convolution Mod 2^64](https://judge.yosupo.jp/problem/convolution_mod_2_64)の44ケースすべてを、依存込みの単独コードと公式checkerで通過した。片方の最大長524288、制限10秒。オンライン提出は行っていない。

専用testでは、小さい入力との全係数比較、負数・64bitを超える係数、零列、同一配列の平方、NTTの長さが切り替わる境界を確認する。さらに、両入力長1048576・全係数2の64乗−1で、対応上限の変換サイズと復元係数を確認した。

## 反復測定

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。全件検証で遅かった3ケースを新しいprocessで各5回逐次測定した。起動・JIT・入出力込み、ケース順は反復ごとに変更し、全出力を公式checkerで照合した。

| ケース | 中央値 | 最大RSS |
| --- | ---: | ---: |
| gen_524288_00 | 3.592秒 | 537928 KiB |
| gen_524288_01 | 3.639秒 | 520292 KiB |
| all_same_01 | 3.326秒 | 575244 KiB |

最大RSSは約562 MiB。多倍長整数を使ったCRT復元とPyPyの実行時メモリを含むため、512 MiB制限への適合は保証しない。メモリ制限を強制した測定ではない。外部の最速提出との比較や全ケースの反復測定は行っていない。

- [公式全件の判定](../../verify/library_checker/results/convolution_mod_2_64.json)
- [各回の時間・RSS・入力とsourceのhash](../../verify/library_checker/benchmarks/convolution_mod_2_64.json)
- [問題用driver](../../verify/library_checker/drivers/convolution_mod_2_64.py)
- [専用test](../verify/convolution/test_convolution64.py)

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/convolution/test_convolution64.py
pypy3 library_codex/tools/check_library_checker.py test convolution_mod_2_64 --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py convolution_mod_2_64 --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
