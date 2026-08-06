# ライブラリページの作成ルール

この文書は、ライブラリの追加やサイト改修で、これまでの会話から決まった読みやすさを維持するための基準です。`library_codex`のsource・API説明・catalogを正本とし、Webサイトだけに説明を足す運用には戻しません。

## 情報の置き場所

- sourceから分かるsignature、公開API、import、依存関係、source code、standalone codeは生成する。
- sourceだけでは分からない意味は`tools/api_metadata.py`へ置く。
- class作成後にできることは`CLASS_DETAILS_BY_SYMBOL.constructorCreates`へ書く。
- 同名methodを区別する説明、引数固有の意味、返り値の構造は`API_DETAILS_BY_SYMBOL`へ書く。
- Webサイトは`library-catalog.json`を表示する。moduleごとの例外説明や検索語をサイト側へ複製しない。

## ページを読んだ人が最初に分かること

各moduleの冒頭だけで、次を判断できるようにします。

1. 何を求めたり管理したりできるか。
2. どのような入力を渡すか。
3. 代表的な操作と計算量。
4. 似たmoduleと何が違うか。違いがないなら説明を増やさない。

実装技法の名前だけを目的の説明にしません。「64-bit確率的分解」のような内部方式は、必要なら補足へ回します。

## 書かない説明

次の文は、利用者が判断できる情報へ置き換えます。

- 「処理を実行する」「値を求める」のようにAPI名を言い換えただけの文。
- 「用途欄を参照」「APIの説明を参照」「包含関係は説明を参照」のように別の場所へ逃がす文。
- 「初期化した`ClassName` object」のように、作成後の操作が分からない文。
- 同じ意味の日本語と英語の併記。
- library全体の規約を各引数で繰り返すだけの「0始まり」「0-indexed」。添字は原則0-indexedなので、1-indexed入力、切替option、返り値との番号対応など、例外や判断材料になる場合だけ書く。
- 正式な関連性を確認していない`Related modules`。

境界は参照先へ逃がさず、その場で「含む」「含まない」または式で明記します。たとえば`lower`と`upper`だけでは足りない場合、`$\mathrm{lower}_i \le x_i < \mathrm{upper}_i$`と書きます。

## 引数

- 配列は、各要素が何を表すか、長さ、並び順を必要に応じて書く。
- 区間は閉区間・開区間・半開区間をその場で明記する。
- callbackは呼出し形式、引数順、返す値、単位元を説明する。
- `op`と`composition`は非可換の場合も分かるように、新旧の値を渡す順序を書く。
- `None`や省略値は、どの動作へ切り替わるかを書く。
- 単に「入力」「値」「対象」とするのは、具体化できないかsourceをもう一度確認してからにする。

引数固有の説明は`API_DETAILS_BY_SYMBOL.argumentDescriptions`へ、引数名をkeyとして書けます。存在しない引数名はcatalog検査で失敗させます。

## 返り値

- `list`: `result[i]`が何か、長さ、順序を説明する。
- `dict`: keyとvalueの意味を分ける。
- `tuple`: `returnParts`で各要素の名前・型・意味を分ける。
- iterator: 1回にyieldする値と順序を説明する。
- class instance: `constructorCreates`で保持する状態と利用できる主要操作を書く。
- `None`: 返さないことだけでなく、どの状態が変わるかを書く。

型を見れば分かる内容を繰り返すより、利用者が次に書くコードを決められる情報を優先します。

## Markdownと数式

catalogの説明文は`markdown+tex`です。API名・引数名・短いcodeはbacktick、数式はTeXを使います。

- 行内数式: `$x_0 \le x_1 \le \cdots \le x_{N-1}$`
- 独立した数式: `$$\sum_{i=0}^{N-1} a_i$$`
- code: `` `query(left, right)` ``

変数の包含関係、漸化式、返り値の対応、変換式は数式にすると読みやすい場合にTeXで書きます。短い型名、method名、通常の文章まで数式にしません。計算量は検索・コピーのしやすさを優先し、通常は`O(N log N)`のままで構いません。

Webサイトはraw HTMLを説明から実行せず、MarkdownとTeXだけを描画します。GitHubの生成APIリファレンスにも同じ原文を載せます。

Webサイトの数式はMathMLと`Fira Math`で表示します。本文やコードから急に古い組版調へ切り替わらないことを優先し、moduleごとに数式フォントを変えません。数式の見た目を変更するときは、英字だけでなく添字、分数、総和、括弧も同じ式で確認します。

## 見た目と言葉

- 本文は読みやすい日本語を使い、`Functions`、`Arguments`、`Returns`、`Complexity`、`Code`など短いUI labelは英語でよい。
- 「日本語 / English」のような冗長な二重labelは作らない。
- 本文文字を細く・小さくしすぎない。薄い灰色だけで重要な説明を置かない。
- 1行ごとの説明位置を揃え、signature・説明・計算量の対応を崩さない。
- moduleごとに別デザインを足さず、難しい内容も共通のsection構造で説明する。
- 強いgradient、装飾的な英語、意味のないbadgeを増やさず、コードを探す速度を優先する。
- Importとそのまま使えるstandalone codeへ近い導線を用意する。bundleは内部wrapperではなく普通のPythonコードとして見せる。
- ページ遷移で不要なscroll animationを入れない。

## 分類とページの大きさ

- 1ページへ目的の違うmoduleをまとめない。
- 通常畳み込み、FPS、GCD/LCM畳み込み、bitwise畳み込みのように入力・代数・用途が違うものは分ける。
- データ構造も操作体系が違えば小カテゴリへ分ける。
- 1カテゴリへmoduleが集中したら、利用目的が名前から分かる単位へ分割する。

## 追加・変更時の確認

1. sourceと`api_metadata.py`を更新する。
2. APIリファレンスと`library-catalog.json`を生成する。
3. `--audit-descriptions`で曖昧な定型文が増えていないか確認する。
4. 変更moduleのページで、目的、引数、返り値、計算量、数式、Codeがcatalogだけから表示されることをtestする。
5. 差分検査を通し、まとまったcheckpointでサイトのJSONと配布ZIPを同期する。

## ページ内容チェックリスト

- [ ] 冒頭に「なにができるか」が具体的にある。
- [ ] 引数の範囲と包含関係を、そのAPI内で判断できる。
- [ ] 自明な0-indexed注記を繰り返していない。
- [ ] `list`・`dict`・`tuple`・instanceの中身が分かる。
- [ ] methodごとのBig-Oがある。
- [ ] 式にしたほうが短く正確な条件はTeXになっている。
- [ ] サイトだけの説明上書きがない。
- [ ] Importとstandalone codeへ迷わず移動できる。
- [ ] 本文の日本語と短い英語UI labelが重複していない。
- [ ] 既存ページと同じ構造・文字サイズ・余白で読める。
