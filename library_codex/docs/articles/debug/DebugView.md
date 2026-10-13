# 実行中の状態を右側に表示する

## 主な機能

Haru Desk 1.36以降を入れたVS Codeで、Pythonから書き出した状態を右側のDebugパネルへ自動表示する。手動でのコピーや貼り付けは不要。

- `dump_flow(g, s, t)`：MaxFlowGraph・PushRelabel・MinCostFlowGraphの容量、流量、順方向と逆方向の残余容量を表示する。実行可能解を得たMinCostBFlowにも対応する。
- `dump_graph(n, edges)`：辺listからグラフや木を表示する。重み、多重辺、自己ループ、有向辺に対応する。
- `dump_array(values)`：列、または`tolist()`を持つBIT・SegTreeなどの論理値を添字付きで表示する。

フロー・グラフの書き出しは`O(V + E + B)`、配列は列挙時間に加えて`O(B)`。`B`は文字列化した出力サイズ。計算本体へ記録処理を追加せず、呼び出した時点だけを書き出す。

## 使い方

```python
from library_codex.graph_flow.MaxFlow import MaxFlowGraph
from library_codex.debug.DebugView import dump_flow, dump_graph, dump_array

g = MaxFlowGraph(4)
for u, v, capacity in [(0, 1, 3), (0, 2, 2), (1, 2, 1), (1, 3, 2), (2, 3, 3)]:
    g.add_edge(u, v, capacity)
g.flow(0, 3)
dump_flow(g, 0, 3)
dump_graph(4, [(0, 1), (1, 2), (1, 3)], name="tree")
dump_array([4, 1, 7], name="values")
```

VS Codeで開いたworkspace内を作業directoryとして実行する。通常のターミナル、Haru DeskのRun、デバッガのいずれでも同じ形式で使える。戻り値は保存したJSONの絶対pathで、標準出力には何も追加しない。

同じprocess・同じ`name`の出力は同じfileを置き換える。違う`name`ならパネル上の選択欄で切り替えられる。残すのは各fileの最新状態で、全呼び出しの履歴ではない。

`labels`には頂点順の表示名、`positions`には頂点順の`[x, y]`を渡せる。座標のyは下向き。グリッドでは`positions=[(v % width, v // width) for v in range(n)]`を指定すると元の配置で表示できる。更新時にはドラッグした配置を維持し、`Reset view`で指定座標に戻す。

## 注意点

- JSONは作業directoryの`.haru-dump`へ一時fileを経由して保存する。Gitへ入れない場合は`.gitignore`へ`.haru-dump/`を追加する。
- 保存先は`directory`、環境変数`HARU_DUMP_DIR`、`.haru-dump`の順で選ぶ。自動表示の対象は開いたworkspace内の`.haru-dump`directoryだけ。
- Haru Deskが有効な、信頼済みworkspaceでPython fileを開いてから実行する。拡張の起動前に保存した古いfileは自動表示しない。
- 最大500頂点・3000辺・10000配列要素・2 MiB。上限超過や不正な入力は例外とし、以前のJSONを残す。巨大な入力は小さな再現ケースで調べる。
- `Residual`は正の残余容量を持つ辺だけを表示する。逆辺は破線。元の辺番号は詳細欄で確認できる。
- 最小カットと表示するのは、通常の最大流で流量保存を満たし、残余グラフでsinkへ到達できない場合だけ。流量上限で途中停止した結果や`change_edge`後の不整合な状態を最小カットと呼ばない。
- MinCostBFlowは実行可能解を得た後に使う。費用付きフローでは、表示から最適性を判定しない。
- フローやグラフは変更しない。`dump_array(obj)`は`obj.tolist()`を呼ぶため、そのmethodの計算量・内部状態の扱いに従う。
- 実数・整数の辺情報は文字列で転送し、大きな整数をJavaScriptの数値へ丸めない。非有限の値は受け付けない。
- 提出時にはデバッグ用importと呼び出しを外す。通常操作に負担はないが、dump自体には列挙・文字列化・file書き込みの時間がかかる。
