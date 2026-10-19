# 固定法の離散対数の検証とPyPy測定

`number_theory/FixedDiscreteLog.py`は、素数と原始根を固定した離散対数の問い合わせをO(1)で処理する。法Pは10の9乗以下。小さい素数の対数を共有探索表で求め、Farey近似と小さい整数の対数表を組み合わせる。[公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/number_theory/discrete_logarithm_fixed_mod/bsdsdblib/numtheo/farey_tech.hpp)を参考にした。

√P以下の素数の個数をRとすると、構築は期待O(P^(2/3) + √(P R))時間・一時メモリ、保持メモリはO(P^(2/3))。整数演算とdict操作をそれぞれO(1)・期待O(1)として数える。

## 検証

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`の`discrete_logarithm_fixed_mod`を、公式生成器・checkerで24 / 24ケース検証した。最大100万問い合わせ、法は10の9乗以下、制限時間10秒。

[専用test](../verify/number_theory/test_fixed_discrete_log.py)では、小さい素数と全原始根、Farey近似を使う法での全指数、大きい素数でのランダムな指数を累乗と照合する。0・負数・法以上の問い合わせ、合成数・範囲外の法・原始根でない底も検査する。

## 反復測定

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。全件検証で遅かった3ケースを、新しいprocessで各5回逐次測定した。前計算・起動・JIT・入出力を含み、ケース順は反復ごとに入れ替える。すべての出力を公式checkerで検査した。

| ケース | 中央値 | 最大RSS |
| --- | ---: | ---: |
| big_safe_random_00 | 1.113秒 | 239,380 KiB |
| max_00 | 1.115秒 | 239,232 KiB |
| big_safe_random_g2_03 | 1.056秒 | 239,376 KiB |

この環境での単独測定で、上位提出との直接比較ではない。オンライン提出と全ケースの反復測定は行っていない。メモリ制限は強制していない。

- [公式全件の判定](../../verify/library_checker/results/discrete_logarithm_fixed_mod.json)
- [各回の時間・RSS、入力・sourceのhash](../../verify/library_checker/benchmarks/discrete_logarithm_fixed_mod.json)
- [問題用driver](../../verify/library_checker/drivers/discrete_logarithm_fixed_mod.py)

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/number_theory/test_fixed_discrete_log.py
pypy3 library_codex/tools/check_library_checker.py test discrete_logarithm_fixed_mod --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py discrete_logarithm_fixed_mod --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
