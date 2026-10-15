# 有向最小全域木の速度とメモリ

2026-10-15、WSLのPyPy 3.10 / 7.3.16で、同じ公式入力を変更前後それぞれ5回測定した。時間は起動・JIT・入出力込みの中央値。RSSは各5回の最大値。実行順は入れ替え、毎回公式checkerで出力を確認した。

| 公式ケース | 変更前 秒 | 変更後 秒 | 変更前 MiB | 変更後 MiB |
| --- | ---: | ---: | ---: | ---: |
| random_00 | 0.391 | 0.282 | 171.0 | 120.9 |
| max_random_00 | 0.311 | 0.286 | 155.9 | 147.9 |
| max_random_03 | 0.308 | 0.290 | 155.8 | 148.0 |

旧実装は縮約のたびに全辺を走査し、最悪 O(VE) 時間・O(VE) メモリを使っていた。新実装は入辺の候補を一括加算可能なpairing heapで持ち、縮約履歴と併せて O(V + E) メモリに収める。時間は O((V + E) log(V + E))。最安の入辺だけで閉路がなければヒープを作らない。

ヒープだけに置き換えた試作では、最大ランダムケースで約0.38〜0.42秒かかり、旧実装より遅かった。その[比較結果](../benchmarks/results/directedmst_pairing_comparison.json)と[試作コード](../benchmarks/baselines/minimum_cost_arborescence_pairing.py)も残している。閉路のない場合の判定を先に行う現在の実装では、比較した3ケースとも旧実装以下の中央値になった。あらゆる入力での定数倍改善を保証するものではない。

公式12ケースを全件通過。専用テストでは全探索との比較に加え、3万頂点の入れ子の閉路、深いパス、負辺、多重辺、自己ループ、到達不能を確認する。オンライン提出や外部の最速実装との速度比較は行っていない。

## 記録と再実行

- [変更前後の各測定値・入力とsourceのhash](../benchmarks/results/directedmst_comparison.json)
- [変更前の実装と問題用入出力](../benchmarks/baselines/minimum_cost_arborescence_before.py)
- [公式全件の検証結果](../../verify/library_checker/results/directedmst.json)
- [変更後の遅い3ケースの反復測定](../../verify/library_checker/benchmarks/directedmst.json)
- [入れ子の閉路を含む専用テスト](../verify/graph_spanning/test_minimum_cost_arborescence.py)

リポジトリ直下から実行する。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/results/directedmst_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/graph/directedmst --cases random_00 max_random_00 max_random_03 --variant before=library_codex/benchmarks/baselines/minimum_cost_arborescence_before.py --variant after=verify/library_checker/solutions/directedmst.py --repeat 5 --output library_codex/benchmarks/results/directedmst_comparison.json
```
