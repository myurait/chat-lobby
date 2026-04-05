"""
title: ChatLobby Dispatch Task Pipe
author: ChatLobby
version: 0.1
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Optional

from pydantic import BaseModel, Field

from open_webui.utils.misc import get_last_user_message


HELP_TEXT = """Dispatch request format:

Plain text:

```text
実装して
```

```json
{
  "prompt": "Search ChatLobby docs for Open WebUI"
}
```

Optional fields: `query`, `path`, `repoPath`, `workingDirectory`, `workerHint`
"""


class Pipe:
    name = "ChatLobby Dispatch Task"

    class Valves(BaseModel):
        dispatcher_base_url: str = Field(
            default="http://host.docker.internal:8790",
            description="Dispatcher base URL reachable from the Open WebUI container.",
        )
        api_bearer_token: str = Field(
            default=os.environ.get("CHATLOBBY_INTERNAL_API_TOKEN", ""),
            description="Bearer token used for dispatcher requests.",
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
        stripped = payload_text.strip()
        if not stripped:
            raise ValueError("Request body must not be empty.")

        if stripped.startswith("{"):
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as error:
                raise ValueError(f"Request body must be valid JSON. {error}") from error

            if not isinstance(payload, dict):
                raise ValueError("Request body must be a JSON object.")

            return payload

        return {"prompt": stripped}

    def _request_json(self, path: str, method: str, payload: Optional[dict] = None) -> tuple[int, dict]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(f"{self.valves.dispatcher_base_url}{path}", data=body, method=method)
        request.add_header("Content-Type", "application/json")
        if self.valves.api_bearer_token:
            request.add_header("Authorization", f"Bearer {self.valves.api_bearer_token}")

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

        status, data = self._request_json("/dispatch", "POST", payload)
        if status != 200:
            return f"Dispatch failed.\n\n{json.dumps(data, ensure_ascii=False)}"

        worker = data.get("worker")
        reason = data.get("reason")
        result = data.get("result", {})

        if worker == "knowledge":
            if "items" in result:
                items = result.get("items", [])
                if not items:
                    return f"Dispatch selected knowledge.\n- reason: {reason}\n- matches: 0"
                lines = [f"Dispatch selected knowledge.", f"- reason: {reason}", f"- matches: {len(items)}", ""]
                for item in items:
                    lines.append(f"{item.get('relativePath')}:{item.get('line')}: {item.get('content')}")
                return "\n".join(lines)

            return (
                f"Dispatch selected knowledge.\n"
                f"- reason: {reason}\n\n"
                f"{result.get('content', '')}"
            )

        task_result = result.get("result", {}) if isinstance(result, dict) else {}
        if worker == "claude":
            message = None
            if isinstance(task_result, dict):
                message = task_result.get("result") or task_result.get("raw") or task_result.get("message")
            if message is None and isinstance(result, dict):
                message = result.get("stdout") or result.get("error")
            if message is None:
                message = json.dumps(result, ensure_ascii=False)
            return (
                f"Dispatch selected claude.\n"
                f"- reason: {reason}\n"
                f"- result: {message}"
            )

        if worker == "codex":
            message = None
            if isinstance(task_result, dict):
                message = task_result.get("message") or task_result.get("raw")
            if message is None and isinstance(result, dict):
                message = result.get("stdout") or result.get("error")
            if message is None:
                message = json.dumps(result, ensure_ascii=False)
            return (
                f"Dispatch selected codex.\n"
                f"- reason: {reason}\n"
                f"- result: {message}"
            )

        return json.dumps(data, ensure_ascii=False)
