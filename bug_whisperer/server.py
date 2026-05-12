import json
import logging
import os
import queue
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


LOGGER = logging.getLogger("bug_whisperer")
WEBHOOK_QUEUE: queue.Queue[dict[str, Any]] = queue.Queue()


def process_webhook(payload: dict[str, Any]) -> None:
    LOGGER.info("Webhook payload queued for processing: action=%s", payload.get("action"))


def worker() -> None:
    while True:
        payload = WEBHOOK_QUEUE.get()
        try:
            process_webhook(payload)
        except Exception:
            LOGGER.exception("Unexpected webhook processing error")
        finally:
            WEBHOOK_QUEUE.task_done()


class WebhookHandler(BaseHTTPRequestHandler):
    server_version = "BugWhisperer/1.0"

    def do_POST(self) -> None:
        if self.path != "/webhook":
            self.send_error(HTTPStatus.NOT_FOUND, "Use POST /webhook")
            return

        payload = self._read_json_body()
        if payload is None:
            self.send_error(HTTPStatus.BAD_REQUEST, "Request body must be valid JSON")
            return

        WEBHOOK_QUEUE.put(payload)
        self._send_json(HTTPStatus.OK, {"status": "accepted"})

    def log_message(self, format: str, *args: Any) -> None:
        LOGGER.info("%s - %s", self.address_string(), format % args)

    def _read_json_body(self) -> dict[str, Any] | None:
        content_length = int(self.headers.get("Content-Length") or "0")
        raw_body = self.rfile.read(content_length)
        try:
            parsed = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            LOGGER.warning("Received invalid JSON webhook body")
            return None

        if not isinstance(parsed, dict):
            LOGGER.warning("Received JSON webhook body that is not an object")
            return None

        return parsed

    def _send_json(self, status: HTTPStatus, body: dict[str, Any]) -> None:
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def run_server() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))

    threading.Thread(target=worker, name="webhook-worker", daemon=True).start()

    httpd = ThreadingHTTPServer((host, port), WebhookHandler)
    LOGGER.info("Bug Whisperer listening on http://%s:%s/webhook", host, port)
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()

