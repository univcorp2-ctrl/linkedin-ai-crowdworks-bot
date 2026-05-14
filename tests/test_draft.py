from datetime import date

from ai_job_hunter.draft import generate_crowdworks_draft
from ai_job_hunter.models import JobCandidate, SearchResult


def test_draft_contains_candidate_url_and_crowdworks_sections() -> None:
    candidate = JobCandidate(
        result=SearchResult(
            title="Prompt Evaluation Assistant - Freelance | LinkedIn",
            url="https://www.linkedin.com/jobs/view/345/",
            snippet="Freelance assistant role to evaluate prompt responses.",
        ),
        score=88,
        reasons=("AI関連キーワード: prompt", "簡単・外注しやすいキーワード: freelance"),
    )

    draft = generate_crowdworks_draft(candidate, today=date(2026, 5, 14))

    assert "https://www.linkedin.com/jobs/view/345/" in draft
    assert "クラウドワークス募集タイトル案" in draft
    assert "求人本文のコピペ納品は禁止" in draft
    assert "2026-05-14" in draft
