from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request

from bug_whisperer.models import IssueReport


LOGGER = logging.getLogger("bug_whisperer.github")
GITHUB_API_URL = "https://api.github.com"


class GitHubClientError(Exception):
    pass


def post_issue_comment(report: IssueReport, comment_body: str) -> str | None:
    if os.getenv("GITHUB_DRY_RUN", "").lower() in {"1", "true", "yes"}:
        LOGGER.info(
            "GITHUB_DRY_RUN enabled; would post comment to %s issue #%s",
            report.repository_full_name,
            report.issue_number,
        )
        return None

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise GitHubClientError("GITHUB_TOKEN is not set")

    if report.issue_number is None:
        raise GitHubClientError("Cannot post comment without issue number")

    if "/" not in report.repository_full_name:
        raise GitHubClientError(f"Invalid repository name: {report.repository_full_name!r}")

    owner, repo = report.repository_full_name.split("/", 1)
    path = f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/issues/{report.issue_number}/comments"
    url = f"{os.getenv('GITHUB_API_URL', GITHUB_API_URL).rstrip('/')}{path}"
    request = urllib.request.Request(
        url,
        data=json.dumps({"body": comment_body}).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "BugWhisperer",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        LOGGER.error("GitHub API failed with status %s: %s", exc.code, error_body)
        raise GitHubClientError(f"GitHub API failed with status {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        LOGGER.error("GitHub API call failed: %s", exc)
        raise GitHubClientError("GitHub API call failed") from exc

    return response_body.get("html_url")

