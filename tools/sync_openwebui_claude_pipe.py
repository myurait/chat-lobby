#!/usr/bin/env python3
"""Register or update the ChatLobby Claude task pipe in Open WebUI."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from openwebui_sync import ensure_active, ensure_function, sign_in


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PIPE_FILE = ROOT_DIR / "tools" / "openwebui" / "chatlobby_claude_task_pipe.py"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Register or update the ChatLobby Claude task pipe in Open WebUI.")
    parser.add_argument("--webui-url", default=os.environ.get("WEBUI_URL", "http://localhost:3000"))
    parser.add_argument("--email", default=os.environ.get("WEBUI_ADMIN_EMAIL"))
    parser.add_argument("--password", default=os.environ.get("WEBUI_ADMIN_PASSWORD"))
    parser.add_argument("--function-id", default="chatlobby_claude_task")
    parser.add_argument("--name", default="ChatLobby Claude Task")
    parser.add_argument(
        "--description",
        default="Run a Claude Code task through the local Claude adapter and return the result to chat.",
    )
    parser.add_argument("--pipe-file", default=str(DEFAULT_PIPE_FILE))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.email or not args.password:
        parser.error("--email and --password are required unless provided via environment variables")

    content = Path(args.pipe_file).read_text(encoding="utf-8")
    token = sign_in(args.webui_url.rstrip("/"), args.email, args.password)
    ensure_function(
        args.webui_url.rstrip("/"),
        token,
        args.function_id,
        args.name,
        args.description,
        content,
    )
    ensure_active(args.webui_url.rstrip("/"), token, args.function_id)

    print(f"Synced Open WebUI function: {args.function_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
