# 大規模畳み込みの検証

`LargeConvolution.multiply`は998244353上で、出力が2^23項を超える積を求める。16列を1本の配列で処理し、8点単位の変換を領域ごとに進める。入力後半がゼロになる場合は、入力コピーと最初の変換をまとめる。公式10秒制限には届いていない。

## 領域ごとの変換とゼロ部分の省略

2026-10-22、8点変換を導入した後の実装を基準に、分割数・処理順・入力時の変換を比較し直した。基準はGit `c6e9e59`の単独提出コードで、保存済みの`large_radix8_medium.py`と同一。通常の`NTT998`と公開APIは変えない。

最大入力では、各列の変換長を2^21のまま維持し、下位9段を8192要素の領域ごとに処理する。64bit整数の配列部分は1領域64KiB。回転係数の表は順・逆それぞれ21項だけ共有する。入力長が作業配列の半分以下なら、後半のゼロを読む計算を省き、入力を格納しながら最初の8点変換を済ませる。

ゼロ部分の省略は最初の1段に特化した処理で、任意長を扱う一般的なtruncated Fourier transform（TFT）は今回実装・比較していない。

試作の同条件3回比較は次のとおり。各回は新しいPyPy 3.10プロセスを起動し、順序を入れ替え、全18回答を公式checkerで検査した。起動・JIT・入出力を含む中央値。

| 入力 | 基準 | 変換・積・逆変換を領域ごとにまとめる | 領域ごとの変換＋ゼロ部分省略 |
| --- | ---: | ---: | ---: |
| max_random_00 | 13.461秒 | 12.510秒 | 12.312秒 |
| random_00 | 6.508秒 | 6.191秒 | 6.047秒 |

最後の案を本体へ移した。最大入力で約8.5%、中間サイズで約7.1%短縮し、最大RSSはほぼ同じ。変換・積・逆変換をまとめる案は、今回の比較ではさらに速くならなかったため採用しない。これは試作の比較であり、配布コードの測定と全件検証は別に記録する。

本体から生成した配布用の単独コードでも、4入力を基準と各3回比較した。全24回答が公式checkerに一致した。source hashは`f4426d361647f3f7da95398646f5d0b811bfe9d6f293e0d30d0fffc222d01e9e`。

| 入力 | 基準の中央値 | 採用版の中央値 | 基準の最大RSS | 採用版の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| max_random_00 | 13.640秒 | 12.091秒 | 833,172 KiB | 833,032 KiB |
| random_00 | 6.752秒 | 6.156秒 | 439,616 KiB | 439,576 KiB |
| random_01 | 7.006秒 | 6.445秒 | 452,232 KiB | 452,120 KiB |
| small_and_large_01 | 8.728秒 | 8.718秒 | 462,524 KiB | 461,972 KiB |

最大入力は約11.4%、中間サイズは約8.8%・8.0%短縮した。片方が短い経路は変更しておらず、ほぼ同じ。最大入力は11.808〜12.280秒で3回とも10秒を超えている。以前の日付の測定と絶対時間を直接比較して、達成・悪化を判断しない。

- [配布コードと基準の4入力・各3回比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-cache-production-comparison.json)
- [組み合わせの3回比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-radix8-combined-comparison.json)
- [領域分割とゼロ省略を個別に比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-radix8-layout-comparison.json)
- [係数共有・変換と積の統合の比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-radix8-tiled-comparison.json)
- [分割数と領域サイズの予備比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-radix8-layout-screen.json)
- [試作を再生成するscript](../benchmarks/experiments/build_large_transform_variants.py)
- [試作の差分・境界値test](../benchmarks/experiments/test_large_transform_layouts.py)

予備比較は各1回。8列は14.627秒、32列は26.136秒で、同じ回の基準13.709秒を上回れなかった。32列は最大RSSも1,108,996KiBへ増えた。初回の8列試作には未測定の中間サイズ経路で作業配列を余分に確保する設定があり、後続の試作では修正した。測定した最大入力の経路は同じで、初回sourceは生成scriptの`lanes8_initial_screen.py`でhashを含め再現できる。

```sh
pypy3 library_codex/benchmarks/experiments/build_large_transform_variants.py
pypy3 -m pytest library_codex/benchmarks/experiments/test_large_transform_layouts.py library_codex/verify/convolution/test_large_convolution.py -q
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/large_convolution_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_mod_large --cases max_random_00 random_00 --variant baseline=.cache/large-transform-variants/baseline.py --variant fused9=.cache/large-transform-variants/fused9.py --variant cached_zero9=.cache/large-transform-variants/cached_zero9.py --repeat 3 --seed 22004 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-radix8-combined-comparison.json
```

## 領域分割版の公式全ケース

配布用の同じ単独コードを、公式10秒制限で全54ケースに実行した。37件が制限内で通過し、17件が時間超過。[公式検査の記録](../../verify/library_checker/results/convolution_mod_large.json)には`failed`を残す。

時間超過した17件は診断上限120秒で各1回実行し、全回答が公式checkerに一致した。先の37件と合わせて全54入力の正答を確認した。診断では`all_same_00`と`random_02`が10秒未満だったが、全ケース検査の判定を書き換えたり、安定して10秒以内と扱ったりはしない。

診断開始時に前の一覧更新が残っており、冒頭の`fft_killer_02`・`fft_killer_08`はその処理と重なった。正答確認には使えるが、速度比較には使わない。境界にあたる`fft_killer_00`も含む3件を単独で再確認し、全回答が一致した。再検査は12.075〜12.399秒で3件とも公式制限を超えた。速度向上の根拠は前節の新旧同条件・各3回比較とする。

- [17件の診断記録と測定上の注記](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-cache-diagnostic.json)
- [冒頭3件の単独再検査](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-cache-isolated-diagnostic.json)

## 配布前の検査

PyPy全体testは1292 passed・10 skipped、試作と畳み込みの専用testは39 passed。10件はCodon実機用の検査で、今回の高速化をCodon対応と扱わない。両test集合には重複があるため件数を合算しない。

全体性能検査の初回は、未変更の区間集計が速度比2.446倍となり基準2.5倍を下回った。実装・基準を変えず性能検査だけ再実行し、区間集計3.862倍を含む全基準を通過した。測定には揺れがあり、初回の失敗も残す。

- [初回検査の要約](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-release-regression-initial.json)
- [性能検査の再実行結果](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-release-regression.json)

## 8点変換導入時の比較

2026-10-21、変更前のGit `0d89f8f`と採用版を公式4入力で各3回比較した。各回は新しいPyPy 3.10プロセスを起動し、実行順序を入れ替える。全24回答が公式checkerに一致し、測定した候補と生成済み提出コードのSHA-256も一致した。

| 入力 | 変更前の中央値 | 採用版の中央値 | 変更前の最大RSS | 採用版の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| `max_random_00` | 14.716秒 | 11.153秒 | 833,364 KiB | 833,344 KiB |
| `random_00` | 10.441秒 | 5.361秒 | 604,916 KiB | 439,688 KiB |
| `random_01` | 12.561秒 | 6.217秒 | 717,840 KiB | 452,080 KiB |
| `small_and_large_01` | 8.465秒 | 8.935秒 | 462,652 KiB | 462,980 KiB |

最大入力は約24.2%短縮したが、11.111〜11.255秒で3回とも10秒を超えた。中間サイズ2件は約48.7%・50.5%短縮し、3回とも10秒以内。片方が短い経路のアルゴリズムは変えていないが、この比較では中央値が約5.6%遅く、改善とは扱わない。

出力が2^23項を超え2^24項以下で、両入力が2^21項を超え、2^22項ずつに分けた入力ブロック数の合計が4以上になる場合も16列方式へ切り替える。各列のNTT長は2^20。短い入力を固定して再利用できる場合などは、従来の分割方式を維持する。

- [各回の時間・RSS・入力とsourceのhash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-production-comparison.json)
- [測定した採用版](../benchmarks/experiments/large_radix8_medium.py)
- [当時の単独提出コード](https://github.com/lif4635/harurun-s-library/blob/c6e9e598a9e3d2fb4328d4a395ce403fd99ee143/verify/library_checker/solutions/convolution_mod_large.py)

## 8点単位の変換と回転係数の共有

2026-10-21、Git `0d89f8f`の提出コードと3つの試作を、公式最大入力`max_random_00`で各3回比較した。新しいPyPy 3.10プロセスを起動し、順序を入れ替え、全12回答を公式checkerで確認した。

| 実装 | 中央値 | 最大RSS |
| --- | ---: | ---: |
| 変更前の16列版 | 16.688秒 | 833,124 KiB |
| 8点単位の変換 | 15.426秒 | 833,912 KiB |
| 4点単位で回転係数を組み合わせる | 15.332秒 | 833,684 KiB |
| 8点単位で回転係数を組み合わせる | 12.672秒 | 833,584 KiB |

最後の案を採用する。変更前より約24.1%短縮し、メモリはほぼ同じ。採用候補の範囲は12.440〜13.149秒で、3回とも10秒を超えた。以前の測定日より変更前も遅く測れているため、別の比較記録の絶対時間を使って速度比を計算しない。

8点の変換に必要な係数をblockごとに先に計算する。内側のloopでは分配法則で積を展開し、中間値の剰余を取ってから別の係数を掛ける処理を避ける。長い入力を別の配列へ並べ替えず、16列の配置と入出力の仕様は維持する。共通の`NTT998`は変更しない。

- [各回の時間・RSS・hash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-distributed-comparison.json)
- [変更前の提出コード](../benchmarks/baselines/large_convolution_before_radix8.py)
- [比較した採用候補](../benchmarks/experiments/large_radix8_distributed.py)
- [8点単位・loop展開の3回比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-radix8-comparison.json)
- [8案の予備比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-transform-screen.json)

32列化、入力のlist化、積の逐次書き戻し、0部分と入力処理の統合、非負の中間値への統一は採用しない。予備比較は各1回なので、上表の3回比較と区別する。入力のlist化は最大RSSも996,796 KiBへ増えた。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/large_convolution_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_mod_large --cases max_random_00 random_00 random_01 small_and_large_01 --variant baseline=library_codex/benchmarks/baselines/large_convolution_before_radix8.py --variant candidate=verify/library_checker/solutions/convolution_mod_large.py --repeat 3 --seed 21993 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-production-comparison.json
```

## 8点変換導入時の公式全ケース

8点単位の変換と中間サイズの切り替えを組み込んだ提出コードを、PyPy 3.10・公式10秒制限で全54ケースに実行した。37件が制限内で通過、17件が時間超過。[当時のケース別判定とsource hash](https://github.com/lif4635/harurun-s-library/blob/c6e9e598a9e3d2fb4328d4a395ce403fd99ee143/verify/library_checker/results/convolution_mod_large.json)に記録する。

時間超過は`random_02`、`max_random_00`・`max_random_01`、`fft_killer_00`〜`fft_killer_09`、`max_ans_zero_00`、`all_same_00`〜`all_same_02`。時間超過した回の出力は検査していないため、この結果だけで全54入力の正答を確認したとはしない。

同じ提出コードで17件を診断上限120秒に延ばして各1回実行し、全回答が公式checkerに一致した。11.868〜13.592秒で、17件とも公式制限は超過。先の37件と合わせて全54入力の正答を確認できたが、制限内通過は37件のままとする。[診断記録](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-radix8-medium-diagnostic.json)には`withinOfficialTimeLimit: false`を残す。

## 16列への変更と正規化の前倒し

2026-10-21、直前の4列版と8列版、採用した16列版を公式最大入力`max_random_00`で各3回比較した。各回は新しいPyPyプロセスで、実行順序を入れ替えた。採用版は実際に配布する提出用standaloneを測っている。

| 実装 | 中央値 | 最大RSS |
| --- | ---: | ---: |
| 変更前の4列版 | 14.288秒 | 835,504 KiB |
| 8列・入力時に正規化 | 13.340秒 | 834,200 KiB |
| 採用した16列・入力時に正規化 | 13.064秒 | 833,356 KiB |

変更前より約8.6%短縮した。採用版の範囲は12.694〜13.289秒で、3回とも10秒を超えた。全9回答は公式checkerに一致した。最大RSSは約814MiBでほぼ変わらない。診断用の時間上限を120秒としており、公式制限内の通過を意味しない。

列数を16、各列のNTT長を2^21にする。評価点ごとに15次以下の多項式を掛け、16次以上の項を折り返す。通常の係数乗算を展開した方が、この環境ではKaratsubaで乗算を共有する版より速かった。逆NTTの正規化は片方の入力を格納する際に済ませ、出力全体の走査を一つ減らした。同じobjectを二乗する場合は順変換の共有を優先し、正規化を逆変換後に行う。短い入力・通常のNTT・従来のブロック経路と公開APIは変更していない。

- [採用版・8列・変更前の3回比較とhash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-sixteen-comparison.json)
- [16列と積共有の予備比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-sixteen-screen.json)
- [8列とKaratsubaの予備比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-eight-product-screen.json)
- [入力時の正規化の予備比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-eight-prescaled-screen.json)
- [剰余回数・逆変換の予備比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-arithmetic-screen.json)

予備比較は各1回。剰余の省略、逆変換への正規化の統合、Karatsubaの再帰的な展開は採用版を上回らなかった。下の各節は、それ以前の変更を測った記録として残す。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/large_convolution_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_mod_large --cases max_random_00 --variant baseline=library_codex/benchmarks/experiments/large_interleaved_ntt.py --variant eight=library_codex/benchmarks/experiments/large_eight_lanes_prescaled.py --variant candidate=verify/library_checker/solutions/convolution_mod_large.py --repeat 3 --seed 21984 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-sixteen-comparison.json
```

## 8点単位へ変更する前の公式全ケース

変更前の16列版を公式10秒制限で全54ケースに実行し、36件が制限内で通過、18件が時間超過だった。時間超過した入力は`random_01`、`random_02`、`max_random_00`、`max_random_01`、`fft_killer_00`〜`fft_killer_09`、`max_ans_zero_00`、`all_same_00`〜`all_same_02`。[当時の結果とsource hash](https://github.com/lif4635/harurun-s-library/blob/0d89f8fc46d734f9fe10155b9aff5a1f7d382c83/verify/library_checker/results/convolution_mod_large.json)に記録する。時間超過した回は出力を検査していないため、この記録だけで全54ケースの正答は確認できない。

続けて同じsourceの18件を診断上限120秒で各1回実行したところ、全回答が公式checkerに一致した。時間は10.534〜12.878秒で、18件とも公式10秒制限を超えている。先の36件と合わせて全54入力の正答は確認できたが、制限内通過は36件のままとする。[診断記録](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-sixteen-diagnostic.json)には`withinOfficialTimeLimit: false`を残し、全件検証の`failed`状態を上書きしない。

```sh
pypy3 library_codex/tools/check_library_checker.py test convolution_mod_large --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_probe.py convolution_mod_large --official /home/harurun/.cache/harurun-library-checker/problems --cases random_01 random_02 max_random_00 max_random_01 fft_killer_00 fft_killer_01 fft_killer_02 fft_killer_03 fft_killer_04 fft_killer_05 fft_killer_06 fft_killer_07 fft_killer_08 fft_killer_09 max_ans_zero_00 all_same_00 all_same_01 all_same_02 --repeat 1 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-sixteen-diagnostic.json
```

## 4列を同じ配列で処理する変更

2026-10-21、Git `767e374`の実装と公式最大入力`max_random_00`を各3回、新しいPyPyプロセスで比較した。

| 実装 | 中央値 | 最大RSS |
| --- | ---: | ---: |
| 変更前 | 15.666秒 | 763,748 KiB |
| 4列を交互に保持し通常の積を使用 | 13.964秒 | 834,904 KiB |
| 4列を交互に保持し積を共有 | 14.088秒 | 834,332 KiB |

通常の積を使う版を採用する。時間は約10.9%短縮し、最大RSSは約9.3%増加して約815MiBになった。全9回答が公式checkerに一致した。メモリ制限を実際に強制した測定ではない。

4列を別々に切り出さず、同じ評価点の4係数を隣接させる。共通NTTの内部処理に列数を渡し、同じ回転係数で4列を続けて処理する。列の変換後に32bit配列へ移す処理、逆変換前のlist化、最後の並べ替えをなくした。積は左の作業配列へ書き戻し、右の作業配列を解放してから逆変換する。公開APIは変えていない。

積の共有案は、通常の16回の係数乗算を10回へ減らすが、一時値と加減算が増える。同じ共通NTTで比較すると改善がなく、採用しない。変換だけを区画化する案、変換・積・逆変換を区画ごとにまとめる案、ゼロの最上段を省く案、手書きの入力解析も試し、採用版への上積みは確認できなかった。

- [通常積と積共有の3回比較とhash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-interleaved-product-comparison.json)
- [採用版の単独コード](../benchmarks/experiments/large_interleaved_ntt.py)
- [配列配置の予備比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-layout-screen.json)
- [配列確保とゼロ部分省略の3回比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-joint-comparison.json)
- [区画処理と入力解析の予備比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-fused-screen.json)
- [共通NTTへの統合時の比較](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-interleaved-ntt-comparison.json)

最初の配列統合案は約1018MiBまで増えたため採用せず、必要な長さを一度に確保する形へ直した。予備比較は各1回で、上表の反復比較とは区別する。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/large_convolution_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_mod_large --cases max_random_00 --variant baseline=library_codex/benchmarks/experiments/large_contiguous_standalone.py --variant karatsuba=library_codex/benchmarks/experiments/large_interleaved_karatsuba.py --variant candidate=library_codex/benchmarks/experiments/large_interleaved_ntt.py --repeat 3 --seed 21964 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-interleaved-product-comparison.json
```

## 4列版の最大入力以外の比較

通常のNTT・片方が短い経路も旧版と各3回比較し、18回答すべてが一致した。これらの経路に実質的な高速化はない。今回の公式比較は最大入力を含め4/54ケースで、全件通過ではない。

| ケース | 変更前 | 採用版 |
| --- | ---: | ---: |
| medium_00 | 0.086秒 | 0.082秒 |
| small_and_large_00 | 5.376秒 | 5.442秒 |
| small_and_large_01 | 6.395秒 | 6.423秒 |

[回帰比較の時間・RSS・hash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-interleaved-regression.json)。

## 測定環境

- 公式問題revision: `1814c4e5205517e368bb57a8d1127eb961cfeaae`。
- WSL2・AMD Ryzen 7 3700X・PyPy 3.10.14 / 7.3.16。
- 入出力は公式hashと照合。提出用standaloneを新しいPyPyプロセスで起動し、出力は公式checkerで検査する。
- 壁時計時間には起動・JIT・入出力を含む。RSSはGNU timeで測る。メモリ制限の強制、オンライン提出は行っていない。C++上位提出は方式の参照であり、同じ環境での速度比較ではない。
- 反復比較は選択したケースだけを測り、全件検査は54ケースを対象とする。診断用の時間上限と公式制限を区別する。

## C++上位提出を参考にした4列分割

2026-10-20に公式APIで、最新問題版のAC・C++23を時間順に取得した。[409657](https://judge.yosupo.jp/submission/409657)と[409616](https://judge.yosupo.jp/submission/409616)を確認し、順位・取得日時・source hashを[取得記録](../benchmarks/results/large_convolution_cpp_reference.json)へ保存した。他のC++言語IDを含めた全体順位とは区別する。

参照実装はNTTを途中で止め、葉で8次未満の多項式を掛ける。AVX2・専用の入出力・キャッシュ内での変換処理も使う。PyPy版では外部packageや機械語を追加せず、4次未満の多項式を掛ける部分を独立に実装した。

入力を添字の4剰余で分ける。

$$
A(x)=\sum_{r=0}^{3}x^r A_r(x^4)
$$

各列を長さSでNTTし、その評価点wごとに次を求める。

$$
\left(\sum_{r=0}^{3}a_r x^r\right)
\left(\sum_{r=0}^{3}b_r x^r\right)\bmod(x^4-w)
$$

4列を逆変換して交互に並べると元の積になる。最大入力ではS=2^23で、順NTTは8回、逆NTTは従来の7回から4回へ減る。入力・出力の意味は変えない。同じobjectの二乗では順NTTを4回へ減らす。従来のブロック分割の方が変換回数の少ない形では切り替えない。

変更前はGit `120cdb8`。各3回、新規PyPyプロセスで順序を入れ替え、全12回答を公式checkerで検査した。

| ケース | 変更前の中央値 | 採用版の中央値 | 変更前の最大RSS | 採用版の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| max_random_00 | 19.216秒 | 15.713秒 | 1,015,912 KiB | 1,025,648 KiB |
| small_and_large_00 | 5.167秒 | 5.304秒 | 461,228 KiB | 461,076 KiB |

この段階の最大ケースは約18.2%短縮。片方100項の経路は変更しておらず、この比較でも改善はない。最大RSSは約1002 MiBだった。現在は次節の保存方法へ変更している。

[各回の値とhash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-interleaved-comparison.json)・[変更前の単独コード](../benchmarks/baselines/large_convolution_before_interleaving.py)・[4列分割の試作](../benchmarks/experiments/large_convolution_interleaved.py)を保存した。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/large_convolution_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_mod_large --cases max_random_00 small_and_large_00 --variant baseline=library_codex/benchmarks/baselines/large_convolution_before_interleaving.py --variant candidate=verify/library_checker/solutions/convolution_mod_large.py --repeat 3 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-interleaved-comparison.json
```

## 逆変換後のメモリ削減

2026-10-21、Git `498a2ce`を基準に最大公式入力`max_random_00`で各3回比較した。逆NTTの結果を既存の`array("I")`へ戻し、一時listを解放してから返却listを作る。4列の値は出力の隣接する4要素へまとめて書く。返り値の型・順序・値とNTT回数は変えない。

| 実装 | 中央値 | 最大RSS |
| --- | ---: | ---: |
| 変更前 | 16.688秒 | 1,025,836 KiB |
| 保存方法変更後 | 16.290秒 | 763,576 KiB |

最大RSSは約25.6%減少。速度差は約2.4%で、初回は変更後の方が遅かったため、速度の大幅改善とは扱わない。メモリ制限ぎりぎりの状態を改善する目的で採用した。全6回答が公式checkerに一致した。前節とは別の測定であり、日をまたいだ絶対時間の差を速度比には使わない。

[各回の時間・RSS・hash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-contiguous-comparison.json)、[変更前の単独コード](../benchmarks/baselines/large_four_lanes_standalone.py)、[比較した単独コード](../benchmarks/experiments/large_contiguous_standalone.py)を保存している。

採用版の提出コードでも`example_00`、`example_01`、`small_15`、`medium_00`、`small_and_large_00`、`small_and_large_01`を各1回検査し、全6回答が一致して10秒以内だった。[選択検査の記録](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-contiguous-probe.json)。最大入力との比較を含め7/54ケースの確認で、全件通過ではない。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/large_convolution_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_mod_large --cases max_random_00 --variant baseline=library_codex/benchmarks/baselines/large_four_lanes_standalone.py --variant contiguous=library_codex/benchmarks/experiments/large_contiguous_standalone.py --repeat 3 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-contiguous-comparison.json
```

## 初期実装

以下は変更前の実装の記録で、採用版との同時比較ではない。

`example_00`・`example_01`・`small_15`・`medium_00`は通過。`max_random_00`は10秒でtimeoutした。

診断上限を300秒へ延ばした同じ最大ケースは17.584秒で出力が一致した。最大RSSは1,156,148 KiB。入力は2^24項の列が2本、出力は2^25-1項。

関数の前後を計時した別実行では、全体18.025秒、入力2.006秒、順NTT6.857秒、逆NTT5.948秒、畳み込み全体15.021秒だった。順変換8回・逆変換7回であり、ブロックの組ごとに変換し直してはいない。この内訳は計測用wrapper付きのimport実行で、standaloneの時間とは区別する。

- [10秒制限の選択検査](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-probe.json)
- [最大ケースの延長測定](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-extended-probe.json)
- [処理時間の内訳](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-profile.json)
- [初期実装の単独コード](../benchmarks/baselines/large_convolution_unplanned.py)

## 比較した変更

同じ最大ケースを各実装3回、新しいプロセスで順序を入れ替えて測った。全出力が公式checkerを通過した。

| 比較 | 変更前の中央値 | 変更後の中央値 | 変更前の最大RSS | 変更後の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| 回転係数表の共有 | 17.589秒 | 17.142秒 | 1,147,664 KiB | 1,215,376 KiB |
| 出力の逐次追加とブロック解放 | 18.071秒 | 19.257秒 | 1,154,796 KiB | 990,792 KiB |

係数表の共有は速度差が小さく、メモリが増えたため不採用。[比較結果](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-plan-comparison.json)と[試作コード](../benchmarks/experiments/large_convolution_planned.py)を残す。

ブロック解放は速度と引き換えにメモリを減らす変更として採用した。[比較結果](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-memory-comparison.json)と[その段階の単独コード](../benchmarks/experiments/large_convolution_release_only.py)を保存した。その後、作業配列の再利用、片方が短い場合の逐次処理を加えた。次の表は4列分割を加える前の測定で、上の旧実装との同時比較ではない。

## 4列分割を加える前の選択検査

公式7ケースを3回ずつ、計21回測定し、すべての出力が公式checkerと一致した。10秒制限を満たしたのは最大ランダム以外の6ケース。最大ランダムは3回とも制限超過である。

| 公式ケース | 入力長 | 中央値 | 最大RSS |
| --- | --- | ---: | ---: |
| max_random_00 | 2^24と2^24 | 20.231秒 | 1,015,008 KiB |
| small_and_large_00 | 100と2^24 | 5.602秒 | 461,176 KiB |
| small_and_large_01 | 1000と2^24 | 6.229秒 | 462,488 KiB |

残りは`example_00`・`example_01`・`small_15`・`medium_00`。最大ケースの時間は18.860〜20.343秒にばらついた。速度優先の旧試作へ戻すだけでも10秒には届かない。

[全21回の値・source hash・入力hash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-current-probe.json)を保存した。公式全件の検証結果や、全件通過済み問題のベンチマーク一覧には混ぜていない。

この段階では通常のquick検査339件と性能回帰検査を通過した。

## 2026-10-20の選択検査

最大ランダムと`small_and_large_00`の反復比較に加え、`example_00`、`example_01`、`small_15`、`medium_00`、`small_and_large_01`を各1回検査した。5回答とも公式checkerに一致し、10秒以内。`small_and_large_01`は6.166秒・462,304 KiBだった。[選択検査の記録](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-optimized-probe.json)。

今回確認した入力は合計7/54ケース。最大ランダムは制限超過で、公式全件の通過は確認していない。専用testは、4列分割の単純解との比較、変換回数、負の係数、入力の非破壊、単独bundleを含み、GF(2^64)畳み込みと合わせて18件が成功した。

2026-10-20の全体回帰testは1,289件成功し、full性能回帰検査も通過した。API・catalog・提出コード・Codon索引の同期検査と説明品質監査も成功した。

## 再実行

リポジトリ直下で実行する。診断用に上限を延ばしても、公式制限超過の判定は残る。

```sh
pypy3 library_codex/benchmarks/official_probe.py convolution_mod_large --official /home/harurun/.cache/harurun-library-checker/problems --cases example_00 example_01 small_15 medium_00 small_and_large_01 --repeat 1 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-optimized-probe.json
```

## 残る問題

- 大規模畳み込みは全54ケースを公式10秒制限で検査済みだが、17件の時間超過が残る。
- 最大入力を関数別に計測した1回の内訳は、入力3.308秒、順変換2回で4.487秒、逆変換1回で3.322秒、変換以外の積処理1.140秒、その他の配列処理・出力1.598秒。[計測記録](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-radix8-profile.json)はimport経由の計測用実行で、提出用standaloneの速度比較とは区別する。
- `convolution_F_2_64`は別の問題。整数を2^64で割った余りの畳み込みでもnim積でもなく、二元体上の既約多項式による剰余体を使う。加法FFTを使うPyPy版は`BinaryFieldConvolution`へ追加し、全51ケースがローカルの公式制限内で通過した。[検証記録](BINARY_FIELD_CONVOLUTION_BENCHMARK.md)を参照。

## 参照

- [大規模畳み込みの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/convolution/convolution_mod_large/sol/correct.cpp)
- [GF(2^64)畳み込みの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/convolution/convolution_F_2_64/sol/correct.cpp)
