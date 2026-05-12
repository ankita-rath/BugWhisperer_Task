from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Task 1 - GitHub Issues webhook fields chosen for triage:
# - action: confirms the webhook activity; the service processes only "opened" issues.
# - issue.number: required to post the AI triage comment back to the original issue.
# - issue.title: gives the shortest symptom statement and anchors the AI summary.
# - issue.body: carries reproduction details, expected behavior, logs, and context.
# - issue.user.login: identifies who reported the bug for follow-up questions.
# - issue.labels[].name: preserves reporter/team hints such as "bug", "ui", or "urgent".
# - repository.full_name: identifies the owner/repo needed by the GitHub comments API.
# - repository.html_url: useful context in logs and troubleshooting.
# - sender.login: identifies the webhook actor, which can differ from the issue author.


@dataclass(frozen=True)
class IssueReport:
    action: str
    issue_number: int | None
    title: str
    body: str
    author: str
    labels: list[str]
    repository_full_name: str
    repository_url: str
    sender: str

    @classmethod
    def from_webhook(cls, payload: dict[str, Any]) -> "IssueReport":
        issue = payload.get("issue") or {}
        repository = payload.get("repository") or {}
        issue_user = issue.get("user") or {}
        sender = payload.get("sender") or {}
        labels = issue.get("labels") or []

        return cls(
            action=str(payload.get("action") or ""),
            issue_number=issue.get("number"),
            title=str(issue.get("title") or ""),
            body=str(issue.get("body") or ""),
            author=str(issue_user.get("login") or "unknown"),
            labels=[
                str(label.get("name"))
                for label in labels
                if isinstance(label, dict) and label.get("name")
            ],
            repository_full_name=str(repository.get("full_name") or ""),
            repository_url=str(repository.get("html_url") or ""),
            sender=str(sender.get("login") or "unknown"),
        )
