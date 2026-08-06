# 実装を追加・変更するときの手引き

この文書は、今後moduleが増えても今回までに整えた品質を崩さないための作業手順です。判断に迷ったときは「提出コードへそのまま貼れて、API表だけを読んだ人が正しく使えるか」を基準にします。

## 1. 追加前に置き場所を決める

まず既存moduleを検索し、同じ目的・同じ内部表現の機能がないか確認します。

- 単独で選べる別のアルゴリズムやデータ構造は、目的が分かる名前の別fileに置く。
- 同じデータ表現を共有する基本操作、forward/inverse、min/maxのような同じfamilyは同じfileでよい。
- `Advanced*`、`Extras`、`Collections`のように中身を予測できない寄せ集めを作らない。
- 通常版、lazy版、dual版など、constructor・制約・計算量が異なるものは分ける。
- 版番号付きfileや、古い名前を残すだけのalias moduleで衝突を避けない。
- sourceの置き場所は「実装技法」ではなく、利用者が探す目的で決める。たとえば通常畳み込み、GCD/LCM畳み込み、bitwise畳み込み、FPSを同じ分類へ集めない。
- 1カテゴリが20 modulesを超える前に、用途の違いが分かるカテゴリへ分ける。カテゴリ定義は`tools/category_config.py`を正本とし、source・APIリファレンス・サイトの分類を同時に更新する。

詳しい境界の例は[モジュール境界の方針](MODULE_BOUNDARIES.md)を参照します。

## 2. 公開APIを決める

競技中に頻繁に書く名前は、短く標準的なものを優先します。長い説明的な名前しかない状態や、同じ処理の別名が複数ある状態を避けます。

- Pythonや競技プログラミングで一般的な`get`、`set`、`add`、`prod`、`sum`などを優先する。
- 元の`library`に広く使っていた自然な名前があれば、意味と引数順を確認したうえで優先する。たとえば組合せ表は`Comb`、二項係数は`C`とする。
- `lis`、`scc`、`msb_index`、`lsb_index`のように競技プログラミングで定着した略称は使ってよい。独自の頭字語は作らない。
- module名ですでに明らかな語を関数名で繰り返さない。入力形式など、呼び分けに必要な情報は残す。
- 既存APIと意味や引数順を揃える。違う場合は理由を明記する。
- `op`を受け取るAPIは、`op(current, value)`か`op(value, current)`かを明記する。
- 添字は原則0-indexed、区間は原則半開区間`[l, r)`とする。
- 互換性目的でaliasが本当に必要な場合は、期限と削除条件をissueまたは文書へ残す。

## 3. 実装する

- `library_codex`を正本として実装する。元の`library`は着想や便利な挙動を探す資料として使う。
- PyPyでの実行速度を意識し、hot loopの一時objectやmethod lookupを増やしすぎない。
- 原則として再帰を使わない。深い木・グラフでも入力サイズでstack overflowしない形にする。
- デバッグや説明だけのために、通常操作へ無視できない常駐メモリや更新時間を追加しない。
- 外部packageへ依存せず、標準libraryと`library_codex`内の明示的なimportで完結させる。

速さを理由に意味が変わる最適化は入れません。複数の実装方式が必要なら、適用条件をconstructorまたは別classとして明示します。

## 4. API説明を書く

module冒頭では、実装方式の名前より先に「何ができるか」を説明します。各公開APIには次を揃えます。

1. 何をするか。method名を言い換えただけにしない。
2. 各引数の意味、添字・区間、許される値、演算順。
3. 返り値の型と形式。
4. methodごとの時間計算量。必要なら追加メモリも書く。

返り値は型名だけで終わらせません。

- `list[int]`: 何の順で並ぶ整数かを書く。
- `dict[int, int]`: keyとvalueがそれぞれ何を表すかを書く。
- `tuple[list[int], list[int]]`: tupleの第1・第2要素と各listの並びを書く。
- iterator: 1回のiterationで得られる値と順序を書く。
- `None`: 状態をどう変更するかを書く。

計算量は`O(log N)`、`O(N + M)`、期待`O(N)`のように、おおよその増え方が分かる形で示します。「Dinic」「64-bit確率的分解」のような実装名だけを計算量欄へ置きません。

sourceだけで表せない説明は`library_codex/tools/api_metadata.py`へ追加し、次でAPIリファレンスを再生成します。

- classが保持する状態と作成後にできることは`CLASS_DETAILS_BY_SYMBOL`へ書く。
- 同名の`get`・`query`などを区別する説明は`API_DETAILS_BY_SYMBOL`へ、module path・class名・method名をkeyとして書く。
- tupleの各要素は`returnParts`で名前・型・意味を分ける。listはindex、dictはkey/value、iteratorはyieldする要素が分かる説明にする。

```sh
pypy3 library_codex/tools/build_api_reference.py
```

## 5. データ構造には論理内容の見え方を用意する

内容を有限時間・有限サイズで列挙できる構造には、直接取得する`tolist()`または`items()`と表示を用意します。

- `str(obj)`: 利用者から見える論理内容。
- `repr(obj)`: `TypeName(...)`の形で型名と論理内容。
- 密な列: index順のlist。
- 行列: 行・列順の2次元list。
- set: 昇順list。
- multiset: 重複を残した昇順list。
- map: key順の`items()`。
- Union-Find: 頂点順が安定した成分list。
- 巨大な疎構造: 全座標を展開せず、使用中のindexと値だけ。

Lazy構造では保留中の作用を反映した現在値を返します。表示を呼んだ後もquery結果や更新履歴が壊れないことをtestします。全形式と計算量は[デバッグ出力](DEBUG_OUTPUT.md)へ追記します。

## 6. testを書く

最低限、次を組み合わせます。

- 小さい入力を単純解と比較するrandomized test。
- 空、要素1、重複、負数、上限付近、空区間など適用可能な境界値。
- 更新とqueryを混ぜた状態遷移。
- `op`を使う構造では文字列連結や行列などの非可換演算。
- 深い木・グラフで再帰に依存しないこと。
- `tolist()`、`items()`、`str`、`repr`の厳密な出力と、呼出し後の状態。
- bundleを単独processで実行し、package未installでも使えること。

反復中は差分検査を使います。Gitの未commit差分から、変更module、それをimportするmodule、対応test、API同期、変更fileだけの再帰監査を自動選択します。

```sh
pypy3 library_codex/tools/check_changed.py
```

直前のcommitを調べる場合は`--base HEAD~1`、実行せず選択内容だけを見る場合は`--list`を付けます。性能を触ったときだけ`--benchmarks`を追加します。

```sh
pypy3 library_codex/tools/check_changed.py --base HEAD~1 --list
pypy3 library_codex/tools/check_changed.py --benchmarks
```

機能がまとまったcheckpointではquick検査を行います。

```sh
pypy3 library_codex/tools/check_library.py
```

全検査は、共通基盤を横断する変更、大規模な性能変更、mainへmergeするrelease checkpointで行います。説明文、サイト表示、1moduleの局所変更のたびには実行しません。

```sh
pypy3 library_codex/tools/check_library.py --profile full
```

## 7. bundleと公開物を確認する

bundleは選択moduleのsourceから、実際にimportする`library_codex`内依存だけを再帰的に展開します。生成物はpackage wrapperや動的な`bundle`関数ではなく、貼り付けて実行できる通常のPythonコードにします。

公開するときは次を同期します。細かい試行ごとに公開せず、確認しやすい変更のまとまりをcheckpointとして一度だけ公開して構いません。サイトのAPI dataは、既存JSONの`sourceRevision`から変更moduleとbundle依存先だけを差分更新します。

- sourceと生成済みAPIリファレンス。
- test数・再帰監査数などREADMEに載せる実績値。
- GitHub branchとpull request。
- サイトが読むAPI JSON。
- サイトから取得できる配布ZIP。

## 8. 共通catalogを同期する

`library_codex/library-catalog.json`は、Yura DeskとWebサイトが共通で読むライブラリ索引です。利用側でsourceを再解析したり、独自の検索語辞書を複製したりしません。

catalogのfunction・class・method、signature、説明、引数、返り値、計算量、依存、source、standalone codeは、source ASTと生成済みAPIリファレンスから自動取得します。categoryは`tools/category_config.py`を正本とします。正式名や説明から推測できない通称だけを、`tools/api_metadata.py`の`SEARCH_TERMS_BY_MODULE`または`SEARCH_TERMS_BY_SYMBOL`へ追加してください。

```sh
pypy3 library_codex/tools/build_api_reference.py
pypy3 library_codex/tools/build_library_catalog.py
pypy3 library_codex/tools/build_library_catalog.py --check
pypy3 library_codex/tools/build_library_catalog.py --audit-descriptions
```

通常の生成は、既存catalogのmodule別fingerprintを使い、変更moduleとそのbundle依存先だけを再生成します。入力に変更がなければJSONを書き換えません。生成結果は一時fileへ完成させ、JSONとschemaを検証してから置き換えるため、途中で失敗しても直前の正常なcatalogは維持されます。

`--audit-descriptions`はcatalogを書き換えず、「上記の処理結果」「指定した範囲の集計結果」など、利用方法を判断できない説明を一覧にします。新しいAPIを追加したときや説明をまとめて改善するときは、この一覧を減らしてください。metadataはmodule別fingerprintへ分離されているため、特定moduleの説明だけを変えた場合は全moduleを再解析しません。

`check_changed.py`と`check_library.py`はcatalog同期検査を含みます。source、API説明、category、検索語辞書を変更したら、catalogを再生成してから完了してください。

## 完了チェックリスト

- [ ] module名だけで主目的が分かる。
- [ ] よく使うAPI名が短く、冗長なaliasがない。
- [ ] moduleの目的、引数、返り値の形式、methodごとの計算量が読める。
- [ ] 非可換演算、境界値、randomized testを必要に応じて追加した。
- [ ] データ構造の論理内容を確認するAPIと表示を検討した。
- [ ] bundleが単独で動き、無関係な依存を含まない。
- [ ] APIリファレンスを再生成した。
- [ ] `library-catalog.json`を再生成し、検索語metadataの参照先が存在する。
- [ ] 反復中は差分検査を通し、checkpointではquick、release条件に該当するときだけfull検査を通した。
- [ ] GitHubとサイトの公開物を同期した。
