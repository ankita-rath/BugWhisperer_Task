# Bug Whisperer

AI-powered first-pass triage for GitHub Issue webhooks.

## Assignment Progress

| Task | Status |
| --- | --- |
| Task 1 - Understand the incoming payload | Completed |
| Task 2 - Set up webhook receiver | Completed |
| Task 3 - Extract and validate payload | Completed |
| Task 4 - Design AI prompt | Pending |
| Task 5 - Call AI API and parse response | Pending |
| Task 6 - Format GitHub comment | Pending |
| Task 7 - Post comment to GitHub | Pending |
| Task 8 - Test full flow end to end | Pending |

## Chosen Payload Fields

The service extracts the issue action, issue number, title, body, author, labels,
repository full name, repository URL, and webhook sender from the GitHub Issues
webhook payload. These fields are enough to understand the bug, validate whether
there is useful detail to triage, and post the final AI-generated comment back to
the correct GitHub Issue.

## Run Locally

```bash
python -m bug_whisperer.server
```

By default the server listens on `http://127.0.0.1:8000/webhook`. Override
`HOST`, `PORT`, and `LOG_LEVEL` with environment variables if needed.

Test the receiver with the sample payload:

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  --data @data/sample_issue_webhook.json
```

`MIN_ISSUE_BODY_LENGTH` controls the minimum issue description length. The default
is `30` characters.
