# FEのSlack RAG

## 目的とターゲット

1. 目的
基本情報技術者試験の合格を目指す学生に対し、効率的でわかりやすい学習環境を提供、および学習の習慣化をサポートする。

2. ターゲット
基本情報資格試験の取得を目指している学生(非情報系も含む)

## 機能要件

- 用語解説機能
- 過去問出題機能
- 問題解説機能(科目Bも含む)

## 非機能要件

- 基本的に24時間365日稼働
- コストはできるだけ抑える

## データソース要件

- IPAが公開している過去問PDFやテキストデータ
- IPAの公式シラバス、またはオープンなIT用語辞典などのデータ

## システム構成、技術スタック

- Python 3.9 以上（3.10+ 推奨）、slack-bolt（Socket Mode）、Chroma（ローカル永続）、OpenAI 互換 API（埋め込み＋チャット）
- コーパスは `data/corpus/*.md`。**オリジナル教材**（`glossary.md` 等）に加え、**IPA 公表 PDF から抽出した `ipa-*.md`**（過去問題・解答例・採点講評・シラバス）を含む。利用上の留意点は [IPA FAQ（試験制度・その他）](https://www.ipa.go.jp/shiken/faq.html#seido) を確認すること。PDF の再取得・テキスト再生成は `python3 scripts/ipa_build_corpus.py --fetch`（詳細は [docs/20260405-ipa-corpus.md](docs/20260405-ipa-corpus.md)）。

## セットアップ・起動

1. 仮想環境を有効化し、依存を入れる（`pip` が無い場合は `python3 -m pip` を使う）。

   ```bash
   cd /path/to/FEbot
   python3 -m venv .venv
   source .venv/bin/activate   # Windows は .venv\Scripts\activate
   python3 -m pip install --upgrade pip
   python3 -m pip install -e .
   ```

   リポジトリ外で `pip3 install` だけ実行すると「インストール対象が無い」エラーになる。必ず上記のように **プロジェクトルートで** `-e .` を付ける。

2. `.env.example` を `.env` にコピーし、値を設定する。

   - `SLACK_TOKEN` … Bot User OAuth Token（`xoxb-`）
   - `SLACK_APP_TOKEN` … App-Level Token（Socket Mode 用、`xapp-`）
   - `AI_API_KEY` … OpenAI 等の API キー（**未設定でも** Slack 接続確認・練習問題・`/fe-help` は利用可。用語・質問の RAG 応答のみオフ）
   - 任意で `AI_BASE_URL`

3. （任意）IPA 由来コーパスを公式サイトから取り直す場合は、ネットワークのある環境で次を実行する。生成物は `data/corpus/ipa-*.md`（`data/ipa_raw/` は `.gitignore` 対象）。

   ```bash
   python3 scripts/ipa_build_corpus.py --fetch
   ```

4. コーパスを埋め込み、Chroma を生成する。

   ```bash
   python3 scripts/ingest.py
   ```

5. ボットを起動する。

   ```bash
   python3 -m febot
   ```

### Slack アプリ側（概要）

- **Socket Mode** をオンにする。
- **Bot Token Scopes** の例: `app_mentions:read`, `chat:write`, `channels:history`, `im:history`（DM 利用時）
- **Event Subscriptions**: `app_mention`, `message.channels`（チャンネルスレッドでの解答用）, `message.im`
- **Slash Commands**: `/fe-help`
- チャンネルでは **@アプリ名** でメンションして質問。DM では本文のみ。`過去問` `出題` `練習問題` でオリジナル練習問題モード。
