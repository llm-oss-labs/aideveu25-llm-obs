"""
Simple terminal chat client for the LLM Workshop API.

Features
- Reads user input in a loop and posts to the API.
- Session-aware: uses a persistent session_id so backend retains history.
- Keeps a local rolling window of the last N messages for display/logging.
- Handles Ctrl+C to cancel or exit gracefully.

Environment variables
- API_BASE_URL: Base URL of the API (default: http://localhost:8000/v1)
- SESSION_ID: Optional fixed session id (default: random short UUID)
- CONTEXT_WINDOW: Number of recent messages to keep locally (default: 20)
- CLI_TIMEOUT: Request timeout in seconds (default: 60)

Run
  python apps/cli/main.py
  python apps/cli/main.py --base-url http://localhost:8000/v1 --session-id my-session --window 10
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import uuid
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Tuple

import httpx


# ----------------------------
# Data structures
# ----------------------------


@dataclass
class Message:
    """Represents a single chat message.

    role: "user" or "assistant"
    content: message text
    """

    role: str
    content: str


# ----------------------------
# CLI logic
# ----------------------------


def make_logger(verbose: bool = False) -> logging.Logger:
    """Configure and return a logger with timestamps.

    Args:
        verbose: If True, sets DEBUG level; otherwise INFO.
    """
    logger = logging.getLogger("cli")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    # Avoid duplicate handlers in some environments
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


def parse_args(argv: List[str]) -> argparse.Namespace:
    """Parse CLI arguments."""
    default_base = os.getenv("API_BASE_URL", "http://localhost:8000/v1")
    default_sid = os.getenv("SESSION_ID")
    default_window = int(os.getenv("CONTEXT_WINDOW", "20"))
    default_timeout = float(os.getenv("CLI_TIMEOUT", "60"))

    parser = argparse.ArgumentParser(
        description="Terminal chat client for the LLM Workshop API",
    )
    parser.add_argument(
        "--base-url",
        default=default_base,
        help=f"API base URL (default: {default_base})",
    )
    parser.add_argument(
        "--session-id",
        default=default_sid,
        help="Session identifier to keep conversation history (default: random)",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=default_window,
        help=f"Rolling context window size to keep locally (default: {default_window})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=default_timeout,
        help=f"HTTP request timeout in seconds (default: {default_timeout})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args(argv)


def generate_session_id(seed: str | None = None) -> str:
    """Generate a short, human-friendly session id.

    If seed provided, return it unchanged. Otherwise generate 8-char UUID.
    """
    if seed:
        return seed
    return uuid.uuid4().hex[:8]


def build_client(timeout: float) -> httpx.Client:
    """Construct a synchronous HTTP client with sane defaults."""
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    return httpx.Client(timeout=timeout, limits=limits)


def post_chat(
    client: httpx.Client, base_url: str, session_id: str, user_message: str
) -> Tuple[int, str]:
    """Send a chat message to the API and return (status_code, text_payload).

    The API schema expects JSON with {"session_id", "user_message"} and returns
    {"session_id", "reply"} on success. Errors will include a JSON "detail" or text.
    """
    url = f"{base_url.rstrip('/')}/chat"
    payload = {"session_id": session_id, "user_message": user_message}
    headers = {"Content-Type": "application/json"}
    resp = client.post(url, headers=headers, json=payload)
    return resp.status_code, resp.text


def extract_reply(status_code: int, payload_text: str) -> Tuple[bool, str]:
    """Parse the server response and return (ok, message).

    On success, message is the assistant reply. On error, message is a concise error.
    """
    try:
        data = json.loads(payload_text)
    except json.JSONDecodeError:
        return False, f"Invalid response ({status_code})."

    if 200 <= status_code < 300:
        reply = data.get("reply")
        if isinstance(reply, str):
            return True, reply
        return False, "Malformed success payload: missing 'reply'."
    else:
        # FastAPI commonly returns {"detail": "..."}
        detail = data.get("detail")
        if isinstance(detail, str) and detail:
            return False, detail
        return False, f"Request failed ({status_code})."


def run_chat_loop(base_url: str, session_id: str, window: int, timeout: float, logger: logging.Logger) -> None:
    """Run the REPL loop until EOF or Ctrl+C.

    Handles Ctrl+C to cancel or exit gracefully. Maintains a local rolling history
    for display/logging only; the backend retains session history by session_id.
    """
    history: Deque[Message] = deque(maxlen=max(1, window))
    client = build_client(timeout=timeout)

    # Ctrl+C behavior: rely on KeyboardInterrupt to exit or cancel requests

    print(f"Session: {session_id}")
    print("Type your message and press Enter. Ctrl+C to cancel a request, Ctrl+D to quit.")

    while True:
        try:
            user_input = input(
                "\nYou: "
            ).strip()
        except EOFError:
            print("\nGoodbye.")
            break
        except KeyboardInterrupt:
            # Ctrl+C at prompt exits the CLI
            print("\nExiting.")
            break

        if not user_input:
            continue

        # Record user message locally
        history.append(Message("user", user_input))

        # Send request
        start = time.time()
        try:
            status, text = post_chat(client, base_url, session_id, user_input)
        except KeyboardInterrupt:
            print("\nCanceled.")
            logger.warning("Request canceled by user")
            continue
        except Exception as exc:
            print("Error: request failed.")
            logger.exception("Request error: %s", exc)
            continue

        ok, message = extract_reply(status, text)
        elapsed = (time.time() - start) * 1000
        logger.debug("Response in %.1f ms | status=%s", elapsed, status)

        if ok:
            history.append(Message("assistant", message))
            # Note: API does not stream; we print whole reply when complete
            print(f"Assistant: {message}")
        else:
            print(f"Error: {message}")
            logger.error("Request failed | status=%s | payload=%s", status, text)


def main(argv: List[str] | None = None) -> int:
    """Entry point for the CLI."""
    args = parse_args(argv or sys.argv[1:])
    logger = make_logger(args.verbose)

    session_id = generate_session_id(args.session_id)
    run_chat_loop(
        base_url=args.base_url,
        session_id=session_id,
        window=args.window,
        timeout=args.timeout,
        logger=logger,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
