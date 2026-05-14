# LinkedIn AI → CrowdWorks Draft Bot

LinkedIn Jobs で見つかる **AI関連・比較的かんたんな仕事** を検索結果から1件選び、クラウドワークスで発注するためのドラフトを Markdown で生成するMVPです。

## 方針

このBotは、安全性と規約順守を優先して、以下は行いません。

- LinkedInのログイン済みページを自動操作しない
- LinkedInページ本文をクローリング・スクレイピングしない
- プロフィールや個人情報を収集しない
- クラウドワークスへ自動投稿しない

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

## 実行例

```bash
ai-job-hunter \
  --query 'site:linkedin.com/jobs AI OR ChatGPT OR LLM remote contract Japan assistant annotation prompt' \
  --max-results 10
```

出力:

```text
Selected: AI Data Annotation Specialist - Remote | LinkedIn
Draft written to: output/crowdworks_draft.md
```

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
- OpenAI API等を使った発注文の自然文改善
