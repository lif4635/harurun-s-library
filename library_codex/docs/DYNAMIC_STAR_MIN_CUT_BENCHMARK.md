# 中心の辺更新と全域最小カットの検証

`graph_flow/DynamicStarMinCut.py`は、固定された非負重み無向グラフに中心を1頂点加え、中心の辺だけを更新する全域最小カットを扱う。構築は `O(N(N+M) log(N+2))`、1本の置換は `O(log²(N+2))`、最小値取得は `O(1)`。最小カットを実現する頂点集合も `O(N)` で取得できる。

## 実装

[Library Checkerの公式解](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/graph/global_minimum_cut_of_dynamic_star_augmented_graph/sol/correct.cpp)のextreme setと木の経路加算を参考にした。

- `ExtremeVertexSet.py`を独立させ、カット候補木の子IDと境界重みを返す。
- 縮約中の多重辺を辞書で合算し、次数を保持する。各段階で全辺の次数を計算し直さない。
- 有効な辺がないグラフは次数順の削除を省き、候補木を線形時間で作る。
- 木は整数IDと配列で保持し、既存のHLDを利用する。更新用の区間最小値は、遅延値を下へ配らない区間加算で管理する。
- 木の構築・更新・カット復元は再帰を使わない。

## 公式全件と反復測定

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae` の21ケースを、依存込みの単独コードと公式checkerで通過した。最大4000頂点・4000固定辺・20万回更新、制限10秒。オンライン提出は行っていない。

全件検証で遅かった3ケースを、PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linuxで各5回測定した。毎回新しいprocessで逐次実行し、起動・JIT・入出力を含め、全出力を公式checkerで照合した。

| ケース | 時間の中央値 | 最大RSS |
| --- | ---: | ---: |
| balance_many_01 | 5.11秒 | 110056 KiB |
| balance_many_00 | 5.16秒 | 107088 KiB |
| doubledeep_01 | 5.06秒 | 102632 KiB |

最大中央値は5.160秒、最大RSSは約107 MiB。メモリ制限は強制していない。この記録は最終版の測定であり、C++上位提出との同条件での速度比較ではない。

- [公式21ケースの判定](../../verify/library_checker/results/global_minimum_cut_of_dynamic_star_augmented_graph.json)
- [各回の時間・RSS・環境・入力とsourceのhash](../../verify/library_checker/benchmarks/global_minimum_cut_of_dynamic_star_augmented_graph.json)

## 独立した正しさの検査

専用テスト7件で、8頂点以下のランダムグラフの全非空頂点集合を調べ、更新後の最小値と復元したカット重みを照合する。候補木についても、各部分木の境界重みが一致し、全extreme setが含まれることを全列挙で検査する。

多重辺・自己ループ・非連結・重み0・頂点1個・巨大整数・無効な更新・デバッグ表示とコピー・深さが再帰上限を超える木も対象とする。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/graph_flow/test_extreme_vertex_set.py library_codex/verify/graph_flow/test_dynamic_star_min_cut.py
pypy3 library_codex/tools/check_library_checker.py test global_minimum_cut_of_dynamic_star_augmented_graph --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py global_minimum_cut_of_dynamic_star_augmented_graph --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
