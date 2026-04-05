"""
title: ChatLobby Publish Pipe
author: ChatLobby
version: 0.1
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Optional

from pydantic import BaseModel, Field

from open_webui.utils.misc import get_last_user_message


HELP_TEXT = """Publish request format:

```json
{
  "kind": "spec",
  "title": "Example feature spec",
  "body": "Summarize the feature here.",
  "slug": "example-feature-spec",
  "date": "2026-04-05",
  "repo": "/workspace/templates/chatlobby-canonical",
  "overwrite": false
}
```

Required fields: `kind`, `title`, `body`
Allowed kinds: `spec`, `adr`, `worklog`
"""


class Pipe:
    name = "ChatLobby Publish"

    class Valves(BaseModel):
        canonical_repo: str = Field(
            default="/workspace/templates/chatlobby-canonical",
            description="Default canonical Git repository path inside the Open WebUI container.",
        )
        publish_tool_path: str = Field(
            default="/workspace/chatlobby/tools/publish_to_repo.py",
            description="Absolute path to the ChatLobby publish CLI inside the Open WebUI container.",
        )
        default_author: str = Field(
            default="ChatLobby",
            description="Fallback author label inserted into the generated document.",
        )

    def __init__(self) -> None:
        self.type = "pipe"
        self.valves = self.Valves()

    def _extract_payload_text(self, message: str) -> str:
        stripped = message.strip()
        if "```json" in stripped:
            start = stripped.find("```json") + len("```json")
            end = stripped.find("```", start)
            if end != -1:
                return stripped[start:end].strip()
        if "```" in stripped:
            start = stripped.find("```") + len("```")
            end = stripped.find("```", start)
            if end != -1:
                return stripped[start:end].strip()
        return stripped

    def _parse_payload(self, message: str) -> dict:
        payload_text = self._extract_payload_text(message)
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as error:
            raise ValueError(f"Request body must be valid JSON. {error}") from error

        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")

        return payload

    def pipe(self, body: dict, __user__: Optional[dict] = None) -> str:
        last_user_message = get_last_user_message(body.get("messages", []))
        if not last_user_message:
            return HELP_TEXT

        try:
            payload = self._parse_payload(last_user_message)
        except ValueError as error:
            return f"{error}\n\n{HELP_TEXT}"

        kind = payload.get("kind")
        title = payload.get("title")
        content = payload.get("body") or payload.get("content")

        if kind not in {"spec", "adr", "worklog"}:
            return "Invalid or missing `kind`.\n\n" + HELP_TEXT
        if not isinstance(title, str) or not title.strip():
            return "Missing `title`.\n\n" + HELP_TEXT
        if not isinstance(content, str) or not content.strip():
            return "Missing `body`.\n\n" + HELP_TEXT

        repo = payload.get("repo") or self.valves.canonical_repo
        author = payload.get("author")
        if not author:
            author = ((__user__ or {}).get("name") or self.valves.default_author).strip()

        command = [
            sys.executable,
            self.valves.publish_tool_path,
            "--repo",
            repo,
            "--kind",
            kind,
            "--title",
            title.strip(),
            "--body",
            content.strip(),
            "--author",
            author,
        ]

        if payload.get("slug"):
            command.extend(["--slug", str(payload["slug"]).strip()])
        if payload.get("date"):
            command.extend(["--date", str(payload["date"]).strip()])
        if payload.get("overwrite"):
            command.append("--overwrite")

        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            error_text = (result.stderr or result.stdout).strip()
            return f"Publish failed.\n\n{error_text}"

        target_path = result.stdout.strip()
        return (
            "Published successfully.\n"
            f"- kind: {kind}\n"
            f"- title: {title.strip()}\n"
            f"- path: {target_path}"
        )
