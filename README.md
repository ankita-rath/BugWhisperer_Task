# Bug Whisperer

AI-powered first-pass triage for GitHub Issue webhooks.

## Assignment Progress

| Task | Status |
| --- | --- |
| Task 1 - Understand the incoming payload | Completed |
| Task 2 - Set up webhook receiver | Completed |
| Task 3 - Extract and validate payload | Completed |
| Task 4 - Design AI prompt | Completed |
| Task 5 - Call AI API and parse response | Completed |
| Task 6 - Format GitHub comment | Completed |
| Task 7 - Post comment to GitHub | Completed |
| Task 8 - Test full flow end to end | Completed |

## Chosen Payload Fields

The service extracts the issue action, issue number, title, body, author, labels,
repository full name, repository URL, and webhook sender from the GitHub Issues
webhook payload. These fields are enough to understand the bug, validate whether
there is useful detail to triage, and post the final AI-generated comment back to
the correct GitHub Issue.

## Project Structure

```text
bug_whisperer/
  ai_client.py          # Gemini REST call and strict JSON parsing
  comment_formatter.py  # Markdown comment formatting
  github_client.py      # GitHub issue comment REST call
  models.py             # Payload and triage dataclasses
  payload.py            # Extraction and validation
  prompt.py             # Prompt template loader/builder
  server.py             # POST /webhook HTTP server
data/
  sample_issue_webhook.json
prompts/
  bug_triage_prompt.txt
tests/
  test_core.py
```

## Run Locally

Use Python 3.9 or newer. The project uses only the Python standard library.

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

Run the automated checks:

```bash
python -m unittest
```

## Environment Variables

| Name | Required | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | Yes, unless `AI_PROVIDER=mock` | Google Gemini API key used for the free AI REST call. |
| `GEMINI_MODEL` | No | Gemini model name. Defaults to `gemini-2.5-flash-lite`. |
| `AI_PROVIDER` | No | Set to `mock` for local testing without calling an AI API. |
| `MOCK_AI_RESPONSE` | No | JSON string returned when `AI_PROVIDER=mock`. |
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token used to post the issue comment. |
| `GITHUB_DRY_RUN` | No | Set to `true` to skip the actual GitHub comment API call. |
| `GITHUB_API_URL` | No | Override the GitHub API base URL. Defaults to `https://api.github.com`. |
| `MIN_ISSUE_BODY_LENGTH` | No | Minimum useful issue description length. Defaults to `30`. |

## Free AI Service

This implementation uses the Google Gemini Developer API over REST. It supports a
free tier for small projects and can return structured JSON with
`responseMimeType=application/json`. Create an API key in Google AI Studio and set
it as `GEMINI_API_KEY`.

For local testing without spending API calls:

```bash
AI_PROVIDER=mock GITHUB_DRY_RUN=true python -m bug_whisperer.server
```

## GitHub Webhook Setup

1. Start the server locally:

```bash
python -m bug_whisperer.server
```

2. Start ngrok in another terminal:

```bash
ngrok http 8000
```

3. Copy the HTTPS forwarding URL from ngrok and add `/webhook`.
   Example: `https://example.ngrok-free.app/webhook`.

4. In the test GitHub repository, open **Settings > Webhooks > Add webhook**.

5. Use these webhook settings:

```text
Payload URL: https://your-ngrok-url/webhook
Content type: application/json
Events: Let me select individual events > Issues
Active: checked
```

6. Create a new issue with a useful title and description. The server should log:
   webhook received, payload validated, AI response parsed, and GitHub comment
   posted.

## Screen Recording Checklist

Record one continuous flow showing:

1. The server running locally.
2. ngrok running with the public HTTPS URL.
3. The GitHub webhook configured with the ngrok `/webhook` URL.
4. A new GitHub Issue being created.
5. The terminal logs showing the webhook received and processed.
6. The AI-generated markdown comment appearing on the GitHub Issue.
