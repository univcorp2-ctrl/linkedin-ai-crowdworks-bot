# LinkedIn AI → CrowdWorks Draft Bot

LinkedIn Jobs で見つかる **AI関連・比較的かんたんな仕事** を検索結果から1件選び、クラウドワークスで発注するためのドラフトと、技術要件・人物要件のレポートを Markdown で生成するMVPです。

## 方針

このBotは、安全性と規約順守を優先して、以下は行いません。

- LinkedInのログイン済みページを自動操作しない
- LinkedInページ本文をクローリング・スクレイピングしない
- プロフィールや個人情報を収集しない
- クラウドワークスへ自動投稿しない

代わりに、Bing Web Search APIなどの検索API、または手元に保存した検索結果JSONから、LinkedIn Jobsの公開URL・タイトル・検索スニペットだけを使って候補を選びます。クラウドワークス発注文は `output/crowdworks_draft.md`、要件レポートは `output/daily_report.md` に出力し、最後は人間が確認して投稿します。

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
  --max-results 10 \
  --top-n 5
```

出力:

```text
Selected: AI Data Annotation Specialist - Remote | LinkedIn
Draft written to: output/crowdworks_draft.md
Report written to: output/daily_report.md
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

## 生成される日次レポート

`output/daily_report.md` に以下を出します。

- 今日の最有力候補
- 技術要件
- 人物要件
- 外注しやすい作業への切り出し案
- クラウドワークス発注時の注意点
- 上位候補一覧

## 毎日自動実行

`.github/workflows/daily-report.yml` が、毎日 09:00 JST に実行されます。

GitHubリポジトリの Settings → Secrets and variables → Actions に、以下の secret を追加してください。

```text
BING_SEARCH_API_KEY
```

実行後、以下のファイルが自動更新されます。

```text
reports/latest.md
reports/YYYY-MM-DD.md
reports/YYYY-MM-DD_crowdworks_draft.md
reports/YYYY-MM-DD_selected_candidate.json
```

APIキーが未設定の場合は、動作確認用に `fixtures/sample_linkedin_results.json` を使ってレポートを作ります。本番の毎日調査には `BING_SEARCH_API_KEY` が必要です。

## テスト

```bash
pytest
```

## 次の改善案

- Slack/メール通知
- 複数検索クエリを日次で回して候補をCSV化
- CrowdWorks投稿前チェックリストの追加
- OpenAI API等を使った発注文の自然文改善
