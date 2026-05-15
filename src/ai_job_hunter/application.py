from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MissingField:
    path: str
    label: str
    reason: str


REQUIRED_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("identity.display_name", "表示名", "応募・提案文で名乗る名前が必要です。"),
    ("identity.location", "稼働拠点", "時差・地域条件の確認に必要です。"),
    ("identity.timezone", "タイムゾーン", "稼働時間の説明に必要です。"),
    ("contact.email", "メールアドレス", "連絡先として必要です。"),
    ("contact.preferred_contact_method", "希望連絡手段", "連絡方法の明記に必要です。"),
    ("availability.hours_per_week", "週あたり稼働時間", "稼働量の判断に必要です。"),
    ("availability.start_date", "開始可能日", "いつから着手できるかの説明に必要です。"),
    ("availability.working_hours", "主な稼働時間", "返信・作業時間帯の説明に必要です。"),
    ("skills.ai_tools", "AIツール経験", "AI関連案件への適性説明に必要です。"),
    ("skills.technical", "技術スキル", "要件との一致度を説明するために必要です。"),
    ("skills.research", "調査スキル", "求人・業務要件整理案件で必要です。"),
    ("skills.writing", "文章作成スキル", "提案文・要約作業への適性説明に必要です。"),
    ("languages", "対応言語", "日本語・英語などの対応可否に必要です。"),
    ("experience.summary", "職務経歴サマリー", "自己紹介に必要です。"),
    ("experience.projects", "関連実績", "信頼性を示すために必要です。"),
    ("application_preferences.target_roles", "狙う仕事", "応募対象の判断に必要です。"),
    ("application_preferences.avoid_roles", "避ける仕事", "誤応募防止に必要です。"),
    ("application_preferences.tone", "応募文のトーン", "文章生成方針に必要です。"),
    ("application_preferences.ng_conditions", "NG条件", "応募しない案件の判断に必要です。"),
    ("compliance.human_review_before_submit", "送信前確認", "最終送信前に人間が確認する同意が必要です。"),
    ("compliance.no_false_claims", "虚偽記載禁止", "実績・経歴の虚偽記載を防ぐために必要です。"),
    ("compliance.no_terms_violating_automation", "規約違反自動化禁止", "サービス規約違反を防ぐために必要です。"),
    ("compliance.no_personal_data_scraping", "個人情報収集禁止", "個人情報保護のために必要です。"),
)

COMPLIANCE_TRUE_FIELDS = (
    "compliance.human_review_before_submit",
    "compliance.no_false_claims",
    "compliance.no_terms_violating_automation",
    "compliance.no_personal_data_scraping",
)


def load_json(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    return json.loads(json_path.read_text(encoding="utf-8"))


def get_path(data: dict[str, Any], dotted_path: str) -> Any:
    current: Any = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, tuple, set, dict)) and len(value) == 0:
        return True
    return False


def validate_user_profile(profile: dict[str, Any]) -> list[MissingField]:
    missing: list[MissingField] = []
    for path, label, reason in REQUIRED_FIELDS:
        value = get_path(profile, path)
        if _is_empty(value):
            missing.append(MissingField(path=path, label=label, reason=reason))

    hourly = get_path(profile, "rates.hourly_jpy")
    fixed = get_path(profile, "rates.fixed_min_jpy")
    if _is_empty(hourly) and _is_empty(fixed):
        missing.append(
            MissingField(
                path="rates.hourly_jpy or rates.fixed_min_jpy",
                label="希望単価",
                reason="時間単価または固定報酬の最低希望のどちらかが必要です。",
            )
        )

    for path in COMPLIANCE_TRUE_FIELDS:
        if get_path(profile, path) is not True:
            missing.append(
                MissingField(
                    path=path,
                    label="コンプライアンス確認",
                    reason="この項目は true である必要があります。",
                )
            )

    return missing


def normalize_candidate(candidate_payload: dict[str, Any]) -> dict[str, Any]:
    selected = candidate_payload.get("selected", candidate_payload)
    return {
        "title": str(selected.get("title", "")).strip(),
        "url": str(selected.get("url", "")).strip(),
        "snippet": str(selected.get("snippet", "")).strip(),
        "score": selected.get("score"),
        "reasons": selected.get("reasons", []),
    }


def _join_values(values: Any) -> str:
    if isinstance(values, list):
        rendered: list[str] = []
        for value in values:
            if isinstance(value, dict):
                if "name" in value and "level" in value:
                    rendered.append(f"{value['name']}（{value['level']}）")
                elif "title" in value and "description" in value:
                    rendered.append(f"{value['title']}: {value['description']}")
                else:
                    rendered.append(json.dumps(value, ensure_ascii=False))
            else:
                rendered.append(str(value))
        return "、".join(rendered)
    if isinstance(values, dict):
        return json.dumps(values, ensure_ascii=False)
    return str(values)


def build_application_draft(candidate: dict[str, Any], profile: dict[str, Any]) -> str:
    display_name = get_path(profile, "identity.display_name")
    location = get_path(profile, "identity.location")
    timezone = get_path(profile, "identity.timezone")
    hours = get_path(profile, "availability.hours_per_week")
    start_date = get_path(profile, "availability.start_date")
    working_hours = get_path(profile, "availability.working_hours")
    ai_tools = _join_values(get_path(profile, "skills.ai_tools"))
    technical = _join_values(get_path(profile, "skills.technical"))
    research = _join_values(get_path(profile, "skills.research"))
    writing = _join_values(get_path(profile, "skills.writing"))
    languages = _join_values(get_path(profile, "languages"))
    summary = get_path(profile, "experience.summary")
    projects = _join_values(get_path(profile, "experience.projects"))
    portfolio_urls = get_path(profile, "portfolio.urls") or []
    hourly = get_path(profile, "rates.hourly_jpy")
    fixed_min = get_path(profile, "rates.fixed_min_jpy")
    rate_notes = get_path(profile, "rates.notes") or ""
    tone = get_path(profile, "application_preferences.tone")

    rate_line = []
    if hourly:
        rate_line.append(f"時間単価: {hourly:,}円" if isinstance(hourly, int) else f"時間単価: {hourly}円")
    if fixed_min:
        rate_line.append(
            f"固定報酬の最低希望: {fixed_min:,}円" if isinstance(fixed_min, int) else f"固定報酬の最低希望: {fixed_min}円"
        )
    if rate_notes:
        rate_line.append(str(rate_notes))

    portfolio_block = "\n".join(f"- {url}" for url in portfolio_urls) or "- 公開可能なURLはありません。必要に応じて概要で説明します。"

    return f"""# 応募・提案ドラフト

## 対象候補

- タイトル: {candidate['title'] or '未取得'}
- URL: {candidate['url'] or '未取得'}
- スニペット: {candidate['snippet'] or '未取得'}

## 提案文

はじめまして、{display_name}と申します。  
{candidate['title'] or 'AI関連業務'}の内容を拝見し、AIツールを使った調査・要約・評価・作業手順化の経験を活かせると考え、応募いたします。

{summary}

対応可能な内容は以下です。

- AIツール: {ai_tools}
- 技術スキル: {technical}
- 調査・整理: {research}
- 文章作成: {writing}
- 対応言語: {languages}

関連実績:

{projects}

稼働条件:

- 拠点: {location}
- タイムゾーン: {timezone}
- 週あたり稼働時間: {hours}時間
- 開始可能日: {start_date}
- 主な稼働時間: {working_hours}
- 希望条件: {' / '.join(rate_line)}

進め方としては、まず要件と評価基準を確認し、少量のテスト作業で認識合わせをしたうえで、本作業に入る形を希望します。  
虚偽の経歴記載や求人本文の丸写しは行わず、必要に応じて確認しながら丁寧に進めます。

どうぞよろしくお願いいたします。

## 想定質問への回答

### いつから対応できますか？

{start_date}から対応可能です。主な稼働時間は{working_hours}です。

### 週にどれくらい稼働できますか？

週{hours}時間程度を想定しています。納期や作業量に応じて事前に相談します。

### AI関連の経験はありますか？

{ai_tools}を使った調査・要約・評価・文章作成の経験があります。関連実績として、{projects}があります。

### 英語の求人・指示に対応できますか？

対応言語は {languages} です。英語指示の読解が必要な場合は、事前に難度を確認します。

### 希望報酬はいくらですか？

{' / '.join(rate_line)} を希望します。初回テストは作業範囲を確認したうえで相談可能です。

## ポートフォリオ

{portfolio_block}

## 文体メモ

希望トーン: {tone}
"""


def build_submission_checklist(candidate: dict[str, Any], profile: dict[str, Any]) -> str:
    ng_conditions = get_path(profile, "application_preferences.ng_conditions") or []
    avoid_roles = get_path(profile, "application_preferences.avoid_roles") or []
    return """# 送信前チェックリスト

## 候補確認

- [ ] 求人タイトルとURLが正しい
- [ ] 募集内容が自分のスキル・稼働条件に合っている
- [ ] 報酬、納期、契約条件を確認した
- [ ] ログインが必要な情報や個人情報を無断収集していない
- [ ] 応募文に虚偽の実績・経歴がない
- [ ] 求人本文を丸写ししていない

## NG条件チェック

避ける仕事:
{avoid_roles}

応募しない条件:
{ng_conditions}

## 最終確認

- [ ] 送信先サービスの規約に反していない
- [ ] 人間が最終確認した
- [ ] 必要に応じて添付ファイルを確認した
- [ ] 送信後の返信対応時間を確保できる
""".format(
        avoid_roles="\n".join(f"- [ ] {item}" for item in avoid_roles) or "- [ ] 特になし",
        ng_conditions="\n".join(f"- [ ] {item}" for item in ng_conditions) or "- [ ] 特になし",
    )


def build_mock_submission_payload(candidate: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": "dry_run_only",
        "service": "manual_or_authorized_api_only",
        "candidate": candidate,
        "applicant": {
            "display_name": get_path(profile, "identity.display_name"),
            "location": get_path(profile, "identity.location"),
            "timezone": get_path(profile, "identity.timezone"),
            "email": get_path(profile, "contact.email"),
            "preferred_contact_method": get_path(profile, "contact.preferred_contact_method"),
        },
        "availability": get_path(profile, "availability"),
        "rates": get_path(profile, "rates"),
        "compliance": get_path(profile, "compliance"),
        "ready_for_human_review": True,
        "live_submission_performed": False,
    }


def build_missing_info_markdown(missing: list[MissingField]) -> str:
    rows = ["|項目|JSONパス|理由|", "|---|---|---|"]
    for field in missing:
        rows.append(f"|{field.label}|`{field.path}`|{field.reason}|")
    return "# 不足しているユーザー情報\n\n" + "\n".join(rows) + "\n"


def write_application_packet(
    candidate_payload: dict[str, Any],
    profile: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, Path | bool | int]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    missing = validate_user_profile(profile)
    if missing:
        missing_path = output / "missing_user_info.md"
        missing_path.write_text(build_missing_info_markdown(missing), encoding="utf-8")
        return {
            "ok": False,
            "missing_count": len(missing),
            "missing_path": missing_path,
        }

    candidate = normalize_candidate(candidate_payload)
    draft = build_application_draft(candidate, profile)
    checklist = build_submission_checklist(candidate, profile)
    payload = build_mock_submission_payload(candidate, profile)
    log = {
        "status": "DRY_RUN_READY_FOR_HUMAN_REVIEW",
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "live_submission_performed": False,
        "message": "Application packet generated. No live application or post was submitted.",
    }

    draft_path = output / "application_draft.md"
    checklist_path = output / "submission_checklist.md"
    payload_path = output / "mock_submission_payload.json"
    log_path = output / "dry_run_submission_log.json"

    draft_path.write_text(draft, encoding="utf-8")
    checklist_path.write_text(checklist, encoding="utf-8")
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "missing_count": 0,
        "draft_path": draft_path,
        "checklist_path": checklist_path,
        "payload_path": payload_path,
        "log_path": log_path,
    }
