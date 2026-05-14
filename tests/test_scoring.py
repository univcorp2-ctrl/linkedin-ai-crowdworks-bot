from ai_job_hunter.models import SearchResult
from ai_job_hunter.scoring import rank_candidates, score_result


def test_easy_ai_linkedin_job_scores_above_senior_engineering_role() -> None:
    easy = SearchResult(
        title="AI Data Annotation Specialist - Remote | LinkedIn",
        url="https://www.linkedin.com/jobs/view/123/",
        snippet="Entry-level remote contract role to review and label AI outputs.",
    )
    senior = SearchResult(
        title="Senior Machine Learning Engineer | LinkedIn",
        url="https://www.linkedin.com/jobs/view/456/",
        snippet="Lead AI platform architecture as a senior engineer.",
    )

    ranked = rank_candidates([senior, easy])

    assert ranked[0].result is easy
    assert ranked[0].score > ranked[1].score


def test_non_linkedin_result_is_penalized() -> None:
    result = SearchResult(
        title="AI Assistant",
        url="https://example.com/jobs/ai-assistant",
        snippet="Remote prompt review assistant.",
    )

    candidate = score_result(result)

    assert "LinkedIn Jobsではない可能性" in candidate.reasons
