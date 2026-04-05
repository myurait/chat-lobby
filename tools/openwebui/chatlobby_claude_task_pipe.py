"""
title: ChatLobby Claude Task Pipe
author: ChatLobby
version: 0.1
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Optional

from pydantic import BaseModel, Field

from open_webui.utils.misc import get_last_user_message


HELP_TEXT = """Claude task request format:

```json
{
  "prompt": "Reply with exactly ok.",
  "workingDirectory": "/workspace",
  "permissionMode": "acceptEdits",
  "model": "sonnet"
}
```

Required field: `prompt`
Optional fields: `workingDirectory`, `permissionMode`, `model`, `appendSystemPrompt`, `allowedTools`
"""


class Pipe:
    name = "ChatLobby Claude Task"

    class Valves(BaseModel):
        adapter_base_url: str = Field(
            default="http://host.docker.internal:8787",
            description="Claude adapter base URL reachable from the Open WebUI container.",
        )
        poll_interval_seconds: float = Field(default=1.0, description="Polling interval while waiting for task completion.")
        poll_timeout_seconds: int = Field(default=180, description="Maximum seconds to wait for a Claude task.")

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

        prompt = payload.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return "Missing `prompt`.\n\n" + HELP_TEXT

        task_request = {"prompt": prompt.strip()}

        for key in ("workingDirectory", "permissionMode", "model", "appendSystemPrompt", "allowedTools"):
            if key in payload:
                task_request[key] = payload[key]

        status, created = self._request_json("/tasks", "POST", task_request)
        if status not in {200, 202}:
            return f"Claude task creation failed.\n\n{json.dumps(created, ensure_ascii=False)}"

        task_id = created.get("id")
        if not task_id:
            return f"Claude adapter returned no task id.\n\n{json.dumps(created, ensure_ascii=False)}"

        deadline = time.time() + self.valves.poll_timeout_seconds
        while time.time() < deadline:
            status, task = self._request_json(f"/tasks/{task_id}", "GET")
            if status != 200:
                return f"Claude task polling failed.\n\n{json.dumps(task, ensure_ascii=False)}"

            state = task.get("state")
            if state == "succeeded":
                result = task.get("result")
                if isinstance(result, dict) and "result" in result:
                    rendered = result["result"]
                else:
                    rendered = json.dumps(result, ensure_ascii=False) if result is not None else task.get("stdout", "")

                return (
                    "Claude task succeeded.\n"
                    f"- task_id: {task_id}\n"
                    f"- result: {rendered}"
                )

            if state == "failed":
                return (
                    "Claude task failed.\n"
                    f"- task_id: {task_id}\n"
                    f"- error: {task.get('error', 'Unknown error')}"
                )

            time.sleep(self.valves.poll_interval_seconds)

        return (
            "Claude task is still running.\n"
            f"- task_id: {task_id}\n"
            f"- status_url: {self.valves.adapter_base_url}/tasks/{task_id}"
        )
