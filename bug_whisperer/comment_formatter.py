from __future__ import annotations

from bug_whisperer.models import TriageResult


def format_github_comment(triage: TriageResult) -> str:
    missing_info = "\n".join(f"- {item}" for item in triage.missing_info)
    if not missing_info:
        missing_info = "- None"

    return "\n".join(
        [
            "## Bug Whisperer Triage",
            "",
            f"**Summary:** {triage.summary}",
            "",
            f"**Category:** {triage.category}",
            "",
            f"**Severity:** {triage.severity}",
            "",
            f"**First step:** {triage.first_step}",
            "",
            "**Missing info:**",
            missing_info,
        ]
    )

