# FPS合成の処理別計測とC++実装の調査

2026-09-30 JST。変更前revisionは`ace5a01f428420a1454ff2008c6bbd919f7ebf80`。調査後に`fps998/Composition.py`を最適化した。commit・公開はまだ行っていない。

## 追加改善: NTTの係数再利用と部分逆変換

N=8000向けの調整ではなく、Large問題の最大サイズ131072を優先した。公開APIは変更していない。

### C++実装から取り入れたこと

[C++提出247871](https://judge.yosupo.jp/submission/247871)の`extend_rt`は、変換で繰り返し掛ける係数を表として保持している。Python版も`_ntt_plan`で順変換・逆変換の係数を一度ずつ作り、合成の全段で使い回すようにした。長さ4H用の表は長さ2Hの変換にも使える。

表は32bitのarrayで保持し、合成1回の終了時に解放する。グローバルな巨大cacheは追加しない。通常の`ntt`・`intt`・`multiply`は表を作らず従来の計算経路を使う。前計算を利用するかどうかの分岐は係数ごとの内側のloopには入れない。

さらに、合成が逆NTTの出力の一部しか使わないことを利用した。必要なindexで特定のbitが0になるため、逆変換の幅がそのbitを越えた段では、不要なindexに属するbutterflyを省ける。この段以降はbitの異なるindex同士を混ぜないので、必要な係数には影響しない。除算による正規化も、取り出す係数だけに行う。

これはC++版のAVX2命令をPythonへ移したものではない。前計算の再利用はC++版を参考にし、部分逆変換は現在の係数配置に合わせて追加した。AVX2・Montgomery演算・[maspypyの二方向NTTとdoubling](https://maspypy.github.io/library/poly/composition.hpp)の全面移植は実施していない。

### 最大サイズでの比較

同一入力・同一PyPy・別process、起動と入出力を含む。実行順を入れ替えた5回の中央値。`before`は直前の改善済み版で、最初の約2.9秒の版ではない。

| 入力 | 直前版 | 今回 | 比較PyPy 367593 | 比較先からの短縮 |
| --- | ---: | ---: | ---: | ---: |
| 密 | 2.561秒 | 2.211秒 | 2.736秒 | 19.2% |
| 内側が疎 | 2.272秒 | 1.975秒 | 2.643秒 | 25.3% |

別seedで3回ずつ再測定した結果は次のとおり。

| 入力 | 直前版 | 今回 | 比較PyPy 367593 | 比較先からの短縮 |
| --- | ---: | ---: | ---: | ---: |
| 密 | 2.496秒 | 2.213秒 | 2.574秒 | 14.0% |
| 内側が疎 | 2.230秒 | 1.954秒 | 2.556秒 | 23.6% |

密入力の最大RSSは5回測定で直前版137.3MiB、今回141.4MiB、比較先428.0MiB。今回の改善はメモリを約4MiB増やしている。

生データ: [5回測定](../benchmarks/results/library_checker/composition-planned-131072.json)、[別seed確認](../benchmarks/results/library_checker/composition-planned-confirm.json)、[関数別内訳](../benchmarks/results/library_checker/composition-planned-profile.json)。前計算は内訳の代表実行で合計約0.008秒。NTTの呼出し数と配列長は直前版と同じだが、表の再計算と逆変換内の演算を削減している。

### 試した案と他の演算への影響

- 正規化する係数を減らすだけの案は、密入力2.543秒→2.541秒、疎入力2.159秒→2.223秒で、単独の改善とは判断しなかった。
- 係数表を毎回作らず使い回す試作は、密入力2.543秒→2.320秒、疎入力2.220秒→2.023秒。
- その試作へ部分逆変換を加えると、密入力2.277秒→2.201秒、疎入力1.971秒→1.864秒。試作の表は変換長別のcacheだったため、最終実装では合成1回につき2表へ整理してから測り直した。

上記はそれぞれ同じ比較run内の中央値。異なるrunの秒数を直接つないで改善率を計算しない。[試行記録](../benchmarks/results/library_checker/composition-ntt-trials.json)に各案のsource hashと測定結果を保存している。

共有NTTを変更したため、通常畳み込みも最大入力で確認した。密入力0.743秒→0.638秒、疎入力0.467秒→0.460秒、片側7項0.221秒→0.213秒。大きな性能退行はこの測定では見られなかったが、ばらつきがあるため小さな改善は断定しない。[生データ](../benchmarks/results/library_checker/convolution-after-planned-ntt.json)。

検査には、大小の変換長で同じ係数表を使う場合、表が書き換わらないこと、すべての保持bitについて必要な係数が完全な逆NTTと一致することを追加した。単純解比較・合成逆関数・非0定数項・standaloneの既存検査も引き続き実行する。

この合成・NTT変更の後、full検査は721 tests passed。API・catalog同期、説明監査、再帰監査も成功した。後続の疎FPS・SPS変更の検証は[疎FPS・2変数FPS・SPSの調査](SERIES_OPTIMIZATION.md)に分けて記録する。

```sh
pypy3 library_codex/benchmarks/library_checker.py compare --snapshot ../lc-comparison/composition_of_formal_power_series_large-pypy3.json --reviewed 367593 --size 131072 --repeat 5 --families dense sparse_inner --baseline ../lc-comparison/composition-paired-before.py --no-variants --output library_codex/benchmarks/results/library_checker/composition-planned-131072.json
pypy3 -m pytest -q library_codex/verify/fps998/test_composition.py library_codex/verify/convolution/test_ntt998.py library_codex/verify/test_composition_profile.py
pypy3 library_codex/tools/check_library.py --profile full --skip-benchmarks
```

## 最初の改善と比較結果（記録）

- 戻り側の順NTTを長さ4Hから2Hへ短縮。隣り合う周波数値と掛け合わせて長さ4Hの逆NTTへ渡す。
- 係数の配置を変更し、周波数配列の反転と位相補正を省略。
- 内側の定数項を0にして処理し、最下段の逆数・畳み込みを省略。非0の定数項は外側のTaylor shiftで扱う。
- 末尾の0を除いてから判定し、恒等写像や単項式への合成は線形時間で処理。
- 公開API、引数の切り詰め規則、再帰を使わない構造、変換結果を32bitのarrayへ保存する方針は維持。

WSL2、PyPy 3.10.14 / 7.3.16。同じ入力を別processで3回ずつ実行した中央値。起動・入出力を含む。計測順は各回で入れ替え、他の検査と同時実行していない。

| N | 入力 | 変更前（秒） | 採用版（秒） | 参照PyPy（秒） |
| ---: | --- | ---: | ---: | ---: |
| 8000 | 密 | 0.2600 | 0.2319 | 0.1946 |
| 8000 | 内側が疎 | 0.2193 | 0.2032 | 0.1995 |
| 8000 | 恒等写像 | 0.2267 | 0.0821 | 0.2071 |
| 65537 | 密 | 2.6599 | 2.4478 | 2.5055 |
| 65537 | 内側が疎 | 2.4714 | 2.2119 | 2.6494 |
| 65537 | 恒等写像 | 2.7557 | 0.0984 | 2.7541 |
| 131072 | 密 | 2.8904 | 2.5539 | 2.6978 |
| 131072 | 内側が疎 | 2.8222 | 2.2432 | 2.6690 |
| 131072 | 恒等写像 | 2.4704 | 0.1077 | 2.5708 |

参照は取得時の各問題のPyPy最速提出。通常版は[398299](https://judge.yosupo.jp/submission/398299)、Large版は[367593](https://judge.yosupo.jp/submission/367593)。この入力でのローカル比較であり、公式全testの再実行・提出や、すべての入力で最速という主張ではない。N=8000の密入力にはまだ差がある。

N=131072の密入力は約11.6%短縮。最大RSSは変更前138.5MiB、採用版137.1MiB、参照423.2MiBだった。
先に試した位相補正付きの案は同じ比較で2.6021秒、140.4MiB。補正を省く案を採用した。生データ内の`candidate`はこの不採用案、`before`は変更前、`library`が採用版。

生データ: [8000](../benchmarks/results/library_checker/composition-optimized-8000.json)、[65537](../benchmarks/results/library_checker/composition-optimized-65537.json)、[131072](../benchmarks/results/library_checker/composition-optimized-131072.json)。各実装のsource hash、入力・出力hash、各回の時間、最大RSSを記録した。外部提出のsourceは含めない。

変更後の[関数別計測](../benchmarks/results/library_checker/composition-optimized-profile.json)では、長さ524288と262144の順NTTがそれぞれ17回。旧版の長さ524288の順NTT34回から、半分を短くできた。関数だけの中央値は2.589秒で、上の提出全体の測定とは別の実行。計測あり2.562秒との差もあるため、微小な差は断定しない。

正しさは専用の`verify/fps998/test_composition.py`で確認する。1200件の単純解比較、300件の合成逆関数の両方向照合、200件の合成逆関数の単純解比較に加え、64前後・2の冪前後、負数・法の倍数、定数項非0、tuple入力、入力非破壊、単項式、Fibonacci係数との4097項照合、単独processでのbundle実行を含む。既存の合成testはカテゴリ一括fileから移し、重複させない。

変更後の`check_changed.py`は成功。関連86 tests、API reference・catalog同期、説明監査0件、変更moduleの8関数の再帰監査を通過した。catalogは363 modules中1 moduleのみ再生成。全libraryのfull検査、公式judgeへの提出、push・サイト公開は今回は行っていない。

再測定は次で行う。baselineは今回の変更前に生成したstandalone codeで、公開moduleへの互換aliasではない。後日比較する場合も、書き換える前に生成したcodeを保存して渡す。`--candidate`で試作案を追加でき、`--no-variants`で問題側の補助variantを除外できる。

```sh
pypy3 library_codex/benchmarks/library_checker.py compare --snapshot ../lc-comparison/composition_of_formal_power_series_large-pypy3.json --reviewed 367593 --size 131072 --repeat 3 --baseline ../lc-comparison/composition-before.py --no-variants --output library_codex/benchmarks/results/library_checker/composition-optimized-131072.json
pypy3 library_codex/benchmarks/profile_composition.py --size 131072 --repeat 3 --output library_codex/benchmarks/results/library_checker/composition-optimized-profile.json
pypy3 -m pytest -q library_codex/verify/fps998/test_composition.py library_codex/verify/test_composition_profile.py library_codex/verify/test_library_checker_benchmark.py
```

以下は変更前の調査記録。「現在」は調査時点の旧版を指す。

## 測定で分かったこと

N=131072、998244353、密な係数、seed=92471。前回の[問題別比較](LIBRARY_CHECKER_PROBLEMS.md)と同じ入力。
WSL2、PyPy 3.10.14 / 7.3.16。今回は合成関数の呼出しだけを測り、入力生成・import・入出力を除外した。
別processで計測なし・関数単位の計測ありを交互に3回ずつ実行。cProfileは使わず、処理をまとめた関数の前後で時間を測った。

- 計測なしの中央値: 2.930秒。
- 計測ありの中央値: 2.994秒。
- 以下は計測ありの中央値に対応する1回の内訳。計測による差は約2.2%であり、割合は目安。
- 全実行で出力hashが一致。小入力は独立した単純解とも一致。

| 処理 | 秒 | 合計に対する割合 |
| --- | ---: | ---: |
| 合成の各段から直接呼ぶ順NTT | 1.440 | 48.1% |
| 同じく逆NTT、正規化を含む | 1.199 | 40.0% |
| 最下段の逆数・畳み込み | 0.070 | 2.3% |
| 保存用arrayへの変換 | 0.029 | 1.0% |
| 周波数配列の区間反転 | 0.013 | 0.4% |
| その他の配列構築、係数積、コピー、制御など | 0.243 | 8.1% |

最下段の畳み込み内のNTTは「最下段」に含め、上2行へ二重計上しない。
JSONの`inclusiveSeconds`には子関数の時間も含まれる。内訳の集計には`exclusiveSeconds`を使う。

配列の反転や保存形式だけを変えることは優先度が低い。大半を占める変換の長さ・回数と、NTT内部の定数倍が主な対象になる。
これは現在の実装の内訳であり、前回のPyPy参照提出との約12%の差を個別要因へ分解した測定ではない。

## 変換長と回数

HをN以上の最小の2の冪とする。今回はH=131072、分割は17段。
最下段の畳み込みを除くと、各段で次を実行していた。

| 部分 | 現在 | C++提出247871のソース上の構成 |
| --- | --- | --- |
| 下降 | 長さ4Hの順変換、長さ2Hの逆変換 | 同じ長さ |
| 上昇 | 長さ4Hの順変換、長さ4Hの逆変換 | 長さ2Hの順変換、長さ4Hの逆変換 |

実測した現在の直接呼出しは、長さ524288の順変換34回、長さ262144の逆変換17回、長さ524288の逆変換17回。
C++版では、戻り側の係数を短い配列で変換し、その結果と保存しておいた周波数値を組み合わせて長い配列を作る。
現在のように係数の間へゼロを挟んでから長さ4Hで順変換する必要を避けている。

長さLの変換の仕事量を`L log2 L`とした場合、この変更は各段のNTT仕事量を約15%減らす見積もりになる。
実際のPython実装で15%速くなると保証する値ではない。添字・周波数順・係数配置も変わるので、NTTの引数長だけを半分にして済む変更ではない。

## 参考にしたC++実装

### Library Checker上位

公開APIから`cpp`、AC、最新問題version、実行時間昇順で2件取得した。

- [247871](https://judge.yosupo.jp/submission/247871): 取得時点のC++23最速、judge上0.149秒、cmk666。
- [247851](https://judge.yosupo.jp/submission/247851): 同0.150秒。合成の構成はほぼ同じ。

`comp_impl`を確認した。合成の戻り側では`dif(e, 2H)`の後に周波数の隣り合う組から長さ4Hの配列を作り、逆変換する。
最速版はAVX2、32bit係数、Montgomery剰余演算、整列した配列と連続コピーも使用する。
これらのCPU命令による高速化を純粋なPythonへそのまま移して同じ効果が出るとは考えない。
とくにMontgomery演算はPythonで書くと演算数が増える可能性があるため、別途比較が必要。

C++は今回ソース調査のみで、ローカルでコンパイル・時間比較していない。judge上の0.149秒を、ローカルPyPyの約3秒と割り算しない。
取得した提出ソースはrepository外の比較キャッシュに保持し、再配布しない。

### Nyaanとmaspypy

- [Nyaanの合成](https://nyaannyaan.github.io/library/fps/fps-composition.hpp.html): 現在の実装と同じ、下降の変換結果を戻りで再利用する構成。大枠をすでに取り入れているため、単純に移し直しても大きな改善にはならない。
- [maspypyの合成](https://maspypy.github.io/library/poly/composition.hpp): `composition_0_ntt`は2方向の変換、変換のdoubling、転置NTTを使い、各段の縦横サイズに応じて処理順を選ぶ。毎段一律に長さ4Hで変換する現在の方式とは異なる候補。ただし細かい変換や配列の取り出しが増えるので、PyPyでの優劣は未検証。

## 優先順位

1. 密入力の合成は、C++上位のように戻り側の順変換を半分の長さにできる構成を試す。メモリ量も測る。
2. 合成で繰り返し使うNTT長・係数分布でNTT本体を比較する。C++向けの剰余演算を無条件に移植しない。
3. maspypy型は別の試作として、同じ入力で比較する。書き換えるだけで速いとはしない。
4. 恒等写像などのゼロ末尾の取りこぼしは、上記と独立した局所修正候補。密入力の速度改善とは区別する。

配列反転・array変換・再帰の有無から手を付ける根拠は今回弱い。最下段の計算も約2.3%で、最優先ではない。

## 再実行

```sh
pypy3 library_codex/benchmarks/profile_composition.py --size 131072 --repeat 3 --output library_codex/benchmarks/results/library_checker/composition-optimized-profile.json
pypy3 -m pytest -q library_codex/verify/test_composition_profile.py
```

[生の計測結果](../benchmarks/results/library_checker/composition-profile.json)に各回の時間、入力・出力・standaloneのhash、変換長別の呼出し回数を保存した。
このfileは変更前の記録として保持する。上のcommandは現在のsourceを測定し、別fileへ保存する。
