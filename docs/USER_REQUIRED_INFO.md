# 応募・提案自動化に必要なユーザー情報

このドキュメントは、AI求人候補に対して応募・提案パケットを作るために、ユーザーから事前に受け取る必要がある情報をまとめたものです。

## 重要な前提

このリポジトリのMVPは、LinkedInやクラウドワークスに対して、本人確認なしに自動応募・自動投稿・自動送信を行いません。

理由:

- 誤応募、誤発注、スパム扱い、アカウント制限のリスクがある
- 求人・発注には本人の意思確認が必要
- LinkedInやクラウドワークス等の各サービス規約に従う必要がある

このMVPで自動化する範囲は以下です。

1. 求人候補JSONを読み込む
2. ユーザー情報JSONを検証する
3. 不足情報を一覧化する
4. 応募・提案文を作る
5. 想定質問への回答を作る
6. 添付・確認チェックリストを作る
7. テスト送信ログを作る
8. 最後は人間が確認して、各サービス上で送信する

## 必須情報

`examples/user_profile.example.json` をコピーして、以下を埋めてください。

### 1. 基本情報

|項目|必須|説明|例|
|---|---:|---|---|
|`identity.display_name`|必須|応募・提案文に出す名前|山田太郎|
|`identity.legal_name`|任意|契約時に必要な正式名|山田太郎|
|`identity.location`|必須|居住地または稼働拠点|日本 / 東京都|
|`identity.timezone`|必須|タイムゾーン|Asia/Tokyo|

### 2. 連絡先

|項目|必須|説明|例|
|---|---:|---|---|
|`contact.email`|必須|連絡可能なメール|taro@example.com|
|`contact.phone`|任意|必要な場合のみ|+81-90-0000-0000|
|`contact.preferred_contact_method`|必須|希望連絡手段|CrowdWorks message / Email|

### 3. 稼働条件

|項目|必須|説明|例|
|---|---:|---|---|
|`availability.hours_per_week`|必須|週あたり稼働可能時間|10|
|`availability.start_date`|必須|開始可能日|2026-05-20|
|`availability.working_hours`|必須|主な稼働時間|平日20:00-23:00、土日午前|
|`availability.response_time`|任意|通常返信時間|24時間以内|

### 4. 希望条件

|項目|必須|説明|例|
|---|---:|---|---|
|`rates.hourly_jpy`|条件付き|時間単価希望|3000|
|`rates.fixed_min_jpy`|条件付き|固定報酬の最低希望|5000|
|`rates.notes`|任意|単価に関する補足|初回のみ相談可|

`hourly_jpy` または `fixed_min_jpy` のどちらかは必須です。

### 5. スキル

|項目|必須|説明|例|
|---|---:|---|---|
|`skills.ai_tools`|必須|使えるAIツール|ChatGPT, Claude, Gemini|
|`skills.technical`|必須|技術スキル|Python, Google Sheets, prompt evaluation|
|`skills.research`|必須|調査・整理スキル|Web research, summarization|
|`skills.writing`|必須|文章作成スキル|Japanese business writing|

### 6. 言語

|項目|必須|説明|例|
|---|---:|---|---|
|`languages`|必須|対応言語とレベル|Japanese native, English business reading|

### 7. 実績・職務経歴

|項目|必須|説明|例|
|---|---:|---|---|
|`experience.summary`|必須|100〜300字程度の自己紹介|AIツールを使ったリサーチ...|
|`experience.projects`|必須|関連実績の配列|AI記事要約、データ整理など|
|`portfolio.urls`|任意|公開できる実績URL|GitHub, Notion, blog等|

公開できるURLがない場合は、`portfolio.urls` を空配列にして、`experience.projects` に非公開実績の概要を書いてください。

### 8. 応募ポリシー

|項目|必須|説明|例|
|---|---:|---|---|
|`application_preferences.target_roles`|必須|狙いたい仕事|AI評価、プロンプト評価、リサーチ|
|`application_preferences.avoid_roles`|必須|避けたい仕事|電話営業、顔出し必須など|
|`application_preferences.tone`|必須|応募文のトーン|丁寧、簡潔、実務寄り|
|`application_preferences.ng_conditions`|必須|応募しない条件|報酬未記載、個人情報提出が多い等|

### 9. コンプライアンス確認

|項目|必須|説明|値|
|---|---:|---|---|
|`compliance.human_review_before_submit`|必須|送信前に人間が確認する|true|
|`compliance.no_false_claims`|必須|虚偽の経歴を書かない|true|
|`compliance.no_terms_violating_automation`|必須|規約違反の自動化をしない|true|
|`compliance.no_personal_data_scraping`|必須|個人情報収集をしない|true|

## 任意だが精度向上に役立つ情報

- 履歴書・職務経歴書のファイルパス
- 過去の提案文サンプル
- 希望する最低報酬
- 得意業界
- 苦手な作業
- 週ごとの稼働変動
- 使用できるツールアカウント
- 請求書・契約関連の希望

## 出力されるもの

`ai-application-packet` 実行後、以下が作られます。

```text
application_draft.md
mock_submission_payload.json
submission_checklist.md
dry_run_submission_log.json
```

不足がある場合:

```text
missing_user_info.md
```

## 最終送信の扱い

このMVPでは、`dry_run_submission_log.json` に「送信直前まで作成できたか」を記録します。

本番で送信まで自動化したい場合は、以下のどちらかが必要です。

1. 対象サービスが許可する公式API
2. 明示的に許可された社内・自社フォーム

LinkedInやクラウドワークスの画面をbotで自動操作して応募・投稿する実装は、このリポジトリでは標準対応しません。
