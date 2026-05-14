from __future__ import annotations

import re

from ai_job_hunter.models import JobCandidate, SearchResult

AI_KEYWORDS = (
    "ai",
    "artificial intelligence",
    "chatgpt",
    "gpt",
    "llm",
    "生成ai",
    "人工知能",
    "prompt",
    "プロンプト",
    "data annotation",
    "annotation",
    "データアノテーション",
    "labeling",
    "ラベリング",
)

EASY_KEYWORDS = (
    "assistant",
    "associate",
    "entry",
    "junior",
    "remote",
    "part-time",
    "contract",
    "freelance",
    "no-code",
    "content",
    "review",
    "evaluate",
    "simple",
    "簡単",
    "未経験",
    "在宅",
    "リモート",
    "業務委託",
    "副業",
    "チェック",
    "評価",
)

HARD_KEYWORDS = (
    "senior",
    "lead",
    "principal",
    "architect",
    "manager",
    "director",
    "head of",
    "phd",
    "research scientist",
    "machine learning engineer",
    "ml engineer",
    "platform engineer",
    "security clearance",
    "シニア",
    "責任者",
    "マネージャー",
    "機械学習エンジニア",
)

LINKEDIN_JOB_PATTERNS = (
    "linkedin.com/jobs",
    "linkedin.com/jobs/view",
)


def _text(result: SearchResult) -> str:
    return f"{result.title} {result.snippet} {result.url}".lower()


def _contains_any(text: str, keywords: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    for keyword in keywords:
        pattern = re.escape(keyword.lower())
        if re.search(pattern, text):
            hits.append(keyword)
    return hits


def score_result(result: SearchResult) -> JobCandidate:
    text = _text(result)
    score = 0
    reasons: list[str] = []

    if any(pattern in text for pattern in LINKEDIN_JOB_PATTERNS):
        score += 30
        reasons.append("LinkedIn JobsのURL")
    elif "linkedin.com" in text:
        score += 10
        reasons.append("LinkedIn関連URL")
    else:
        score -= 30
        reasons.append("LinkedIn Jobsではない可能性")

    ai_hits = _contains_any(text, AI_KEYWORDS)
    if ai_hits:
        score += min(40, 12 * len(ai_hits))
        reasons.append("AI関連キーワード: " + ", ".join(ai_hits[:5]))

    easy_hits = _contains_any(text, EASY_KEYWORDS)
    if easy_hits:
        score += min(30, 8 * len(easy_hits))
        reasons.append("簡単・外注しやすいキーワード: " + ", ".join(easy_hits[:5]))

    hard_hits = _contains_any(text, HARD_KEYWORDS)
    if hard_hits:
        score -= min(35, 10 * len(hard_hits))
        reasons.append("難度高めキーワードを検出: " + ", ".join(hard_hits[:5]))

    if not result.title.strip():
        score -= 20
        reasons.append("タイトルなし")
    if not result.url.strip():
        score -= 30
        reasons.append("URLなし")

    return JobCandidate(result=result, score=score, reasons=tuple(reasons))


def rank_candidates(results: list[SearchResult]) -> list[JobCandidate]:
    candidates = [score_result(result) for result in results]
    return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)
