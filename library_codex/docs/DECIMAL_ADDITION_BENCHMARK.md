# 巨大整数の加算・オイラー閉路数の比較記録

2026-10-14。PyPy 7.3.16 / Python 3.10.14、WSL Linux、Ryzen 7 3700X。公式問題revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。

## 対象と検証範囲

| 問題 | 実装 | 公式ケース数 |
| --- | --- | ---: |
| Addition of Big Integers | DecimalAddition.add_decimal | 22 |
| Addition of Hex Big Integers | 標準のint・加算・format | 24 |
| Counting Eulerian Circuits | EulerianCircuits.count_eulerian_circuits | 16 |

計62ケースを公式checker・公式時間制限で通過した。オンライン提出はしていない。10進・16進加算は最大200万桁、オイラー閉路数は最大500頂点・20万辺の公式入力を含む。

10進加算は9桁ずつの筆算を使い、両入力が18桁以内なら通常の整数加算へ分岐する。巨大な整数全体の10進変換を避けながら、小さな入力を大量に処理する場合の負担を減らした。16進変換は標準機能で十分速いため、同じ処理を包むライブラリAPIは追加していない。

オイラー閉路数はBEST定理と行列式を使う。孤立頂点を取り除いた行列を作り、必要な階乗の積だけを計算する。行列式の消去を関数内で行うため、コピー用コードに無関係な行列APIは含まれない。辺を持つ頂点数をKとした行列式の計算がO(K³)で、巨大な疎グラフ向けの線形時間実装ではない。

## 上位PyPyとの同条件比較

取得時点で最新テストにACしたPyPy提出を実行時間順に取得し、先頭の提出を比較した。

- 10進加算: [209464](https://judge.yosupo.jp/submission/209464)。18桁区切りの多倍長整数classと専用入出力。
- オイラー閉路数: [297721](https://judge.yosupo.jp/submission/297721)。BEST定理・行列式・階乗表。

各ケースを各実装で5回実行。毎回新しいPyPyプロセスを使い、起動・JIT・入出力を含む壁時計時間の中央値を比較した。順番を入れ替え、すべての出力を公式checkerで検証した。

| 問題・ケース | 採用版 | 上位PyPy | 採用版の最大RSS | 上位の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| 10進 small_00 | 0.304秒 | 0.341秒 | 96000 KiB | 75412 KiB |
| 10進 max_max_00 | 0.121秒 | 0.141秒 | 95556 KiB | 94020 KiB |
| 10進 carry_chain_00 | 0.168秒 | 0.269秒 | 68528 KiB | 72684 KiB |
| 閉路 max_random_circuit_00 | 0.449秒 | 0.498秒 | 97268 KiB | 96704 KiB |
| 閉路 has_isolated_point_00 | 0.147秒 | 0.588秒 | 95824 KiB | 110016 KiB |
| 閉路 loops_00 | 0.133秒 | 0.302秒 | 97208 KiB | 96352 KiB |

10進加算で短い入力への分岐を省いた版は、`small_00`で0.752秒、`max_max_00`で0.138秒、`carry_chain_00`で0.167秒だった。短い入力への分岐を採用する。比較用の分岐なし実装は[decimal_addition_chunks.py](../benchmarks/experiments/decimal_addition_chunks.py)に残した。

閉路の大きいランダムケースでは同程度の時間だった。上位提出の各回は0.425〜0.508秒、採用版は0.430〜0.464秒で、差は実行時の揺れにも左右される。孤立頂点を含むケースや自己ループのケースでは速かったが、すべてのグラフで速いとは扱わない。10進の小さい入力では上位提出より約20 MiB多く使っている。

## 採用版の反復測定

公式全件検証で遅かった各3ケースを各5回測定した。全62ケースを5回ずつ測ったわけではない。最大RSSを記録したが、ローカルでメモリ制限は強制していない。

| 問題 | 最大中央値 | 最大RSS | 公式時間制限 |
| --- | ---: | ---: | ---: |
| 10進加算 | 0.331秒 | 95972 KiB | 5秒 |
| 16進加算 | 0.230秒 | 85240 KiB | 5秒 |
| オイラー閉路数 | 0.435秒 | 97432 KiB | 5秒 |

- 同条件比較: [10進加算](../benchmarks/results/decimal_addition_comparison.json)、[オイラー閉路数](../benchmarks/results/eulerian_circuits_comparison.json)。入力・sourceのhash、参照提出の取得記録、各回の時間とRSSを含む。
- 公式全件検証: [results](../../verify/library_checker/results/)。上の3問題のJSONを参照。
- 反復測定: [問題別一覧](../../verify/library_checker/benchmarks/README.md)。CPU・OS・PyPy・入力・source・checkerのhashを各問題のJSONに保存している。

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test addition_of_big_integers addition_of_hex_big_integers counting_eulerian_circuits --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py addition_of_big_integers addition_of_hex_big_integers counting_eulerian_circuits --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```

比較用sourceを取得・確認した後、保存したsnapshotを指定する。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot /home/harurun/.cache/harurun-library-checker/comparisons/addition_of_big_integers/addition_of_big_integers-pypy3.json --reviewed 209464 --problem /home/harurun/.cache/harurun-library-checker/problems/big_integer/addition_of_big_integers --cases small_00 max_max_00 carry_chain_00 --variant candidate=verify/library_checker/solutions/addition_of_big_integers.py --variant chunks=library_codex/benchmarks/experiments/decimal_addition_chunks.py --repeat 5 --timeout 10 --output library_codex/benchmarks/results/decimal_addition_comparison.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot /home/harurun/.cache/harurun-library-checker/comparisons/counting_eulerian_circuits/counting_eulerian_circuits-pypy3.json --reviewed 297721 --problem /home/harurun/.cache/harurun-library-checker/problems/graph/counting_eulerian_circuits --cases max_random_circuit_00 has_isolated_point_00 loops_00 --variant candidate=verify/library_checker/solutions/counting_eulerian_circuits.py --repeat 5 --timeout 10 --output library_codex/benchmarks/results/eulerian_circuits_comparison.json
```
