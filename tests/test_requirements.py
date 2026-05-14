from ai_job_hunter.models import SearchResult
from ai_job_hunter.requirements import extract_requirements


def test_extracts_technical_and_personal_requirements() -> None:
    result = SearchResult(
        title="Prompt Evaluation Assistant - Freelance | LinkedIn",
        url="https://www.linkedin.com/jobs/view/345/",
        snippet="Remote assistant role to evaluate ChatGPT prompt responses using simple guidelines.",
    )

    summary = extract_requirements(result)

    assert "ChatGPT・LLM・プロンプトの基本理解" in summary.technical
    assert "AI出力の評価・品質チェック" in summary.technical
    assert "在宅で自律的に作業できること" in summary.personal
    assert "細かい違いに気づける注意力" in summary.personal


def test_defaults_are_used_when_no_keywords_match() -> None:
    result = SearchResult(
        title="Unknown Role",
        url="https://www.linkedin.com/jobs/view/999/",
        snippet="General job description.",
    )

    summary = extract_requirements(result)

    assert summary.technical
    assert summary.personal
