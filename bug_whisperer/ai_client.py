from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from bug_whisperer.models import TriageResult


LOGGER = logging.getLogger("bug_whisperer.ai")
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
REQUIRED_KEYS = {"summary", "category", "severity", "first_step", "missing_info"}
ALLOWED_CATEGORIES = {"UI", "backend", "authentication", "database", "infrastructure", "unknown"}


class AIClientError(Exception):
    pass


def call_ai(prompt: str) -> str:
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    if provider == "mock":
        return os.getenv(
            "MOCK_AI_RESPONSE",
            json.dumps(
                {
                    "summary": "Checkout hangs after applying a discount code.",
                    "category": "backend",
                    "severity": "P2 - Checkout is impaired but no outage is proven.",
                    "first_step": "Reproduce checkout with SAVE20 and inspect the discount API response.",
                    "missing_info": ["Affected account type", "Recent deployment details"],
                }
            ),
        )

    return call_gemini(prompt)


def call_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AIClientError("GEMINI_API_KEY is not set")

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    encoded_model = urllib.parse.quote(model, safe="")
    url = GEMINI_ENDPOINT.format(model=encoded_model)
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseJsonSchema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": sorted(ALLOWED_CATEGORIES),
                    },
                    "severity": {"type": "string"},
                    "first_step": {"type": "string"},
                    "missing_info": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": sorted(REQUIRED_KEYS),
                "additionalProperties": False,
            },
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        LOGGER.error("AI API failed with status %s: %s", exc.code, error_body)
        raise AIClientError(f"AI API failed with status {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        LOGGER.error("AI API call failed: %s", exc)
        raise AIClientError("AI API call failed") from exc

    try:
        return payload["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        LOGGER.error("AI API response did not contain model text: %s", payload)
        raise AIClientError("AI API response missing text") from exc


def parse_ai_response(raw_response: str) -> TriageResult:
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        LOGGER.error("AI response was not valid JSON: %s; raw=%s", exc, raw_response)
        raise AIClientError("AI response was not valid JSON") from exc

    if not isinstance(parsed, dict):
        LOGGER.error("AI response JSON was not an object: %s", raw_response)
        raise AIClientError("AI response JSON was not an object")

    keys = set(parsed)
    if keys != REQUIRED_KEYS:
        LOGGER.error("AI response keys were invalid: expected=%s actual=%s raw=%s", REQUIRED_KEYS, keys, raw_response)
        raise AIClientError("AI response keys were invalid")

    return triage_result_from_dict(parsed)


def triage_result_from_dict(parsed: dict[str, Any]) -> TriageResult:
    missing_info = parsed["missing_info"]
    if not isinstance(missing_info, list) or not all(isinstance(item, str) for item in missing_info):
        raise AIClientError("AI response missing_info must be an array of strings")

    category = str(parsed["category"])
    if category not in ALLOWED_CATEGORIES:
        raise AIClientError(f"AI response category is not allowed: {category}")

    return TriageResult(
        summary=str(parsed["summary"]),
        category=category,
        severity=str(parsed["severity"]),
        first_step=str(parsed["first_step"]),
        missing_info=missing_info,
    )

