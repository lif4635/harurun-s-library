# 余因子行列の比較記録

2026-10-14。PyPy 7.3.16 / Python 3.10.14、WSL Linux、Ryzen 7 3700X。公式問題revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。

## 対象と検証範囲

`linear_algebra/Adjugate.py`の`adjugate`を、Library Checkerの[Adjugate Matrix](https://judge.yosupo.jp/problem/adjugate_matrix)で検査した。素数法の正方行列から余因子を転置した行列を返す。正則・階数N−1・階数N−2以下を区別し、一度の消去で計算する。乱数は使わない。

公式44ケースを全件通過。オンライン提出は行っていない。小さい素数法の2×2行列の全探索と、N=1〜7の全階数のランダム行列について、余因子を一つずつ計算する単純解とも比較した。

## 上位PyPyとの比較

取得時点の最速PyPy提出[250213](https://judge.yosupo.jp/submission/250213)を、同じ公式4ケースで各5回測定した。プロセスを毎回起動し、起動・JIT・入出力を含む。実行順は入れ替え、全出力を公式checkerで確認した。

| ケース | 行列サイズN | 最初の実装 | 採用版 | 参照250213 | 採用版の最大RSS | 参照の最大RSS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| max_random_00 | 500 | 1.195秒 | 0.515秒 | 0.767秒 | 80048 KiB | 83144 KiB |
| highrank_max_random_00 | 500 | 1.191秒 | 0.469秒 | 0.709秒 | 74020 KiB | 85432 KiB |
| lowrank_max_random_02 | 497 | 1.022秒 | 0.423秒 | 0.619秒 | 72388 KiB | 82700 KiB |
| perm_max_random_00 | 494 | 0.106秒 | 0.106秒 | 0.719秒 | 72136 KiB | 84760 KiB |

- 密な3ケースでは、最初の実装の約2.3〜2.5倍速く、参照提出より約32〜34%短い時間だった。
- 順列行列では最初の実装とほぼ同じ。参照提出は補助行列を乱数で拡張するため、疎性を利用する本実装とは挙動が異なる。
- 比較はこの4ケースとこのPyPy環境に限る。全入力・全言語での最速性は主張しない。
- 参照実装は、拡張した行列が特異なら零行列を返す確率的な方式。本実装は小さい素数でも確率的な誤答を避けるため、その方式を採用していない。

[各回の時間・RSS・入力とsourceのhash・取得時のランキング](../benchmarks/results/adjugate_matrix_comparison.json)を保存した。比較前のコードは[基準実装](../benchmarks/baselines/adjugate_matrix.py)、採用版は[提出コード](../../verify/library_checker/solutions/adjugate_matrix.py)にある。

## 定数倍の変更

最初の実装では、拡大行列の消去を任意法の剰余演算で行っていた。998244353の場合だけ内側ループの法を定数で書き、消去係数を非負の剰余にした。ほかの素数では一般のループを使う。APIと計算結果は同じ。

単に関数の先頭で`mod = 998244353`と代入し直す試作では十分な差が出なかった。最終版では、実際の反復内の剰余演算を定数にしている。JIT内部の命令列を解析したわけではなく、採否は同条件の実測で判断した。

## 公式ケースの反復測定

全件検証後、遅かった公式3ケースを各5回測定した。[各回の記録](../../verify/library_checker/benchmarks/adjugate_matrix.json)と[一覧](../../verify/library_checker/benchmarks/README.md)を参照。公式44ケースすべてを反復したわけではない。公式の時間制限は5秒、メモリ制限はローカルでは強制していない。

## 再実行

リポジトリのルートから実行する。`--official`と`--cache`は手元の保存先に合わせる。

```sh
pypy3 library_codex/tools/check_library_checker.py test adjugate_matrix --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py adjugate_matrix --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/library_checker.py fetch --problem adjugate_matrix --language pypy3 --top 2 --cache /home/harurun/.cache/harurun-library-checker/comparisons/adjugate_matrix
```

取得したsourceを確認してから、比較に使うIDを指定する。ランキングが変わった場合は、保存したsnapshotのIDとhashで測定対象を区別する。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot /home/harurun/.cache/harurun-library-checker/comparisons/adjugate_matrix/adjugate_matrix-pypy3.json --reviewed 250213 --problem /home/harurun/.cache/harurun-library-checker/problems/linear_algebra/adjugate_matrix --cases max_random_00 highrank_max_random_00 lowrank_max_random_02 perm_max_random_00 --variant baseline=library_codex/benchmarks/baselines/adjugate_matrix.py --variant candidate=verify/library_checker/solutions/adjugate_matrix.py --repeat 5 --timeout 30 --output library_codex/benchmarks/results/adjugate_matrix_comparison.json
```
