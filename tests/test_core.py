import json
import unittest

from bug_whisperer.ai_client import parse_ai_response
from bug_whisperer.comment_formatter import format_github_comment
from bug_whisperer.models import IssueReport, TriageResult
from bug_whisperer.payload import validation_error
from bug_whisperer.prompt import build_prompt


class BugWhispererTests(unittest.TestCase):
    def setUp(self):
        with open("data/sample_issue_webhook.json", encoding="utf-8") as payload_file:
            self.payload = json.load(payload_file)

    def test_extracts_issue_report(self):
        report = IssueReport.from_webhook(self.payload)

        self.assertEqual(report.action, "opened")
        self.assertEqual(report.issue_number, 42)
        self.assertEqual(report.repository_full_name, "ankita-rath/BugWhisperer_Task")
        self.assertIn("bug", report.labels)

    def test_validates_short_body(self):
        payload = dict(self.payload)
        payload["issue"] = dict(self.payload["issue"])
        payload["issue"]["body"] = "too short"

        error = validation_error(IssueReport.from_webhook(payload))

        self.assertIn("too short", error)

    def test_build_prompt_includes_issue_context(self):
        prompt = build_prompt(IssueReport.from_webhook(self.payload))

        self.assertIn("Checkout fails when applying discount code", prompt)
        self.assertIn("missing_info", prompt)

    def test_parse_ai_response(self):
        result = parse_ai_response(
            json.dumps(
                {
                    "summary": "Checkout hangs after applying a discount code.",
                    "category": "backend",
                    "severity": "P2 - Checkout is impaired but no outage is proven.",
                    "first_step": "Reproduce checkout and inspect the discount API response.",
                    "missing_info": ["Affected account type"],
                }
            )
        )

        self.assertEqual(result.category, "backend")

    def test_formats_comment(self):
        comment = format_github_comment(
            TriageResult(
                summary="Checkout hangs.",
                category="backend",
                severity="P2 - Checkout is impaired.",
                first_step="Inspect the discount API response.",
                missing_info=["Affected account type"],
            )
        )

        self.assertIn("## Bug Whisperer Triage", comment)
        self.assertIn("**Severity:** P2 - Checkout is impaired.", comment)


if __name__ == "__main__":
    unittest.main()

