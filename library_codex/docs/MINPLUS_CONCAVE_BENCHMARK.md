# 凹列のmin-plus畳み込みの検証

2026-10-10 JST。公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`を固定。オンライン提出は行わない。

## 追加した機能

`convolution/MinPlusConvolution.py` に `minplus_conv_concave(arbitrary, concave, return_argmin=False)` を追加した。既存の凸列版とは別の関数で、引数順は一般列、第2引数が形状を制約した列、で揃える。

- 凹列の隣接差分は広義単調減少。
- 入力長をA、Cとして時間 `O(A log(C+1)+C)`、追加メモリ `O(A+C)`。
- 両方が空でないとき、出力長は `A+C-1`。
- 最小値に加え、必要なら凹列側の添字を返す。入力は変更せず、整数幅を制限しない。
- 互換alias、再帰、要素ごとのnode objectは追加していない。

## 正当性と計算量

一般列を長さC以下の区間へ分ける。1区間の長さをLとすると、その区間による出力長は `C+L-1`。先頭C個を順方向、残りL-1個を逆方向から計算する。いずれも、既に追加された候補が走査の終了まで有効なprefix問題になる。

凹列bと、古い候補i、新しい候補jについて、候補間の差は次の値。

$$D(k)=a_j+b_{k-j}-a_i-b_{k-i},\qquad i<j$$

bの差分が広義単調減少なので、Dはkについて広義単調増加。新候補が有利な範囲はprefixになり、旧候補へ戻る位置を二分探索できる。候補を添字と有効終端の2配列で保持し、新候補に全有効範囲で負ける候補は除く。各候補の追加・削除は高々1回、二分探索は追加1回につき高々1回。全区間の走査長は `O(A+C)`、候補数は `O(A)` なので上記の計算量となる。

## 検証

- `min_plus_convolution_concave_arbitrary`: 公式41ケース通過。
- 同じmoduleを使う凸列×一般列41ケース、凸列×凸列34ケースも再検証した。累計189/253問題・4474ケース通過、未実装64問題。
- 負数、同値、長さ1、長さが不均衡な列、40桁を超える整数、添字復元、入力非破壊を単体testで確認。
- ランダムな一般列・凹列3,000組について単純解と比較。添字復元版・最小値のみの版の両方を確認。
- 公式用の依存展開済みコードはpackageなしで実行する。
- PyPyの全体テストは971件通過・1件失敗。失敗原因は、既存catalogテストが公開関数を凸列版2個に固定していたこと。凹列版を含む期待値へ更新し、冒頭要約も修正して、catalog・API説明・min-plusの関連55テストを再実行し全件通過した。全972件の確認はこの全体実行と再検査の合計であり、修正後に全体をもう一度実行したという意味ではない。
- 修正後に `check_library.py --profile full --skip-tests` で同期・説明・再帰・全性能回帰を再検査した。6167関数に直接・相互再帰なし、説明監査0件、性能検査は既存の閾値のまま通過。

公式検証には公式時間制限を使用する。オンラインとはCPU・PyPyが異なり、メモリ制限は強制していない。

## 上位PyPy提出との比較

[提出389177](https://judge.yosupo.jp/submission/389177)を公式APIの「最新テストAC・PyPy・時間昇順」の先頭から取得した。取得時点の順位であり、全言語や将来の最速を意味しない。全文を確認後、同じ公式入力・checker・PyPyで比較した。

公式解法・比較提出は有効領域を長方形に分割し、各長方形でmonotone minimaを実行する。今回のライブラリは上記のprefix候補管理を使う。[LuzhiledのSMAWK版](https://ei1333.github.io/library/dp/min-plus-convolution-concave-arbitary.hpp)も設計調査で確認したが、移植・性能測定はしていない。

WSL Ubuntu、Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。新規processの起動・JIT・入出力を含む秒数の中央値と最大RSS。各5回、実行順をseed固定で入れ替え、各出力を公式checkerで検査する。重いtestとは並行しないが、Windowsの他アプリやCPU周波数は固定していない。

| 公式ケース | 今回 秒 | 上位PyPy 秒 | 今回 RSS KiB | 上位PyPy RSS KiB |
| --- | ---: | ---: | ---: | ---: |
| max_random_00 | 0.3215 | 0.9420 | 164436 | 183848 |
| monotone_02 | 0.6437 | 1.4326 | 165416 | 182672 |
| only_first_small_00 | 0.3390 | 0.9614 | 172920 | 183484 |

この3ケースでは約2.2〜2.9倍速く、最大RSSは約6〜11%減少した。全入力で同じ倍率になる保証ではない。初回測定はWindows上の記録置換時に一時的なPermissionErrorが発生したため、3ケースすべてを最初から再測定し、完全な記録を保存し直した。

各回の時間・メモリ・入力hash・source hash・比較提出のsnapshotは[比較記録](../benchmarks/results/min_plus_convolution_concave_arbitrary_official_comparison.json)、公式全件後の遅かった3ケース各5回の測定は[標準ベンチマーク](../../verify/library_checker/benchmarks/min_plus_convolution_concave_arbitrary.json)に保存した。

## 再実行

```sh
pypy3 -m pytest library_codex/verify/convolution/test_min_plus_convolution.py -q
pypy3 library_codex/tools/check_library_checker.py build
pypy3 library_codex/tools/check_library_checker.py test min_plus_convolution_concave_arbitrary min_plus_convolution_convex_arbitrary min_plus_convolution_convex_convex --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py min_plus_convolution_concave_arbitrary --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/library_checker.py fetch --problem min_plus_convolution_concave_arbitrary --top 1 --cache ../lc-matching-reference
```

取得したsourceを確認してから実行する。以下のIDは今回確認したもの。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/min_plus_convolution_concave_arbitrary-pypy3.json --reviewed 389177 --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/min_plus_convolution_concave_arbitrary --cases max_random_00 monotone_02 only_first_small_00 --variant library=verify/library_checker/solutions/min_plus_convolution_concave_arbitrary.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/min_plus_convolution_concave_arbitrary_official_comparison.json
```
