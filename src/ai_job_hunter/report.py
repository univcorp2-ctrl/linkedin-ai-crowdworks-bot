from __future__ import annotations

from datetime import date
from textwrap import dedent

from ai_job_hunter.models import JobCandidate
from ai_job_hunter.requirements import extract_requirements


def _bullet(items: tuple[str, ...] | list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def generate_daily_report(
    candidates: list[JobCandidate],
    query: str,
    today: date | None = None,
    top_n: int = 5,
) -> str:
    """Generate a daily Markdown report focused on requirements and outsourcing fit."""

    today = today or date.today()
    if not candidates:
        return dedent(
            f"""
            # AI関連求人 日次レポート

            生成日: {today.isoformat()}
            検索クエリ: `{query}`

            ## 結果

            候補は見つかりませんでした。
            """
        ).strip() + "\n"

    selected = candidates[0]
    selected_req = extract_requirements(selected.result)
    reasons = _bullet(list(selected.reasons)) if selected.reasons else "- 条件に一致"

    sections: list[str] = [
        dedent(
            f"""
            # AI関連求人 日次レポート

            生成日: {today.isoformat()}
            検索クエリ: `{query}`

            ## 今日の最有力候補

            - タイトル: {selected.result.title or "未取得"}
            - URL: {selected.result.url or "未取得"}
            - スコア: {selected.score}
            - 検索スニペット: {selected.result.snippet or "未取得"}

            ### 選定理由

            {reasons}

            ## 職務に必要そうな技術要件

            {_bullet(selected_req.technical)}

            ## 職務に必要そうな人物要件

            {_bullet(selected_req.personal)}

            ## クラウドワークスで外注しやすい作業への切り出し案

            {_bullet(selected_req.outsourcing_tasks)}

            ## 発注前の注意点

            {_bullet(selected_req.cautions)}
            """
        ).strip()
    ]

    rows = ["|順位|スコア|タイトル|技術要件シグナル|人物要件シグナル|URL|", "|---:|---:|---|---|---|---|"]
    for index, candidate in enumerate(candidates[:top_n], start=1):
        req = extract_requirements(candidate.result)
        tech = "<br>".join(req.technical[:3])
        personal = "<br>".join(req.personal[:3])
        title = (candidate.result.title or "未取得").replace("|", "\\|")
        url = candidate.result.url or "未取得"
        rows.append(f"|{index}|{candidate.score}|{title}|{tech}|{personal}|{url}|")

    sections.append("## 上位候補一覧\n\n" + "\n".join(rows))
    sections.append(
        dedent(
            """
            ## 読み方

            このレポートはLinkedInページ本文を自動取得せず、検索結果のタイトル・URL・スニペットのみから初期判断しています。  
            技術要件・人物要件は発注前の仮説として扱い、クラウドワークス掲載前に必ず人間が確認してください。
            """
        ).strip()
    )

    return "\n\n".join(sections) + "\n"
