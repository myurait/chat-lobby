import json
import os
import socket
import subprocess
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT_DIR / "services" / "status-store" / "src" / "server.ts"


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class StatusStoreTests(unittest.TestCase):
    def _start_server(self, extra_env: dict[str, str] | None = None):
        port = find_free_port()
        env = os.environ.copy()
        env["STATUS_STORE_HOST"] = "127.0.0.1"
        env["STATUS_STORE_PORT"] = str(port)
        env["CHATLOBBY_INTERNAL_API_TOKEN"] = "secret-token"
        if extra_env:
            env.update(extra_env)

        process = subprocess.Popen(
            ["node", str(SERVER_PATH)],
            cwd=ROOT_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        deadline = time.time() + 10
        health_url = f"http://127.0.0.1:{port}/health"
        while time.time() < deadline:
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=1)
                self.fail(f"status store exited early\nstdout:\n{stdout}\nstderr:\n{stderr}")

            try:
                with urllib.request.urlopen(health_url) as response:
                    if response.status == 200:
                        return port, process
            except Exception:  # noqa: BLE001
                time.sleep(0.1)

        self.fail("status store did not become healthy in time")

    def _request_json(self, port: int, method: str, path: str, payload: dict | None = None, bearer_token: str | None = "secret-token"):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}{path}",
            data=body,
            method=method,
            headers=headers,
        )

        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                raw = response.read().decode("utf-8")
                return response.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            raw = error.read().decode("utf-8")
            return error.code, json.loads(raw) if raw else {}

    def _cleanup_process(self, process: subprocess.Popen[str]) -> None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        if process.stdout is not None:
            process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()

    def test_event_merge_and_filtered_listing(self):
        port, process = self._start_server()
        try:
            status, created = self._request_json(
                port,
                "POST",
                "/events",
                {
                    "taskId": "codex-task-1",
                    "worker": "codex",
                    "state": "running",
                    "title": "Codex task",
                    "approvalState": "may_require_approval",
                    "currentStep": "task started",
                    "createdAt": "2026-04-05T22:59:03+09:00",
                },
            )
            self.assertEqual(status, 202)
            self.assertEqual(created["statusId"], "codex:codex-task-1")
            self.assertEqual(created["approvalState"], "may_require_approval")

            status, updated = self._request_json(
                port,
                "POST",
                "/events",
                {
                    "taskId": "codex-task-1",
                    "worker": "codex",
                    "state": "succeeded",
                    "currentStep": "completed",
                    "resultSummary": "implemented",
                },
            )
            self.assertEqual(status, 202)
            self.assertEqual(updated["state"], "succeeded")
            self.assertEqual(updated["resultSummary"], "implemented")
            self.assertEqual(updated["approvalState"], "may_require_approval")
            self.assertEqual(updated["createdAt"], "2026-04-05T22:59:03+09:00")
            self.assertTrue(updated["completedAt"])

            status, listing = self._request_json(port, "GET", "/tasks?worker=codex&state=succeeded&limit=5")
            self.assertEqual(status, 200)
            self.assertEqual(len(listing["items"]), 1)
            self.assertEqual(listing["items"][0]["statusId"], "codex:codex-task-1")

            status, detail = self._request_json(port, "GET", "/tasks/codex:codex-task-1")
            self.assertEqual(status, 200)
            self.assertEqual(detail["currentStep"], "completed")
            self.assertEqual(detail["resultSummary"], "implemented")
        finally:
            self._cleanup_process(process)

    def test_oldest_record_is_trimmed_when_max_tasks_is_exceeded(self):
        port, process = self._start_server({"STATUS_STORE_MAX_TASKS": "1"})
        try:
            self._request_json(
                port,
                "POST",
                "/events",
                {"taskId": "task-1", "worker": "knowledge", "state": "running"},
            )
            time.sleep(0.05)
            self._request_json(
                port,
                "POST",
                "/events",
                {"taskId": "task-2", "worker": "knowledge", "state": "running"},
            )

            status, listing = self._request_json(port, "GET", "/tasks")
            self.assertEqual(status, 200)
            self.assertEqual(len(listing["items"]), 1)
            self.assertEqual(listing["items"][0]["statusId"], "knowledge:task-2")

            status, detail = self._request_json(port, "GET", "/tasks/knowledge:task-1")
            self.assertEqual(status, 404)
        finally:
            self._cleanup_process(process)

    def test_bearer_token_is_required_when_configured(self):
        port, process = self._start_server()
        try:
            status, payload = self._request_json(
                port,
                "GET",
                "/tasks",
                bearer_token=None,
            )
            self.assertEqual(status, 401)
            self.assertIn("token", payload["error"])
        finally:
            self._cleanup_process(process)


if __name__ == "__main__":
    unittest.main()
