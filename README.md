#  Bug Whisperer

An AI-powered triage assistant that automatically analyzes GitHub issues and provides instant AI-generated feedback through comments.

**What it does:** When someone opens an issue, Bug Whisperer listens via webhook, analyzes the issue with AI, and posts a helpful triage comment back on GitHub—all automatically.

---

##  Features

- **Automatic Issue Analysis** – Uses Google Gemini API to understand bug reports
- **Smart Triage Comments** – Posts formatted, actionable feedback directly on GitHub issues
- **Webhook-Ready** – Integrates seamlessly with GitHub webhook events
- **Lightweight** – Built with only Python standard library (Python 3.9+)
- **Flexible Configuration** – Easily customize via environment variables
- **Mock Mode for Testing** – Test locally without spending API credits

---

##  What Gets Extracted

The webhook listener extracts these key fields from each GitHub issue:
- Issue action and number
- Title and description
- Author and labels
- Repository info and webhook sender

These fields are all you need to understand the bug and generate meaningful triage feedback.

---

##  Project Structure

```
bug_whisperer/
├── ai_client.py          # Handles Gemini API calls & JSON parsing
├── comment_formatter.py  # Formats the response as GitHub markdown
├── github_client.py      # Posts comments back to GitHub
├── models.py             # Data models for payloads and responses
├── payload.py            # Extracts & validates webhook data
├── prompt.py             # AI prompt template management
└── server.py             # HTTP webhook receiver

data/
└── sample_issue_webhook.json    # Example webhook payload

prompts/
└── bug_triage_prompt.txt        # AI system prompt

tests/
└── test_core.py                 # Unit tests
```

---

##  Quick Start

### Prerequisites
- Python 3.9 or newer
- A Google Gemini API key (free tier available)
- A GitHub Personal Access Token (for posting comments)

### Run Locally

```bash
# Start the webhook server
python -m bug_whisperer.server
```

The server listens on `http://127.0.0.1:8000/webhook` by default.

### Test with Sample Data

In another terminal:

```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  --data @data/sample_issue_webhook.json
```

### Run Tests

```bash
python -m unittest
```

---

##  Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes* | Your Google Gemini API key |
| `GEMINI_MODEL` | No | Model to use (default: `gemini-2.5-flash-lite`) |
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token |
| `AI_PROVIDER` | No | Set to `mock` for testing without API calls |
| `MOCK_AI_RESPONSE` | No | JSON string to return when using mock AI |
| `GITHUB_DRY_RUN` | No | Set to `true` to skip actually posting to GitHub |
| `GITHUB_API_URL` | No | Override GitHub API base URL (default: `https://api.github.com`) |
| `HOST` | No | Server host (default: `127.0.0.1`) |
| `PORT` | No | Server port (default: `8000`) |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |
| `MIN_ISSUE_BODY_LENGTH` | No | Minimum issue description length (default: `30` chars) |

*Not required when `AI_PROVIDER=mock`

### Local Testing (No API Costs)

Test everything locally without spending Gemini API credits:

```bash
AI_PROVIDER=mock GITHUB_DRY_RUN=true python -m bug_whisperer.server
```

---

##  Using with Real GitHub Webhooks

Want to set up actual GitHub integration? Here's how:

### 1. **Start the Server**

```bash
python -m bug_whisperer.server
```

### 2. **Expose Your Local Server (using ngrok)**

```bash
ngrok http 8000
```

This gives you a public URL like `https://example.ngrok-free.app`

### 3. **Add GitHub Webhook**

In your test GitHub repo:

1. Go to **Settings > Webhooks > Add webhook**
2. Fill in these settings:
   - **Payload URL:** `https://your-ngrok-url/webhook`
   - **Content type:** `application/json`
   - **Events:** Select "Issues"
   - **Active:**  Checked

3. Click **Add webhook**

### 4. **Test It Out**

Create a new issue with a good title and description. You should see:
- Server logs showing webhook received
- Payload validated
- AI response generated
- Comment posted to GitHub 

---

##  AI & API Details

### Google Gemini Integration

This project uses the **Google Gemini Developer API** (free tier):
- No authentication needed beyond the API key
- Supports structured JSON responses
- Perfect for triage automation

To get started:
1. Visit [Google AI Studio](https://aistudio.google.com)
2. Create an API key
3. Set it as `GEMINI_API_KEY` environment variable

### Customizing the Prompt

The AI behavior is controlled by `prompts/bug_triage_prompt.txt`. Edit it to change how issues are analyzed.

---

## 📊 Task Completion Status

| Task | Status |
|------|--------|
| Understand GitHub webhook payload | Completed |
| Build webhook receiver |  Completed |
| Extract and validate payload |  Completed |
| Design AI prompt for triage |  Completed |
| Call Gemini API and parse response |  Completed |
| Format GitHub comment in markdown |  Completed |
| Post comment back to GitHub |  Completed |
| End-to-end testing |  Completed |

---

##  Tips & Tricks

- **Dry Run Mode:** Use `GITHUB_DRY_RUN=true` to test without posting to GitHub
- **Mock AI:** Use `AI_PROVIDER=mock` to test without Gemini API calls
- **Adjust Minimum Length:** Increase `MIN_ISSUE_BODY_LENGTH` to only triage detailed issues
- **Check Logs:** Set `LOG_LEVEL=DEBUG` for detailed logging during development

---

## License

This project is part of the BugWhisperer assignment.

---

**Questions or issues?** Check the test file (`tests/test_core.py`) for usage examples.
