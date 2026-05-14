from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from ai_job_hunter.draft import generate_crowdworks_draft
from ai_job_hunter.report import generate_daily_report
from ai_job_hunter.scoring import rank_candidates
from ai_job_hunter.search import provider_from_env

DEFAULT_QUERY = (
    "site:linkedin.com/jobs "
    "AI OR ChatGPT OR LLM remote contract Japan assistant annotation prompt"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find one easy AI-related LinkedIn Jobs search result and draft a CrowdWorks post."
    )
    parser.add_argument("--query", default=DEFAULT_QUERY, help="Search query")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum search results to inspect")
    parser.add_argument("--top-n", type=int, default=5, help="Number of ranked candidates in report")
    parser.add_argument(
        "--fixture",
        default=None,
        help="Use a local JSON fixture instead of a live search API",
    )
    parser.add_argument(
        "--output",
        default="output/crowdworks_draft.md",
        help="Markdown output path for CrowdWorks draft",
    )
    parser.add_argument(
        "--report-output",
        default="output/daily_report.md",
        help="Markdown output path for daily requirements report",
    )
    parser.add_argument(
        "--json-output",
        default="output/selected_candidate.json",
        help="JSON output path for the selected candidate",
    )
    parser.add_argument(
        "--timezone",
        default="Asia/Tokyo",
        help="Timezone used for report date",
    )
    return parser


def _write_text(path: str | Path, content: str) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    today = datetime.now(ZoneInfo(args.timezone)).date()
    provider = provider_from_env(fixture_path=args.fixture)
    results = provider.search(query=args.query, max_results=args.max_results)
    ranked = rank_candidates(results)

    if not ranked:
        raise SystemExit("No search results found.")

    selected = ranked[0]
    draft = generate_crowdworks_draft(selected, today=today)
    report = generate_daily_report(ranked, query=args.query, today=today, top_n=args.top_n)

    output_path = _write_text(args.output, draft)
    report_path = _write_text(args.report_output, report)

    json_path = Path(args.json_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(
            {
                "selected": {
                    "title": selected.result.title,
                    "url": selected.result.url,
                    "snippet": selected.result.snippet,
                    "source": selected.result.source,
                    "score": selected.score,
                    "reasons": list(selected.reasons),
                },
                "ranked_count": len(ranked),
                "report_path": str(report_path),
                "draft_path": str(output_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Selected: {selected.result.title}")
    print(f"Score: {selected.score}")
    print(f"Draft written to: {output_path}")
    print(f"Report written to: {report_path}")
    print(f"JSON written to: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
