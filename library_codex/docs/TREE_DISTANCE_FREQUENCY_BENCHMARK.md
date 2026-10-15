# 木の距離分布の速度とメモリ

2026-10-15、WSLのPyPy 3.10 / 7.3.16で、同じ公式入力に対して変更前後を各5回測定した。時間は起動・JIT・入出力を含む中央値。RSSは各5回の最大値。実行順は入れ替え、出力を毎回公式checkerで確認した。

| 公式ケース | 変更前 秒 | 変更後 秒 | 変更前 MiB | 変更後 MiB |
| --- | ---: | ---: | ---: | ---: |
| max_random_00 | 4.341 | 1.397 | 401.6 | 114.2 |
| line_00 | 6.434 | 2.419 | 637.3 | 124.3 |
| line_star_02 | 7.569 | 2.386 | 462.5 | 124.9 |
| almost_uni_00 | 1.792 | 0.537 | 264.6 | 111.1 |

比較した4ケースでは約2.7〜3.3倍高速化した。変更後は公式20ケースすべてをローカルで通過。オンライン提出や外部の最速提出との測定比較ではない。

## 変更内容

- 各頂点から全祖先重心への経路を保存せず、成分を処理するときに距離ヒストグラムを作って消費する。追加メモリを O(N log N) から O(N) に削減した。
- ヒストグラムの二乗の各係数は「最大要素×要素の総和」以下。この上限が998244353未満なら1つのNTTだけで整数の答えが確定する。
- 上限が大きい場合は2つの法から復元し、それでも足りなければ従来の3つの法を使う。小さいヒストグラムは直接計算する。
- `include_same=True`の検査が呼出し結果ではなく手作業の配列変更を比較していたため、実際の呼出し結果を検査する形へ修正した。

公開関数の引数、順序を区別しない数え方、末尾の0を省く返り値は変更していない。

## 記録と再実行

- [変更前後の各測定値・sourceと入力のhash](../benchmarks/results/tree_distance_frequency_comparison.json)
- [変更前の単独実行コード](../benchmarks/baselines/tree_distance_frequency_before.py): ライブラリは`3d4494b`時点、問題用の入出力は現在と同じ。
- [変更後の公式全件検証](../../verify/library_checker/results/frequency_table_of_tree_distance.json)
- [変更後の反復測定](../../verify/library_checker/benchmarks/frequency_table_of_tree_distance.json): 実行環境のCPU・OS・PyPy情報も収録。

リポジトリ直下で実行する。公式問題リポジトリの生成済み入力・正解・checkerを使う。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/results/tree_distance_frequency_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/tree/frequency_table_of_tree_distance --cases max_random_00 line_00 line_star_02 almost_uni_00 --variant before=library_codex/benchmarks/baselines/tree_distance_frequency_before.py --variant after=verify/library_checker/solutions/frequency_table_of_tree_distance.py --repeat 5 --output library_codex/benchmarks/results/tree_distance_frequency_comparison.json
```
