from __future__ import annotations

from dataclasses import dataclass

from ai_job_hunter.models import SearchResult


@dataclass(frozen=True)
class RequirementSummary:
    """Extracted requirements from search result metadata.

    Because this project intentionally avoids scraping LinkedIn job pages, the extraction is based
    only on title, URL, and search snippet. Items are therefore best treated as first-pass signals.
    """

    technical: tuple[str, ...]
    personal: tuple[str, ...]
    outsourcing_tasks: tuple[str, ...]
    cautions: tuple[str, ...]


TECHNICAL_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("chatgpt", "gpt", "llm", "生成ai", "prompt", "プロンプト"), "ChatGPT・LLM・プロンプトの基本理解"),
    (("data annotation", "annotation", "labeling", "label", "ラベリング", "データアノテーション"), "AI学習データの確認・分類・ラベリング"),
    (("evaluate", "evaluation", "review", "レビュー", "評価", "quality"), "AI出力の評価・品質チェック"),
    (("content", "writing", "copy", "記事", "ライティング"), "文章作成・要約・編集"),
    (("excel", "spreadsheet", "google sheets", "スプレッドシート", "csv"), "表計算・CSV整理"),
    (("python", "api", "automation", "自動化"), "Python/API/自動化の基礎"),
    (("sql", "database", "データベース"), "SQL・データベースの基礎"),
    (("nlp", "natural language", "自然言語"), "自然言語処理の基礎知識"),
    (("machine learning", "ml", "機械学習"), "機械学習の基礎知識"),
)

PERSONAL_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("remote", "リモート", "在宅"), "在宅で自律的に作業できること"),
    (("contract", "freelance", "業務委託", "副業"), "業務委託・副業として期限を守れること"),
    (("entry", "junior", "assistant", "associate", "未経験", "アシスタント"), "初心者向け手順を理解して丁寧に進められること"),
    (("review", "evaluate", "annotation", "label", "quality", "評価", "チェック"), "細かい違いに気づける注意力"),
    (("writing", "content", "copy", "communication", "文章", "ライティング"), "読みやすい日本語または英語で説明できること"),
    (("guideline", "policy", "ルール", "ガイドライン"), "ガイドラインに沿って判断できること"),
)

DEFAULT_TECHNICAL = (
    "ChatGPTなど生成AIツールの基本操作",
    "Web検索と情報整理",
    "要約文の作成",
)

DEFAULT_PERSONAL = (
    "納期を守れること",
    "不明点を早めに質問できること",
    "求人本文を丸写しせず要約できること",
)

DEFAULT_TASKS = (
    "求人の業務内容を3〜5行で要約する",
    "必要スキルを技術要件と人物要件に分けて整理する",
    "クラウドワークスで発注しやすい軽作業に分解する",
)

DEFAULT_CAUTIONS = (
    "LinkedIn本文の丸写しは禁止し、要約・再構成にする",
    "ログインが必要な情報や個人情報は収集しない",
    "検索結果スニペット由来の推定を含むため、発注前に人間が確認する",
)


def _text(result: SearchResult) -> str:
    return f"{result.title} {result.snippet}".lower()


def _match_rules(text: str, rules: tuple[tuple[tuple[str, ...], str], ...]) -> list[str]:
    matched: list[str] = []
    for keywords, label in rules:
        if any(keyword.lower() in text for keyword in keywords):
            if label not in matched:
                matched.append(label)
    return matched


def extract_requirements(result: SearchResult) -> RequirementSummary:
    text = _text(result)
    technical = _match_rules(text, TECHNICAL_RULES)
    personal = _match_rules(text, PERSONAL_RULES)

    outsourcing_tasks = list(DEFAULT_TASKS)
    if any(word in text for word in ("annotation", "labeling", "ラベリング", "データアノテーション")):
        outsourcing_tasks.insert(0, "AI学習データの分類・ラベル付けルールを整理する")
    if any(word in text for word in ("prompt", "プロンプト", "chatgpt", "gpt", "llm")):
        outsourcing_tasks.insert(0, "プロンプト例とAI出力の良し悪しを整理する")
    if any(word in text for word in ("review", "evaluate", "評価", "チェック")):
        outsourcing_tasks.insert(0, "AI出力を評価するチェック項目を作る")

    return RequirementSummary(
        technical=tuple(technical or DEFAULT_TECHNICAL),
        personal=tuple(personal or DEFAULT_PERSONAL),
        outsourcing_tasks=tuple(dict.fromkeys(outsourcing_tasks)),
        cautions=DEFAULT_CAUTIONS,
    )
