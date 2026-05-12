from pathlib import Path

from bug_whisperer.models import IssueReport


PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "bug_triage_prompt.txt"
START_MARKER = "--- PROMPT TEMPLATE START ---"
END_MARKER = "--- PROMPT TEMPLATE END ---"


def load_prompt_template(path: Path = PROMPT_PATH) -> str:
    content = path.read_text(encoding="utf-8")
    start = content.index(START_MARKER) + len(START_MARKER)
    end = content.index(END_MARKER)
    return content[start:end].strip()


def build_prompt(report: IssueReport) -> str:
    template = load_prompt_template()
    labels = ", ".join(report.labels) if report.labels else "none"

    return template.format(
        title=report.title.strip(),
        body=report.body.strip(),
        author=report.author,
        labels=labels,
        repository=report.repository_full_name,
        issue_number=report.issue_number,
    )

