# 線形漸化式の連続項の検証

`fps998/LinearRecurrence.py`の`linear_recurrence_slice`は、開始添字Kから連続するM項を一括で返す。漸化式の次数をDとして、時間は`O(D log(D+1) log(K+2)+(D+M) log(D+M+1))`、追加領域は`O(D log(K+2)+M)`。

## 実装

1/Qの必要な係数区間を半分の添字へ縮め、逆向きに復元する。降下時のQの周波数表現を復元時にも再利用する。必要な中央部分に折り返しが混ざらない長さの巡回畳み込みを使い、不要な端の係数まで計算するための変換長拡大を避ける。全処理は反復で行う。

[Library Checker公式解答](https://github.com/yosupo06/library-checker-problems/blob/master/other/consecutive_terms_of_linear_recurrent_sequence/sol/correct.cpp)の有理母関数を移動する方法を参考にした。既存の第n項APIは変更していない。

## 公式ケースとPyPy測定

[Consecutive Terms of Linear Recurrent Sequence](https://judge.yosupo.jp/problem/consecutive_terms_of_linear_recurrent_sequence)の公式43ケースを通過した。Dは最大10万、Mは最大50万、Kは最大10の18乗、時間制限は10秒。公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。全件検証で遅かった3ケースを各5回、新しいprocessで逐次測定した。起動・JIT・入出力込み。ケース順を入れ替え、毎回公式checkerで答えを検証している。

| ケース | 中央値 | 最大RSS |
| --- | ---: | ---: |
| random_01 | 4.800秒 | 235,348 KiB |
| max_random_00 | 5.001秒 | 238,672 KiB |
| max_random_01 | 5.075秒 | 238,612 KiB |

この環境での単独測定で、上位提出との比較ではない。オンライン提出と全ケースの反復測定は行っていない。メモリ制限は強制していない。

- [全ケースの判定](../../verify/library_checker/results/consecutive_terms_of_linear_recurrent_sequence.json)
- [各回の時間とRSS、入力・sourceのhash](../../verify/library_checker/benchmarks/consecutive_terms_of_linear_recurrent_sequence.json)
- [問題用driver](../../verify/library_checker/drivers/consecutive_terms_of_linear_recurrent_sequence.py)

## APIの検査

[専用test](../verify/fps998/test_linear_recurrence.py)で素朴な漸化式展開と比較する。巨大添字では既存の第n項APIとも比較し、係数の末尾0、全係数0、空列、空の取得範囲、負の入力係数、入力非破壊を検査する。既存の漸化式推定と有理FPS係数のtestもこのfileへまとめた。

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/fps998/test_linear_recurrence.py
pypy3 library_codex/tools/check_library_checker.py test consecutive_terms_of_linear_recurrent_sequence --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py consecutive_terms_of_linear_recurrent_sequence --official /path/to/library-checker-problems --repeat 5 --slowest 3
```
