# 最大流の軽量化と最小費用b-flowの検査

2026-10-11 JST。PyPy 3.10.14 / 7.3.16、WSL Ubuntu、Ryzen 7 3700X。オンライン提出は行わない。

## ARC232 AでのACLとの差

ユーザーの[ARC232 A](https://atcoder.jp/contests/arc232/tasks/arc232_a)用コードにあるMaxFlowGraphは変更前のライブラリと同じ実装だった。比較対象はC++版ではなく、`from atcoder.maxflow import MFGraph`で使う[Python版ACL](https://github.com/not522/ac-library-python/blob/master/atcoder/maxflow.py)。ローカルのac-library-python 0.1.0のsourceを確認し、hashを測定結果へ保存した。

どちらも非再帰Dinicで、Python版ACLも増加路を1本ずつ流す。違いは次のとおり。

- 旧版はBFSで到達可能な全頂点を走査する。ACLは終点を発見したら止める。
- 旧版は始点からDFSする。ACLは終点から逆向きにDFSし、始点側の距離が1小さい残余辺をたどる。
- 旧版は進むたびに経路の最小容量を更新し、頂点・辺位置のtupleを積む。ACLは経路が見つかってから最小容量を求め、辺への参照を積む。
- 旧版の逆辺は二段のlist添字から引く。ACLは辺objectが逆辺objectを直接参照する。objectを使うことだけで遅いとは判断できない。

この呼出しは整数容量で`flow(0, n, 2)`なので、成功する増加は高々2回。経路ごとにstackを作る回数だけを大きな速度差の原因にはできない。両方式とも、この流量上限では流量計算は`O(V+E)`に収まる。グラフの構築・sortは別。

## 比較方法

ユーザーの`solve`と同じ`ml`・`mr`・`ng`による辺生成と追加順を再現し、次の4入力を作った。区間は実装内の半開形式。各`N=500000`で、問題の制約内。

- `short_interval`: 区間`[0, 2)`を一つ。長い経路になる。
- `whole_interval`: 区間`[0, N)`を一つ。終点へ直接入る辺が多数ある。
- `windows`: 長さ32の区間を左端0から一つずつずらす。各層での探索が重なる。
- `infeasible`: `[0, 2)`・`[1, 3)`・`[0, 3)`。流量2には届かない。

AtCoderの非公開テストではなく、生成入力である。問題の解法自体の証明やオンライン実行時間の再現を主張しない。

各5回、新しいPyPy processで実行し、順序を固定seedで入れ替えた。グラフ構築と`flow`を別に測定し、辺容量・流量保存則・流量上限未到達時のカット証明を毎回確認する。入力hash・source hash・各回の値は[結果JSON](../benchmarks/results/flow.json)。全process時間と最大RSSには入力の読込・検証も含み、表のflow時間には含まない。特にRSSはflow構造だけのサイズではない。CPU周波数やWindowsの他アプリは固定していない。

## 探索の切り分け

秒、flow部分の中央値。

| 入力 | 旧版 | BFS早期終了のみ | 早期終了＋逆向きDFS | Python版ACL | 採用版 | PushRelabel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| short_interval | 0.4371 | 0.4069 | 0.4725 | 0.4786 | 0.2318 | 0.2157 |
| whole_interval | 0.3978 | 0.0551 | 0.0586 | 0.0162 | 0.0040 | 0.1573 |
| windows | 0.8190 | 0.7314 | 0.3411 | 0.2962 | 0.1576 | 0.1510 |
| infeasible | 0.2350 | 0.2361 | 0.3677 | 0.3206 | 0.1693 | 0.2003 |

逆向きDFSの比較版は、旧版の辺listを維持し、容量の最小値を経路発見後に求める変更も含む。探索方向だけの効果を完全に分離した測定ではない。

`whole_interval`ではBFSの早期終了が大きく効いた。`windows`ではそれだけでは十分でなく、逆向き探索とstack処理の変更でACLに近づく。長い経路や不可能な入力ではACLが旧版より遅い場合もあり、ACLが常に速いという結果ではない。

## 採用した変更

- 辺ごとの小さいlistと位置tupleを、整数ID・行先list・残余容量listへ置き換えた。逆辺は`edge ^ 1`。
- BFSは終点の距離が決まった段階で打ち切る。
- 終点側からの非再帰DFSで、複数の子から戻った流量をまとめる。[C++版ACL](https://github.com/atcoder/ac-library/blob/master/atcoder/maxflow.hpp)のblocking flow集約も参考にした。Python版ACLと同じコードへの置換ではない。
- `flow`・`get_edge`・`change_edge`・残余グラフ・カット・流量分解の呼出し方を保った。内部`graph`の要素は辺listから整数IDへ変更した。

`windows`のflow部分は旧版の約5.2倍速く、構築の中央値も0.2553秒から0.1632秒へ短縮した。Python版ACLは構築0.2564秒、flow0.2962秒。生成・sort・入出力を含むAtCoder提出全体の速度ではない。

| 入力 | 旧版 構築秒 | ACL 構築秒 | 採用版 構築秒 | 旧版 RSS KiB | ACL RSS KiB | 採用版 RSS KiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| short_interval | 0.4824 | 0.3910 | 0.2550 | 742048 | 722256 | 576632 |
| whole_interval | 0.5781 | 0.3981 | 0.2682 | 793092 | 628944 | 504372 |
| windows | 0.2553 | 0.2564 | 0.1632 | 453624 | 436152 | 352448 |
| infeasible | 0.4268 | 0.3679 | 0.2586 | 675304 | 669392 | 542812 |

## 他のグラフ形状

既存の生成器を使った。頂点数・辺数・seedはJSONに保存。秒、flow部分の中央値。

| 入力 | 旧版 | ACL | 採用版 | PushRelabel |
| --- | ---: | ---: | ---: | ---: |
| sparse | 0.0216 | 0.0127 | 0.0133 | 0.0354 |
| dense | 0.0364 | 0.0334 | 0.0287 | 0.0191 |
| layered | 0.0403 | 0.0424 | 0.0321 | 0.0400 |
| grid | 0.0157 | 0.0151 | 0.0132 | 0.0191 |
| bipartite | 0.0212 | 0.0201 | 0.0241 | 0.0218 |
| dead_end | 0.0025 | 0.0004 | 0.0002 | 0.0006 |

小さい二部グラフでは採用版が約14%遅い。小入力はJITの影響も大きく、数ミリ秒の差を一般化しない。PushRelabelが勝つ入力もあるので、これを削除したり一律にDinicへ統合したりしていない。

最初の3回試測は[flow_initial.json](../benchmarks/results/flow_initial.json)。その時の測定scriptは`benchmarks/experiments/flow_initial.py`へ同じ内容で保存した。再現時はそれを`benchmarks/flow.py`の位置に置く。旧ライブラリは`benchmarks/baselines/max_flow.py`に保存した。

## 最小費用b-flow

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`の54ケースを通過。空、負の費用・流量下限、自己ループ、大きい容量、実行不可能、逐次最短路に厳しい入力を含む。累計193/253問題・4578ケース、未対応60問題。ローカルの公式checkerによる検証であり、オンラインACではない。メモリ制限は強制していない。

cost scalingの倍率を`V`から`V+1`にした。最終段階のepsilonが1でも、単純閉路の長さは高々Vであり、負の閉路が残らないための厳密な余裕を持たせる。これは理論上の境界を安全にする修正で、今回旧版の誤答を観測したという意味ではない。

公式全件後、遅かった3ケースを各5回測り、[標準ベンチマーク](../../verify/library_checker/benchmarks/min_cost_b_flow.json)へ保存した。比較対象は取得時の最新問題版AC・PyPy・時間昇順の先頭[389037](https://judge.yosupo.jp/submission/389037)。全文を確認してから同じ公式入力で測定し、[比較JSON](../benchmarks/results/min_cost_b_flow_comparison.json)へ保存した。

| 公式入力 | ライブラリ 秒 | 上位PyPy 秒 | ライブラリ RSS KiB | 上位PyPy RSS KiB |
| --- | ---: | ---: | ---: | ---: |
| near_maximum_00 | 0.1512 | 0.1404 | 64672 | 63604 |
| goto_07 | 0.1711 | 0.1513 | 64296 | 63424 |
| anti_ssp_00 | 0.1240 | 0.1260 | 62564 | 62448 |

起動・JIT・入出力込みの中央値。最初の2件では約8〜13%の差が残る。最後はほぼ同程度で、数ミリ秒の差を優劣の根拠にしない。参照は補助頂点への高費用辺で初期流を作るcost scaling、ライブラリは最大流で実行可能流を作ってからcost scalingする。参照の方式への全面置換はしていない。

## 正しさの検査

- PyPyの全985テストが通過。API説明の監査は0件、6245関数の直接・相互再帰は検出されなかった。
- `prepare_checkpoint.py --profile full`の同期・全テスト・全性能回帰検査が通過。性能閾値は緩めていない。
- 最大流は小さいグラフの全カット列挙と比較。追加辺・小分けの流量制限・0制限・再呼出し・自己ループ・平行辺を確認した。
- 20万頂点の鎖で再帰に依存しないこと、70桁の容量でも正確な整数を返すことを確認した。
- 最小費用b-flowは小さい整数流量の全列挙と比較し、最適費用・流量保存則・相補性を確認した。費用合計が-1の閉路は、頂点順を変えて検査した。

## 再実行

```sh
pypy3 library_codex/benchmarks/flow.py --repeat 5
pypy3 library_codex/tools/check_library_checker.py test min_cost_b_flow --official /home/harurun/.cache/harurun-library-checker/problems --reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py min_cost_b_flow --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/library_checker.py fetch --problem min_cost_b_flow --top 1 --cache ../lc-matching-reference
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/min_cost_b_flow-pypy3.json --reviewed 389037 --problem /home/harurun/.cache/harurun-library-checker/problems/graph/min_cost_b_flow --cases near_maximum_00 goto_07 anti_ssp_00 --variant library=verify/library_checker/solutions/min_cost_b_flow.py --repeat 5 --output library_codex/benchmarks/results/min_cost_b_flow_comparison.json
```

fetch後にsourceを確認する。順位や参照IDは取得時点のもの。`flow.py`には比較用のac-library-pythonを要するが、ライブラリ本体と提出コードには不要。
