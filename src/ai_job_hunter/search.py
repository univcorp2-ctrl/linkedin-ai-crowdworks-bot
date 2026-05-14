from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Protocol

import requests

from ai_job_hunter.models import SearchResult


class SearchProvider(Protocol):
    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Return search results without scraping LinkedIn pages."""


class FixtureSearchProvider:
    """Load search results from a local JSON file for development and tests."""

    def __init__(self, fixture_path: str | Path):
        self.fixture_path = Path(fixture_path)

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        if not self.fixture_path.exists():
            raise FileNotFoundError(f"Fixture not found: {self.fixture_path}")

        payload = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        rows = payload.get("results", payload if isinstance(payload, list) else [])
        results: list[SearchResult] = []
        for row in rows[:max_results]:
            results.append(
                SearchResult(
                    title=str(row.get("title", "")).strip(),
                    url=str(row.get("url", row.get("link", ""))).strip(),
                    snippet=str(row.get("snippet", row.get("description", ""))).strip(),
                    source="fixture",
                    metadata={"query": query},
                )
            )
        return results


class BingSearchProvider:
    """Search via Bing Web Search API.

    This provider does not open or crawl LinkedIn pages; it only uses search result metadata.
    """

    def __init__(self, api_key: str, endpoint: str | None = None, market: str = "ja-JP"):
        if not api_key:
            raise ValueError("Bing API key is required")
        self.api_key = api_key
        self.endpoint = endpoint or "https://api.bing.microsoft.com/v7.0/search"
        self.market = market

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        response = requests.get(
            self.endpoint,
            headers={"Ocp-Apim-Subscription-Key": self.api_key},
            params={"q": query, "count": max_results, "mkt": self.market, "textFormat": "Raw"},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        web_pages = payload.get("webPages", {}).get("value", [])

        results: list[SearchResult] = []
        for item in web_pages[:max_results]:
            results.append(
                SearchResult(
                    title=str(item.get("name", "")).strip(),
                    url=str(item.get("url", "")).strip(),
                    snippet=str(item.get("snippet", "")).strip(),
                    source="bing",
                    metadata={"query": query, "id": item.get("id")},
                )
            )
        return results


def provider_from_env(fixture_path: str | None = None) -> SearchProvider:
    """Choose a provider.

    Priority:
    1. Explicit fixture path
    2. Bing Web Search API env var
    3. Clear error message
    """

    if fixture_path:
        return FixtureSearchProvider(fixture_path)

    api_key = os.getenv("BING_SEARCH_API_KEY", "").strip()
    endpoint = os.getenv("BING_SEARCH_ENDPOINT", "").strip() or None
    if api_key:
        return BingSearchProvider(api_key=api_key, endpoint=endpoint)

    raise RuntimeError(
        "No search provider configured. Set BING_SEARCH_API_KEY or run with "
        "--fixture fixtures/sample_linkedin_results.json"
    )
