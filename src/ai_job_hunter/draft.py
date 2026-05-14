from __future__ import annotations

from datetime import date
from textwrap import dedent

from ai_job_hunter.models import JobCandidate


def generate_crowdworks_draft(candidate: JobCandidate, today: date | None = None) -> str:
    """Generate a human-reviewable CrowdWorks posting draft.

    The draft avoids copying a LinkedIn job post verbatim. It summarizes the search result and
    turns the idea into a small outsourcing task.
    """

    today = today or date.today()
    result = candidate.result
    reasons = "\n".join(f"- {reason}" for reason in candidate.reasons) or "- 条件に一致"

    return dedent(
        f"""
        # クラウドワークス発注文ドラフト

        生成日: {today.isoformat()}

        ## 参考にしたLinkedIn求人候補

        - タイトル: {result.title or "未取得"}
        - URL: {result.url or "未取得"}
        - 検索スニペット: {result.snippet or "未取得"}
        - スコア: {candidate.score}

        ### 選定理由

        {reasons}

        ---

        ## クラウドワークス募集タイトル案

        AI関連求人を参考にした軽作業リサーチ・要件整理をお願いします

        ## 依頼概要

        LinkedIn Jobs上で見つかるAI関連の求人情報を参考に、クラウドワークスで外注しやすい小さな作業へ分解するためのリサーチをお願いします。  
        求人本文の丸写しではなく、公開されている範囲の情報をもとに、業務内容・必要スキル・作業手順を要約してください。

        ## 作業内容

        1. 上記URLまたは同種のAI関連求人を確認
        2. 仕事内容を3〜5行で要約
        3. 初心者・副業ワーカーに任せやすい作業だけを抽出
        4. クラウドワークスで発注する場合の作業手順を作成
        5. 注意点、必要スキル、納品形式を整理

        ## 納品物

        Googleドキュメント、Markdown、またはテキストファイルで以下を納品してください。

        - 求人URL
        - 業務内容の要約
        - 外注できそうな作業の切り出し案
        - 作業手順
        - 必要スキル
        - 想定作業時間
        - 発注時の注意点

        ## 応募条件

        - ChatGPTなど生成AIツールを使ったことがある方
        - Web検索と要約ができる方
        - 著作権や個人情報に配慮して、文章を丸写ししない方

        ## 予算案

        まずはテスト依頼として、1件あたり3,000〜8,000円程度を想定しています。  
        内容が良ければ、同様の求人リサーチを複数件お願いする可能性があります。

        ## 納期案

        契約から2〜3日以内。

        ## 注意事項

        - LinkedInやその他サイトの規約に反する自動スクレイピングはしないでください。
        - 個人情報、応募者情報、ログインが必要な情報は収集しないでください。
        - 求人本文のコピペ納品は禁止です。必ず要約・再構成してください。
        """
    ).strip() + "\n"
