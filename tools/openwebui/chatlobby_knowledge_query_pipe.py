"""
title: ChatLobby Knowledge Query Pipe
author: ChatLobby
version: 0.1
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

from pydantic import BaseModel, Field

from open_webui.utils.misc import get_last_user_message


HELP_TEXT = """Knowledge request format:

Search:
```json
{
  "query": "Open WebUI",
  "repoPath": "/workspace/templates/chatlobby-canonical"
}
```

Read:
```json
{
  "path": "/Users/you/.../workspace/templates/chatlobby-canonical/README.ja.md"
}
```
"""


class Pipe:
    name = "ChatLobby Knowledge Query"

    class Valves(BaseModel):
        adapter_base_url: str = Field(
            default="http://host.docker.internal:8789",
            description="Knowledge adapter base URL reachable from the Open WebUI container.",
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
        try:
            payload = json.loads(self._extract_payload_text(message))
        except json.JSONDecodeError as error:
            raise ValueError(f"Request body must be valid JSON. {error}") from error

        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")

        return payload

    def _request_json(self, path: str, method: str, payload: Optional[dict] = None) -> tuple[int, dict]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(f"{self.valves.adapter_base_url}{path}", data=body, method=method)
        request.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(request) as response:
                raw = response.read().decode("utf-8")
                return response.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            raw = error.read().decode("utf-8")
            data = json.loads(raw) if raw else {}
            return error.code, data

    def pipe(self, body: dict, __user__: Optional[dict] = None) -> str:
        last_user_message = get_last_user_message(body.get("messages", []))
        if not last_user_message:
            return HELP_TEXT

        try:
            payload = self._parse_payload(last_user_message)
        except ValueError as error:
            return f"{error}\n\n{HELP_TEXT}"

        if "path" in payload:
            status, data = self._request_json("/read", "POST", payload)
            if status != 200:
                return f"Knowledge read failed.\n\n{json.dumps(data, ensure_ascii=False)}"

            return (
                "Knowledge read succeeded.\n"
                f"- path: {data.get('path')}\n\n"
                f"{data.get('content', '')}"
            )

        if "query" in payload:
            status, data = self._request_json("/search", "POST", payload)
            if status != 200:
                return f"Knowledge search failed.\n\n{json.dumps(data, ensure_ascii=False)}"

            items = data.get("items", [])
            if not items:
                return "Knowledge search succeeded.\n- matches: 0"

            lines = ["Knowledge search succeeded.", f"- matches: {len(items)}", ""]
            for item in items:
                lines.append(f"{item.get('relativePath')}:{item.get('line')}: {item.get('content')}")

            return "\n".join(lines)

        return "Missing `query` or `path`.\n\n" + HELP_TEXT
