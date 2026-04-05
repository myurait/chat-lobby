"""
title: ChatLobby Status Panel Pipe
author: ChatLobby
version: 0.1
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

from pydantic import BaseModel, Field

from open_webui.utils.misc import get_last_user_message


HELP_TEXT = """Status panel request format:

Plain text:
```text
status
```

```json
{
  "state": "running",
  "worker": "codex",
  "limit": 10
}
```

Optional fields: `statusId`, `state`, `worker`, `limit`
"""


class Pipe:
    name = "ChatLobby Status Panel"

    class Valves(BaseModel):
        status_store_base_url: str = Field(
            default="http://host.docker.internal:8791",
            description="Status store base URL reachable from the Open WebUI container.",
        )
        api_bearer_token: str = Field(
            default=os.environ.get("CHATLOBBY_INTERNAL_API_TOKEN", ""),
            description="Bearer token used for status store requests.",
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
        stripped = self._extract_payload_text(message).strip()
        if not stripped or stripped.lower() == "status":
            return {"state": "running", "limit": 10}

        if stripped.startswith("{"):
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as error:
                raise ValueError(f"Request body must be valid JSON. {error}") from error
            if not isinstance(payload, dict):
                raise ValueError("Request body must be a JSON object.")
            return payload

        return {"state": "running", "limit": 10}

    def _request_json(self, path: str) -> tuple[int, dict]:
        request = urllib.request.Request(f"{self.valves.status_store_base_url}{path}", method="GET")
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
        last_user_message = get_last_user_message(body.get("messages", [])) or "status"

        try:
            payload = self._parse_payload(last_user_message)
        except ValueError as error:
            return f"{error}\n\n{HELP_TEXT}"

        status_id = payload.get("statusId")
        if isinstance(status_id, str) and status_id.strip():
            status, data = self._request_json(f"/tasks/{urllib.parse.quote(status_id.strip(), safe='')}")
            if status != 200:
                return f"Status lookup failed.\n\n{json.dumps(data, ensure_ascii=False)}"

            lines = [
                "ChatLobby status detail.",
                f"- status_id: {data.get('statusId')}",
                f"- worker: {data.get('worker')}",
                f"- state: {data.get('state')}",
                f"- approval: {data.get('approvalState', 'unknown')}",
                f"- step: {data.get('currentStep', '-')}",
                f"- last_action: {data.get('lastAction', '-')}",
                f"- updated_at: {data.get('updatedAt', '-')}",
            ]
            if data.get("resultSummary"):
                lines.append(f"- result: {data.get('resultSummary')}")
            if data.get("error"):
                lines.append(f"- error: {data.get('error')}")
            return "\n".join(lines)

        query = urllib.parse.urlencode(
          {
              "state": payload.get("state", "running"),
              "worker": payload.get("worker", ""),
              "limit": payload.get("limit", 10),
          }
        )
        status, data = self._request_json(f"/tasks?{query}")
        if status != 200:
            return f"Status list failed.\n\n{json.dumps(data, ensure_ascii=False)}"

        items = data.get("items", [])
        if not items:
            return "ChatLobby status panel.\n- items: 0"

        lines = ["ChatLobby status panel.", f"- items: {len(items)}", ""]
        for item in items:
            lines.append(
                f"- {item.get('statusId')} | worker={item.get('worker')} | state={item.get('state')} | "
                f"approval={item.get('approvalState', 'unknown')} | step={item.get('currentStep', '-')} | "
                f"updated={item.get('updatedAt', '-')}"
            )
        return "\n".join(lines)
