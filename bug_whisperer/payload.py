from __future__ import annotations

import logging
import os

from bug_whisperer.models import IssueReport


LOGGER = logging.getLogger("bug_whisperer.payload")
DEFAULT_MIN_BODY_LENGTH = 30


def extract_issue_report(payload: dict) -> IssueReport:
    return IssueReport.from_webhook(payload)


def minimum_body_length() -> int:
    raw_value = os.getenv("MIN_ISSUE_BODY_LENGTH", str(DEFAULT_MIN_BODY_LENGTH))
    try:
        return max(1, int(raw_value))
    except ValueError:
        LOGGER.warning(
            "Invalid MIN_ISSUE_BODY_LENGTH=%r; using %s",
            raw_value,
            DEFAULT_MIN_BODY_LENGTH,
        )
        return DEFAULT_MIN_BODY_LENGTH


def validation_error(report: IssueReport) -> str | None:
    if report.action and report.action != "opened":
        return f"ignoring issue action {report.action!r}; only 'opened' is processed"

    if report.issue_number is None:
        return "missing issue.number"

    if not report.repository_full_name:
        return "missing repository.full_name"

    body = report.body.strip()
    if not body:
        return "issue description is empty"

    min_length = minimum_body_length()
    if len(body) < min_length:
        return f"issue description is too short ({len(body)} chars; minimum {min_length})"

    return None
