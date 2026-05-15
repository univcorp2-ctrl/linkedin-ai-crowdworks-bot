# LinkedIn AI → CrowdWorks Draft Bot

LinkedIn Jobs で見つかる **AI関連・比較的かんたんな仕事** を検索結果から1件選び、クラウドワークスで発注するためのドラフトを Markdown で生成するMVPです。

加えて、テスト用途で **応募・提案直前までの作業を自動化する応募パケット生成機能** を追加しています。

## 方針

このBotは、安全性と規約順守を優先して、以下は行いません。

- LinkedInのログイン済みページを自動操作しない
- LinkedInページ本文をクローリング・スクレイピングしない
- プロフィールや個人情報を収集しない
- LinkedInやクラウドワークスで、本人確認なしに応募・投稿・送信しない

代わりに、Bing Web Search APIなどの検索API、または手元に保存した検索結果JSONから、LinkedIn Jobsの公開URL・タイトル・検索スニペットだけを使って候補を選びます。クラウドワークス発注文は `output/crowdworks_draft.md` に出力し、最後は人間が確認して投稿します。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
cp .env.example .env
```

Bing Web Search APIを使う場合は `.env` にキーを入れます。

```bash
BING_SEARCH_API_KEY=your_key_here
BING_SEARCH_ENDPOINT=https://api.bing.microsoft.com/v7.0/search
```

APIキーなしでも、同梱のサンプル検索結果で動作確認できます。

```bash
ai-job-hunter --fixture fixtures/sample_linkedin_results.json
```

## 求人候補検索の実行例

```bash
ai-job-hunter \
  --query 'site:linkedin.com/jobs AI OR ChatGPT OR LLM remote contract Japan assistant annotation prompt' \
  --max-results 10
```

出力:

```text
Selected: AI Data Annotation Specialist - Remote | LinkedIn
Draft written to: output/crowdworks_draft.md
JSON written to: output/selected_candidate.json
```

## 応募・提案パケット生成

`output/selected_candidate.json` とユーザー情報JSONから、応募・提案に使う文章、想定質問への回答、必要情報チェック、テスト送信ログを生成します。

まずサンプルのユーザー情報をコピーします。

```bash
cp examples/user_profile.example.json user_profile.json
```

`user_profile.json` を自分の情報に編集してから実行します。

```bash
ai-application-packet \
  --candidate-json output/selected_candidate.json \
  --profile user_profile.json \
  --output-dir output/application_packet
```

生成物:

```text
output/application_packet/application_draft.md
output/application_packet/mock_submission_payload.json
output/application_packet/submission_checklist.md
output/application_packet/dry_run_submission_log.json
```

不足情報がある場合は、以下を出力して終了します。

```text
output/application_packet/missing_user_info.md
```

## ユーザーから必要な情報

必要情報は `docs/USER_REQUIRED_INFO.md` にまとめています。

最低限必要なもの:

- 氏名または表示名
- 連絡先
- 稼働可能時間
- 希望単価または予算条件
- AI/ChatGPT関連スキル
- 職務経歴・実績
- ポートフォリオURL
- 対応言語
- 応募時のNG条件
- 最終送信前に人間が確認することへの同意

## 生成されるクラウドワークス発注文

`output/crowdworks_draft.md` に以下のような内容を出します。

- 参考にしたLinkedIn求人URL
- 簡単そうだと判断した理由
- クラウドワークスの募集タイトル案
- 業務内容
- 納品物
- 応募条件
- 予算・納期の初期案
- 注意事項

## テスト

```bash
pytest
```

## 次の改善案

- 複数検索クエリを日次で回して候補をCSV化
- Slack/メール通知
- CrowdWorks投稿前チェックリストの追加
- 許可された公式APIがあるサービスへの送信アダプタ追加
- OpenAI API等を使った応募文・発注文の自然文改善
