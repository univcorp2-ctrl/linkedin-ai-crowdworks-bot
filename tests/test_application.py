from pathlib import Path

from ai_job_hunter.application import (
    build_application_draft,
    load_json,
    normalize_candidate,
    validate_user_profile,
    write_application_packet,
)


VALID_PROFILE = {
    "identity": {
        "display_name": "山田太郎",
        "location": "日本 / 東京都",
        "timezone": "Asia/Tokyo",
    },
    "contact": {
        "email": "taro@example.com",
        "preferred_contact_method": "CrowdWorks message",
    },
    "availability": {
        "hours_per_week": 10,
        "start_date": "2026-05-20",
        "working_hours": "平日夜、土日午前",
    },
    "rates": {"hourly_jpy": 3000},
    "skills": {
        "ai_tools": ["ChatGPT"],
        "technical": ["prompt evaluation"],
        "research": ["web research"],
        "writing": ["Japanese business writing"],
    },
    "languages": [{"name": "Japanese", "level": "Native"}],
    "experience": {
        "summary": "AIリサーチと要約が得意です。",
        "projects": [{"title": "AI要約", "description": "記事要約を行いました。"}],
    },
    "application_preferences": {
        "target_roles": ["AI評価"],
        "avoid_roles": ["電話営業"],
        "tone": "丁寧",
        "ng_conditions": ["報酬未記載"],
    },
    "compliance": {
        "human_review_before_submit": True,
        "no_false_claims": True,
        "no_terms_violating_automation": True,
        "no_personal_data_scraping": True,
    },
}


CANDIDATE_PAYLOAD = {
    "selected": {
        "title": "AI Data Annotation Specialist - Remote | LinkedIn",
        "url": "https://www.linkedin.com/jobs/view/123/",
        "snippet": "Remote contract role helping review and label AI model outputs.",
        "score": 90,
        "reasons": ["LinkedIn JobsのURL"],
    }
}


def test_validate_user_profile_accepts_valid_profile() -> None:
    assert validate_user_profile(VALID_PROFILE) == []


def test_validate_user_profile_requires_compliance_true() -> None:
    profile = {**VALID_PROFILE, "compliance": {**VALID_PROFILE["compliance"]}}
    profile["compliance"]["human_review_before_submit"] = False

    missing = validate_user_profile(profile)

    assert any(item.path == "compliance.human_review_before_submit" for item in missing)


def test_build_application_draft_contains_candidate_and_profile() -> None:
    candidate = normalize_candidate(CANDIDATE_PAYLOAD)

    draft = build_application_draft(candidate, VALID_PROFILE)

    assert "AI Data Annotation Specialist" in draft
    assert "山田太郎" in draft
    assert "ChatGPT" in draft
    assert "週あたり稼働時間" in draft


def test_write_application_packet_outputs_files(tmp_path: Path) -> None:
    result = write_application_packet(CANDIDATE_PAYLOAD, VALID_PROFILE, tmp_path)

    assert result["ok"] is True
    assert (tmp_path / "application_draft.md").exists()
    assert (tmp_path / "mock_submission_payload.json").exists()
    assert (tmp_path / "submission_checklist.md").exists()
    assert (tmp_path / "dry_run_submission_log.json").exists()


def test_write_application_packet_reports_missing_fields(tmp_path: Path) -> None:
    bad_profile = {"identity": {"display_name": "山田太郎"}}

    result = write_application_packet(CANDIDATE_PAYLOAD, bad_profile, tmp_path)

    assert result["ok"] is False
    assert (tmp_path / "missing_user_info.md").exists()


def test_example_profile_is_valid() -> None:
    profile = load_json("examples/user_profile.example.json")

    assert validate_user_profile(profile) == []
