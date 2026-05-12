# Bug Whisperer

AI-powered first-pass triage for GitHub Issue webhooks.

## Assignment Progress

| Task | Status |
| --- | --- |
| Task 1 - Understand the incoming payload | Completed |
| Task 2 - Set up webhook receiver | Pending |
| Task 3 - Extract and validate payload | Pending |
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

