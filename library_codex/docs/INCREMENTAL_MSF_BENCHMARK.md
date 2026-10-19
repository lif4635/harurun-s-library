# 辺追加最小全域森の検証とPyPy測定

`graph_spanning/IncrementalMinimumSpanningForest.py`の`IncrementalMSF`は、辺を追加するたびに最小全域森から外れた辺のIDを返す。合計重み、連結成分数、現在採用している辺も取得できる。

[AM-treeの論文](https://arxiv.org/abs/2504.04619)のlazy AM-treeとPerchを用いる。頂点数に比例する配列で状態を保持し、辺ごとのノードは作らない。辺追加は償却O(log(N + 1))時間、保持メモリはO(N)。比較用のLink-Cut Tree実装は公開APIに含めず、測定用として残している。

## 検証

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`の`incremental_minimum_spanning_forest`を、公式生成器・checkerで17 / 17ケース検証した。最大50万頂点・100万辺、制限時間10秒。

[専用test](../verify/graph_spanning/test_incremental_minimum_spanning_forest.py)では、ランダムな追加列の各prefixをKruskal法と比較する。負の重み、同じ重み、多重辺、自己ループ、不正な頂点、空グラフ、デバッグ出力の非破壊性も検査する。内部の親関係・部分木サイズと、変形前後の木の全頂点対に対するパス最大値も小規模ケースで照合する。

## 反復測定

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。新しいprocessで各5回逐次測定した。起動・JIT・入出力を含み、実行順を入れ替える。すべての出力を公式checkerで検査し、GNU timeで最大RSSを記録した。メモリ制限は強制していない。

全件検証で遅かった3ケースの再測定では、中央値の最大は`max_random_09`の2.467秒、最大RSSは157,396 KiBだった。

同じ入力で比較用Link-Cut Tree実装と測った結果は次のとおり。

| ケース | AM-tree 中央値 | Link-Cut Tree 中央値 | AM-tree 最大RSS | Link-Cut Tree 最大RSS |
| --- | ---: | ---: | ---: | ---: |
| max_random_04 | 2.439秒 | 11.309秒 | 156,536 KiB | 241,612 KiB |
| hack_decreasing_00 | 0.542秒 | 0.925秒 | 138,520 KiB | 248,812 KiB |
| random_04 | 0.229秒 | 0.250秒 | 85,808 KiB | 108,296 KiB |

比較時のtimeoutは40秒。Link-Cut Treeの`max_random_04`は問題の制限時間10秒を超える。これはリポジトリ内の比較実装との測定であり、提出ランキングの最速実装との比較ではない。オンライン提出と全17ケースの反復測定は行っていない。

全入力を先読みする分割統治版も試したが、`max_random_04`の単発測定で20.08秒・540,300 KiBとなり採用しなかった。この版は小規模Kruskal比較のみで、公式全件の検証はしていない。実装は比較用ファイル内の`incremental_msf`として残している。比較用CLIが実行するのはLink-Cut Tree版である。

- [公式全件の判定](../../verify/library_checker/results/incremental_minimum_spanning_forest.json)
- [重い3ケースの各回の時間・RSS・hash](../../verify/library_checker/benchmarks/incremental_minimum_spanning_forest.json)
- [同一入力での比較記録](../benchmarks/results/incremental_msf_comparison.json)
- [比較対象の指定](../benchmarks/results/incremental_msf_snapshot.json)
- [比較用実装](../benchmarks/baselines/incremental_msf_lct.py)
- [問題用driver](../../verify/library_checker/drivers/incremental_minimum_spanning_forest.py)

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/graph_spanning/test_incremental_minimum_spanning_forest.py
pypy3 library_codex/tools/check_library_checker.py test incremental_minimum_spanning_forest --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py incremental_minimum_spanning_forest --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/results/incremental_msf_snapshot.json --problem /path/to/library-checker-problems/graph/incremental_minimum_spanning_forest --cases max_random_04 hack_decreasing_00 random_04 --variant am_tree=verify/library_checker/solutions/incremental_minimum_spanning_forest.py --variant link_cut=library_codex/benchmarks/baselines/incremental_msf_lct.py --repeat 5 --timeout 40 --output library_codex/benchmarks/results/incremental_msf_comparison.json
```
