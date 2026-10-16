# 永続区間アフィン変換の検証

`segment_tree/PersistentRangeAffineRangeSum.py`は、区間アフィン変換・別の版からの区間コピー・区間和をO(log N)で処理する。版ごとに配列全体を複製せず、変更された境界の経路だけを追加する。子への参照に変換係数を持たせ、遅延情報を下ろすだけのノード複製を避ける。

## 公式ケース

[Persistent Range Affine Range Sum](https://judge.yosupo.jp/problem/persistent_range_affine_range_sum)の公式26ケースをPyPyで通過。公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`、NとQの上限はともに10万、時間制限は5秒。

## 反復測定

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。全件検証で遅かった3ケースを各5回、新しいprocessで逐次実行した。起動・JIT・入出力を含み、ケース順は入れ替え、出力を毎回公式checkerで確認した。

| ケース | 中央値 | 最大RSS |
| --- | ---: | ---: |
| max_less_query_types_03 | 2.271秒 | 381,156 KiB |
| max_less_query_types_00 | 2.258秒 | 388,196 KiB |
| max_random_01 | 1.644秒 | 265,904 KiB |

全ケースの反復測定やオンライン提出は行っていない。上位提出との速度比較ではなく、この環境での単独測定。メモリ制限は強制していない。

- [全26ケースの判定](../../verify/library_checker/results/persistent_range_affine_range_sum.json)
- [各回の時間・RSS・入力とsourceのhash](../../verify/library_checker/benchmarks/persistent_range_affine_range_sum.json)
- [問題用driver](../../verify/library_checker/drivers/persistent_range_affine_range_sum.py)

## APIの検査

[専用test](../verify/segment_tree/test_persistent_range_affine_range_sum.py)では、素朴な配列コピーと比較し、過去の版からの分岐・別の版からの区間コピー・倍率0・負係数・合成数mod・空配列を検査する。問い合わせとデバッグ出力でノードが増えないこと、部分更新のノード増加が木の高さに比例することも確認する。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/segment_tree/test_persistent_range_affine_range_sum.py
pypy3 library_codex/tools/check_library_checker.py test persistent_range_affine_range_sum --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py persistent_range_affine_range_sum --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
