from datetime import date

from ai_job_hunter.models import JobCandidate, SearchResult
from ai_job_hunter.report import generate_daily_report


def test_daily_report_contains_requirement_sections_and_ranking() -> None:
    candidate = JobCandidate(
        result=SearchResult(
            title="AI Data Annotation Specialist - Remote | LinkedIn",
            url="https://www.linkedin.com/jobs/view/123/",
            snippet="Remote contract role helping review and label AI model outputs.",
        ),
        score=92,
        reasons=("LinkedIn JobsのURL", "AI関連キーワード: AI"),
    )

    report = generate_daily_report(
        [candidate],
        query="site:linkedin.com/jobs AI",
        today=date(2026, 5, 14),
        top_n=3,
    )

    assert "職務に必要そうな技術要件" in report
    assert "職務に必要そうな人物要件" in report
    assert "上位候補一覧" in report
    assert "2026-05-14" in report
    assert "https://www.linkedin.com/jobs/view/123/" in report
