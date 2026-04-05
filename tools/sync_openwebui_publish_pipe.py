#!/usr/bin/env python3
"""Register or update the ChatLobby publish pipe in Open WebUI."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PIPE_FILE = ROOT_DIR / "tools" / "openwebui" / "chatlobby_publish_pipe.py"


def request_json(url: str, method: str, payload: dict | None = None, token: str | None = None) -> tuple[int, dict]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8")
        data = json.loads(raw) if raw else {}
        return error.code, data


def sign_in(base_url: str, email: str, password: str) -> str:
    status, data = request_json(
        f"{base_url}/api/v1/auths/signin",
        "POST",
        {"email": email, "password": password},
    )
    if status != 200 or "token" not in data:
        raise RuntimeError(f"Failed to sign in to Open WebUI: {data}")
    return data["token"]


def ensure_pipe(
    base_url: str,
    token: str,
    function_id: str,
    name: str,
    description: str,
    content: str,
) -> dict:
    form = {
        "id": function_id,
        "name": name,
        "meta": {"description": description},
        "content": content,
    }

    status, data = request_json(f"{base_url}/api/v1/functions/id/{function_id}", "GET", token=token)
    if status == 200:
        status, data = request_json(
            f"{base_url}/api/v1/functions/id/{function_id}/update",
            "POST",
            form,
            token=token,
        )
        if status != 200:
            raise RuntimeError(f"Failed to update function: {data}")
        return data

    not_found = isinstance(data, dict) and data.get("detail") == "We could not find what you're looking for :/"
    if status not in {401, 404} or not not_found:
        raise RuntimeError(f"Failed to inspect existing function: {data}")

    status, data = request_json(f"{base_url}/api/v1/functions/create", "POST", form, token=token)
    if status != 200:
        raise RuntimeError(f"Failed to create function: {data}")
    return data


def ensure_active(base_url: str, token: str, function_id: str) -> None:
    status, data = request_json(f"{base_url}/api/v1/functions/id/{function_id}", "GET", token=token)
    if status != 200:
        raise RuntimeError(f"Failed to read function after sync: {data}")

    if not data.get("is_active", False):
        status, data = request_json(
            f"{base_url}/api/v1/functions/id/{function_id}/toggle",
            "POST",
            {},
            token=token,
        )
        if status != 200:
            raise RuntimeError(f"Failed to activate function: {data}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Register or update the ChatLobby publish pipe in Open WebUI.")
    parser.add_argument("--webui-url", default=os.environ.get("WEBUI_URL", "http://localhost:3000"))
    parser.add_argument("--email", default=os.environ.get("WEBUI_ADMIN_EMAIL"))
    parser.add_argument("--password", default=os.environ.get("WEBUI_ADMIN_PASSWORD"))
    parser.add_argument("--function-id", default="chatlobby_publish")
    parser.add_argument("--name", default="ChatLobby Publish")
    parser.add_argument(
        "--description",
        default="Publish a spec, ADR, or worklog Markdown document into the canonical Git repository.",
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
    ensure_pipe(
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
