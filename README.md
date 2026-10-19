# Saitoの個人開発アプリ（開発者のトップページ）

公開しているURL：`https://saito-apps.github.io/`（GitHubの組織`saito-apps`のリポジトリ`saito-apps.github.io`。2026-10-15公開）。各アプリのサポート・プライバシーポリシーは、アプリごとのリポジトリのGitHub Pages（例：`https://saito-apps.github.io/shikigoke/`）にある。

## 作り方

- ページ（`index.html`・`en/index.html`）は`apps.json`から`python3 build.py`で作る。HTMLを手で直さない
- `apps.json`の順に、アプリの画面の枠と説明を左右交互に並べる（番号01・02…も順に振る）
- 見た目は`style.css`。消炭色の地に生成りの文字、差し色は朱1色（2026-10-19にデザインを変更）

## アプリを足すとき

1. `images/`に画像を置く
   - アイコン：`<id>.png`（256×256、角丸なしの正方形。表示側で角を丸める）
   - アプリの画面：`<id>_screen_ja.jpg`・`<id>_screen_en.jpg`（横600px、縦は画面の比率のまま。ステータスバーは写っていてよい）。無ければ省略可（画面の枠にアイコンを大きく出す）
2. `apps.json`に1件足す（書き方は四季苔を見本に。日本語`ja`と英語`en`の両方を書く）
   - 必須：`id`・`icon`・`name`・`subtitle`・`category`（例：「ゲーム ・ 無料」）・`short`（ひとこと、30字前後。今のページでは使っていない）・`description`（説明、2文程度）
   - 省略可：`appStore`（未公開なら省くと「近日公開」になる）・`support`・`privacy`（このサイトからの相対パス、例`shikigoke/`）・`screenshot`・`tags`（4つ前後）・`released`（公開日`YYYY-MM-DD`。この日から30日間「NEW」の印が出る。日数は`build.py`の`NEW_DAYS`）
3. `python3 build.py`を実行し、`index.html`をブラウザで開いて確かめる

## 決めたこと

- 日本だけで配信しているアプリは、英語ページのApp Storeのリンクも日本のストア（`/jp/`）にする（海外のストアでは「この国では入手できません」と出るため）
- 英語のサポート・プライバシーのページが無いアプリは、英語ページからも日本語のページにつなぐ（英語版を出すときに作る）
