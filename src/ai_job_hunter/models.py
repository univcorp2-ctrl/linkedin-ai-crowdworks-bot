from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SearchResult:
    """A search result returned by a search provider.

    The bot intentionally stores only title, URL, and snippet. It does not fetch or scrape the
    LinkedIn page itself.
    """

    title: str
    url: str
    snippet: str = ""
    source: str = "search"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class JobCandidate:
    """A scored job candidate."""

    result: SearchResult
    score: int
    reasons: tuple[str, ...]
