from pathlib import Path

from ai_job_hunter.search import FixtureSearchProvider


def test_fixture_provider_loads_results() -> None:
    fixture = Path("fixtures/sample_linkedin_results.json")
    provider = FixtureSearchProvider(fixture)

    results = provider.search("test", max_results=2)

    assert len(results) == 2
    assert results[0].title
    assert "linkedin.com/jobs" in results[0].url
